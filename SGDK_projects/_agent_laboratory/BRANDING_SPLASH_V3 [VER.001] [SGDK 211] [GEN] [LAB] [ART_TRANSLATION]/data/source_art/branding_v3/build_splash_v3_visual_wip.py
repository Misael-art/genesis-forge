#!/usr/bin/env python3
"""Build deterministic, source-derived Splash V3 WIP assets.

This builder does not draw shapes. It crops/pads, snaps source colors to the
declared Mega Drive palette, and reuses source-authored 8x8 background tiles.
Outputs are development placeholders, not final art.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = PROJECT_ROOT.parents[2]
PNG_NORMALIZER = WORKSPACE_ROOT / "tools" / "image-tools" / "normalize_indexed_sgdk_png.py"
SOURCE_ROOT = PROJECT_ROOT / "data" / "source_art" / "branding_v3" / "sources"
RES_ROOT = PROJECT_ROOT / "res"
RUN_STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
REPORT_PATH = PROJECT_ROOT / "out" / "logs" / f"splash_v3_visual_translation_report_{RUN_STAMP}.json"
BOARD_PATH = PROJECT_ROOT / "rascunho" / "visual_lab" / f"splash_v3_native_pixel_candidate_wip_{RUN_STAMP}.png"
ELITE_CONTROL_PATH = PROJECT_ROOT / "rascunho" / "visual_lab" / f"splash_backdrop_v3_40tile_control_{RUN_STAMP}.png"

SOURCES = {
    "backdrop": (
        "source_backdrop_concept_ai_v004_20261014.png",
        "dcf271e7c4c21e7d3a2aee275d32fe24a3196ddbc4954ba9309ce659fdcb2efa",
    ),
    "lettering": (
        "source_lettering_plate_ai_v002.png",
        "701f28c87caf80171d2328c433a10dc176d27c60cab8011add0935345b2086c3",
    ),
    "particles": (
        "source_particle_strip_concept_ai_v001.png",
        "f27219421ce39a62979d46e09a3291e61f2234d80f07a0040052de5f2e325f7c",
    ),
}

# ResComp requires its magenta key for transparent mark/sprite pixels. The
# full-screen backdrop is the one exception: it stores valid VDP black at 0.
TRANSPARENT = (255, 0, 255)
VDP_BACKDROP_BLACK = (0, 0, 0)
BG_PALETTE = [
    VDP_BACKDROP_BLACK,
    (0, 0, 34), (0, 0, 68), (0, 0, 102), (0, 0, 136), (0, 0, 170),
    (0, 34, 204), (0, 68, 204), (0, 102, 204), (0, 136, 238), (0, 170, 238),
    (34, 170, 238), (34, 204, 238), (102, 204, 238), (170, 204, 238), (238, 238, 238),
]
MARK_PALETTE = [
    TRANSPARENT,
    (0, 0, 68), (0, 0, 102), (0, 0, 170), (0, 34, 204), (0, 68, 204),
    (0, 102, 238), (34, 136, 238), (34, 170, 238), (34, 204, 238),
    (102, 204, 238), (170, 204, 238), (204, 238, 238), (238, 238, 238),
    (0, 68, 136), (0, 102, 170),
]
FX_PALETTE = [
    TRANSPARENT,
    (0, 0, 68), (0, 0, 102), (0, 0, 170), (0, 34, 204), (0, 68, 204),
    (0, 102, 238), (0, 136, 238), (34, 170, 238), (34, 204, 238),
    (102, 204, 238), (170, 204, 238), (204, 238, 238), (238, 238, 238),
    (102, 170, 238), (204, 238, 238),
]

EXPECTED_LOGO_BOXES = {
    "sgdk": ((48, 76, 272, 116), (224, 48)),
    "forge": ((64, 131, 256, 156), (192, 32)),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def palette_bytes(colors: list[tuple[int, int, int]]) -> list[int]:
    values: list[int] = []
    for color in colors:
        values.extend(color)
    return values + [0] * (768 - len(values))


def nearest_visible_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> int:
    return min(
        range(1, 16),
        key=lambda index: sum((rgb[channel] - palette[index][channel]) ** 2 for channel in range(3)),
    )


def make_indexed(size: tuple[int, int], pixels: list[int], palette: list[tuple[int, int, int]]) -> Image.Image:
    image = Image.new("P", size)
    image.putdata(pixels)
    image.putpalette(palette_bytes(palette))
    image.info["transparency"] = 0
    return image


def source_backdrop(path: Path) -> Image.Image:
    with Image.open(path) as source:
        fitted = ImageOps.fit(source.convert("RGB"), (320, 224), method=Image.Resampling.NEAREST, centering=(0.5, 0.5))
    indexed: list[int] = []
    for red, green, blue in fitted.getdata():
        if max(red, green, blue) <= 22:
            indexed.append(0)
        else:
            indexed.append(nearest_visible_index((red, green, blue), BG_PALETTE))
    return make_indexed((320, 224), indexed, BG_PALETTE)


def tile_bytes(image: Image.Image, tile_x: int, tile_y: int) -> bytes:
    return bytes(
        image.getpixel((tile_x * 8 + x, tile_y * 8 + y))
        for y in range(8)
        for x in range(8)
    )


def tile_distance(left: bytes, right: bytes, color_distance: list[list[int]]) -> int:
    return sum(color_distance[a][b] for a, b in zip(left, right))


def reuse_authored_tiles(image: Image.Image, limit: int = 40) -> tuple[Image.Image, int, list[int]]:
    columns = image.width // 8
    rows = image.height // 8
    tiles = [tile_bytes(image, x, y) for y in range(rows) for x in range(columns)]
    unique_tiles = list(dict.fromkeys(tiles))

    color_distance = [
        [sum((BG_PALETTE[i][c] - BG_PALETTE[j][c]) ** 2 for c in range(3)) for j in range(16)]
        for i in range(16)
    ]
    # Seed from the darkest source-authored tile, then choose the most visually
    # distinct remaining source tiles. Every output cluster is copied from this set.
    seed = max(range(len(unique_tiles)), key=lambda i: (unique_tiles[i].count(0), -i))
    selected = [seed]
    nearest = [tile_distance(tile, unique_tiles[seed], color_distance) for tile in unique_tiles]
    while len(selected) < min(limit, len(unique_tiles)):
        candidate = max(range(len(unique_tiles)), key=lambda i: (nearest[i], -i))
        if candidate in selected or nearest[candidate] == 0:
            break
        selected.append(candidate)
        prototype = unique_tiles[candidate]
        for i, tile in enumerate(unique_tiles):
            distance = tile_distance(tile, prototype, color_distance)
            if distance < nearest[i]:
                nearest[i] = distance

    prototypes = [unique_tiles[index] for index in selected]
    remapped = [
        min(prototypes, key=lambda prototype: tile_distance(tile, prototype, color_distance))
        for tile in tiles
    ]
    pixels = [0] * (image.width * image.height)
    out_index = 0
    for tile_y in range(rows):
        for local_y in range(8):
            row_start = (tile_y * 8 + local_y) * image.width
            for tile_x in range(columns):
                source_tile = remapped[tile_y * columns + tile_x]
                start = row_start + tile_x * 8
                pixels[start : start + 8] = source_tile[local_y * 8 : local_y * 8 + 8]
                out_index += 8

    result = make_indexed(image.size, pixels, BG_PALETTE)
    used_tiles = len({tile_bytes(result, x, y) for y in range(rows) for x in range(columns)})
    return result, used_tiles, selected


def make_wordmark(source: Image.Image, crop_box: tuple[int, int, int, int], size: tuple[int, int]) -> Image.Image:
    crop = source.crop(crop_box).convert("RGB")
    target_w, target_h = size
    if crop.width > target_w or crop.height > target_h:
        raise ValueError(f"Wordmark crop {crop.size} exceeds target {size}; do not downscale silently")
    indexed = [0] * (target_w * target_h)
    offset_x = (target_w - crop.width) // 2
    offset_y = (target_h - crop.height) // 2
    for y in range(crop.height):
        for x in range(crop.width):
            rgb = crop.getpixel((x, y))
            if max(rgb) <= 24:
                continue
            indexed[(offset_y + y) * target_w + offset_x + x] = nearest_visible_index(rgb, MARK_PALETTE)
    return make_indexed(size, indexed, MARK_PALETTE)


def make_particle_strip(path: Path) -> tuple[Image.Image, list[dict[str, int]]]:
    with Image.open(path) as source:
        rgba = source.convert("RGBA")
    frames: list[Image.Image] = []
    frame_report: list[dict[str, int]] = []
    for frame in range(8):
        x0 = (frame * rgba.width) // 8
        x1 = ((frame + 1) * rgba.width) // 8
        cell = rgba.crop((x0, 0, x1, rgba.height))
        alpha = cell.getchannel("A")
        mask_pixels = [255 if a >= 128 and max(cell.getpixel((x, y))[:3]) > 20 else 0
                       for y in range(cell.height) for x, a in enumerate(alpha.crop((0, y, cell.width, y + 1)).getdata())]
        mask = Image.new("L", cell.size)
        mask.putdata(mask_pixels)
        bbox = mask.getbbox()
        if bbox is None:
            raise ValueError(f"Particle concept frame {frame} contains no visible pixels")
        crop = cell.crop(bbox).convert("RGBA")
        scale = min(8 / crop.width, 8 / crop.height)
        scaled_size = (max(1, int(crop.width * scale)), max(1, int(crop.height * scale)))
        reduced = crop.resize(scaled_size, Image.Resampling.NEAREST)
        left = (8 - scaled_size[0]) // 2
        top = (8 - scaled_size[1]) // 2
        pixels = [0] * 64
        for y in range(reduced.height):
            for x in range(reduced.width):
                red, green, blue, a = reduced.getpixel((x, y))
                if a >= 128 and max(red, green, blue) > 20:
                    pixels[(top + y) * 8 + left + x] = nearest_visible_index((red, green, blue), FX_PALETTE)
        frames.append(make_indexed((8, 8), pixels, FX_PALETTE))
        frame_report.append({"frame": frame, "source_bbox_width": bbox[2] - bbox[0], "source_bbox_height": bbox[3] - bbox[1],
                             "output_visible_pixels": sum(pixel != 0 for pixel in pixels)})

    strip_pixels: list[int] = []
    for y in range(8):
        for frame in frames:
            strip_pixels.extend(frame.getpixel((x, y)) for x in range(8))
    return make_indexed((64, 8), strip_pixels, FX_PALETTE), frame_report


def check_asset(name: str, path: Path, max_colors: int, expected_size: tuple[int, int] | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{name}: invalid PNG signature")
    bit_depth = raw[24]
    offset = 8
    plte_entries = 0
    while offset + 8 <= len(raw):
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        chunk_type = raw[offset + 4 : offset + 8]
        if chunk_type == b"PLTE":
            plte_entries = length // 3
            break
        offset += length + 12
    if bit_depth > 4 or plte_entries > 16:
        raise ValueError(f"{name}: PNG hardware format requires <=4bpp and <=16 PLTE entries; got {bit_depth}bpp/{plte_entries} entries")

    with Image.open(path) as image:
        used = sorted(set(image.getdata()))
        colors = image.getpalette() or []
        visible_colors: list[tuple[int, int, int]] = []
        for index in used:
            rgb = tuple(colors[index * 3 : index * 3 + 3])
            if index == 0 and image.info.get("transparency") == 0:
                expected_zero = VDP_BACKDROP_BLACK if name == "backdrop" else TRANSPARENT
                if rgb != expected_zero:
                    raise ValueError(f"{name}: transparent index 0 must store {expected_zero}, got {rgb}")
                continue
            if any(channel not in (0, 34, 68, 102, 136, 170, 204, 238) for channel in rgb):
                raise ValueError(f"{name}: palette color at index {index} {rgb} is outside the 9-bit grid")
            visible_colors.append(rgb)
        if image.mode != "P":
            raise ValueError(f"{name}: expected indexed PNG, got {image.mode}")
        if image.info.get("transparency") != 0:
            raise ValueError(f"{name}: palette index 0 must be transparent")
        if len(visible_colors) > max_colors:
            raise ValueError(f"{name}: {len(visible_colors)} used visible colors exceeds {max_colors}")
        if image.width % 8 or image.height % 8:
            raise ValueError(f"{name}: dimensions {image.size} do not align to 8x8")
        if expected_size and image.size != expected_size:
            raise ValueError(f"{name}: expected {expected_size}, got {image.size}")
        unique_tiles = len({tile_bytes(image, x, y) for y in range(image.height // 8) for x in range(image.width // 8)})
        return {"path": path.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(path), "size_px": list(image.size),
                "bit_depth": bit_depth, "plte_entries": plte_entries,
                "used_indices": used, "visible_colors_used": len(visible_colors), "unique_tiles": unique_tiles,
                "acceptance_status": "placeholder_speculative_downstream"}


def normalize_outputs(paths: list[Path]) -> None:
    """Compact indexed PNGs and normalize the transparent slot, without backups in res/."""
    if not PNG_NORMALIZER.is_file():
        raise FileNotFoundError(f"Shared indexed-PNG normalizer missing: {PNG_NORMALIZER}")

    output_root = PROJECT_ROOT / "out"
    output_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_png_normalize_", dir=output_root) as temp_name:
        temp_root = Path(temp_name)
        for source in paths:
            staged = temp_root / source.name
            shutil.copy2(source, staged)
            subprocess.run(
                [sys.executable, str(PNG_NORMALIZER), "transparent0", str(staged)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            data = bytearray(staged.read_bytes())
            offset = 8
            palette_updated = False
            while offset + 12 <= len(data):
                length = struct.unpack(">I", data[offset : offset + 4])[0]
                chunk_type = data[offset + 4 : offset + 8]
                if chunk_type == b"PLTE":
                    if length < 3:
                        raise ValueError(f"{source}: PNG palette is empty")
                    zero_rgb = VDP_BACKDROP_BLACK if source.name == "splash_backdrop_v3_320x224.png" else TRANSPARENT
                    data[offset + 8 : offset + 11] = bytes(zero_rgb)
                    crc_offset = offset + 8 + length
                    crc = zlib.crc32(data[offset + 4 : crc_offset]) & 0xFFFFFFFF
                    data[crc_offset : crc_offset + 4] = struct.pack(">I", crc)
                    palette_updated = True
                    break
                offset += length + 12
            if not palette_updated:
                raise ValueError(f"{source}: PNG PLTE chunk not found after normalization")
            staged.write_bytes(data)
            shutil.copy2(staged, source)


def render_with_marks(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", (320, 224), (0, 0, 0, 255))
    bg.alpha_composite(backdrop.convert("RGBA"))
    bg.alpha_composite(sgdk.convert("RGBA"), (48, 72))
    bg.alpha_composite(forge.convert("RGBA"), (64, 128))
    return bg


def composite_board(original: Image.Image, basic: Image.Image, elite: Image.Image,
                    sgdk: Image.Image, forge: Image.Image, particles: Image.Image) -> None:
    board = Image.new("RGB", (960, 448), (0, 0, 0))
    board.paste(render_with_marks(original, sgdk, forge).convert("RGB"), (0, 0))
    board.paste(render_with_marks(basic, sgdk, forge).convert("RGB"), (320, 0))
    board.paste(render_with_marks(elite, sgdk, forge).convert("RGB"), (640, 0))
    marks_only = Image.new("RGBA", (320, 224), (0, 0, 0, 255))
    marks_only.alpha_composite(sgdk.convert("RGBA"), (48, 72))
    marks_only.alpha_composite(forge.convert("RGBA"), (64, 128))
    board.paste(marks_only.convert("RGB"), (0, 224))
    particle_alpha = particles.convert("RGBA").resize((512, 64), Image.Resampling.NEAREST)
    particle_preview = Image.new("RGBA", particle_alpha.size, (0, 0, 0, 255))
    particle_preview.alpha_composite(particle_alpha)
    board.paste(particle_preview.convert("RGB"), (384, 304))
    BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    board.save(BOARD_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", help="Validate current WIP outputs without rebuilding")
    args = parser.parse_args()
    source_paths = {role: SOURCE_ROOT / filename for role, (filename, _) in SOURCES.items()}
    for role, path in source_paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing project-local source for {role}: {path}")
        expected_hash = SOURCES[role][1]
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise ValueError(f"Source hash mismatch for {role}: expected {expected_hash}, got {actual_hash}")

    output_paths = {
        "backdrop": RES_ROOT / "branding_v3" / "splash_backdrop_v3_320x224.png",
        "sgdk": RES_ROOT / "branding_v3" / "splash_sgdk_wordmark_v3_224x48.png",
        "forge": RES_ROOT / "branding_v3" / "splash_forge_wordmark_v3_192x32.png",
        "particles": RES_ROOT / "sprites" / "splash_particle_v3_8x8_strip.png",
    }
    if args.self_check:
        expected = {"backdrop": (320, 224), "sgdk": (224, 48), "forge": (192, 32), "particles": (64, 8)}
        limits = {"backdrop": 15, "sgdk": 15, "forge": 15, "particles": 15}
        results = [check_asset(name, path, limits[name], expected[name]) for name, path in output_paths.items()]
        print(json.dumps({"status": "pass", "assets": results}, indent=2))
        return 0

    for path in output_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    basic_backdrop = source_backdrop(source_paths["backdrop"])
    elite_backdrop, elite_backdrop_tiles, selected_tiles = reuse_authored_tiles(basic_backdrop, 40)
    lettering_source = Image.open(source_paths["lettering"]).convert("RGB")
    sgdk_box, sgdk_size = EXPECTED_LOGO_BOXES["sgdk"]
    forge_box, forge_size = EXPECTED_LOGO_BOXES["forge"]
    sgdk = make_wordmark(lettering_source, sgdk_box, sgdk_size)
    forge = make_wordmark(lettering_source, forge_box, forge_size)
    particles, particle_frames = make_particle_strip(source_paths["particles"])

    basic_backdrop.save(output_paths["backdrop"], format="PNG", optimize=False)
    elite_backdrop.save(ELITE_CONTROL_PATH, format="PNG", optimize=False)
    sgdk.save(output_paths["sgdk"], format="PNG", optimize=False)
    forge.save(output_paths["forge"], format="PNG", optimize=False)
    particles.save(output_paths["particles"], format="PNG", optimize=False)
    normalize_outputs(list(output_paths.values()))

    assets = [
        check_asset("backdrop", output_paths["backdrop"], 15, (320, 224)),
        check_asset("sgdk", output_paths["sgdk"], 15, (224, 48)),
        check_asset("forge", output_paths["forge"], 15, (192, 32)),
        check_asset("particles", output_paths["particles"], 15, (64, 8)),
    ]
    source_backdrop_image = Image.open(source_paths["backdrop"]).convert("RGB")
    source_preview = ImageOps.fit(source_backdrop_image, (320, 224), method=Image.Resampling.NEAREST, centering=(0.5, 0.5))
    composite_board(source_preview, basic_backdrop, elite_backdrop, sgdk, forge, particles)
    report = {
        "schema_version": "1.0.0",
        "status": "development_wip_speculative_downstream",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "builder": "data/source_art/branding_v3/build_splash_v3_visual_wip.py",
        "pixel_generation_policy": "crop_pad_palette_snap_nearest_and_reuse_source_authored_tiles_only; no drawing primitives",
        "human_visual_approval": False,
        "source_hashes": {role: sha256(path) for role, path in source_paths.items()},
        "backdrop_translation": {"source_canvas": "high-resolution AI concept", "target_canvas_px": [320, 224],
                                 "palette_roles": "PAL0 index 0 stores valid black for the hardware backdrop; mark and sprite PNGs retain the ResComp magenta transparency key at index 0",
                                 "selected_res_candidate_unique_tiles": assets[0]["unique_tiles"],
                                 "experimental_40_tile_control": {"path": ELITE_CONTROL_PATH.relative_to(PROJECT_ROOT).as_posix(),
                                     "unique_tiles": elite_backdrop_tiles, "sha256": sha256(ELITE_CONTROL_PATH),
                                     "result": "rejected_due_to_repetitive_crosshatch_noise_across_center_and_edges"},
                                 "selected_source_tile_indices": selected_tiles},
        "wordmark_translation": {"source": "AI lettering study v002", "crop_boxes": {
            "SGDK": list(sgdk_box), "FORGE": list(forge_box)},
            "outline_palette_state": "fade indices 1-9 as blue contour first; fade indices 10-15 in over 18 frames from frame 120 for the pale fill"},
        "particle_translation": {"source": "AI particle concept strip; output is a technical WIP candidate, not final native authorship",
                                  "frames": particle_frames, "sweep_strategy": "seven 8x8 crystal sprites reuse this strip as a moving trail"},
        "assets": assets,
        "review_board": {"path": BOARD_PATH.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(BOARD_PATH)},
        "limitations": ["No quality_reference_board or final human pixel approval.",
                        "No VDP VRAM/DMA/CPU/FPS claim is established by this conversion report.",
                        "A visual review in BlastEm is still required before any final-art status."],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "built_wip", "assets": assets, "report": REPORT_PATH.relative_to(PROJECT_ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
