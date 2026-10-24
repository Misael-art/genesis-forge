#!/usr/bin/env python3
"""Build native-size, source-derived lettering probes outside runtime resources.

This tool crops the persisted AI lettering study, scales each wordmark to the
existing 8-pixel plate contracts, snaps colors to the Mega Drive 9-bit grid,
and composites review frames over the selected V005 backdrop. It does not draw
glyphs. By default it writes only to rascunho/visual_lab; the explicit
--activate-b-preview flag backs up the pre-B plates once and copies B into the
existing isolated WIP res paths.
"""

from __future__ import annotations

import hashlib
import argparse
import json
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = PROJECT_ROOT.parents[2]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/sources/source_lettering_model_sheet_ai_v003_20261014.png"
BACKDROP = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v005_320x224.png"
RUNTIME_SGDK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
RUNTIME_FORGE = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"
NORMALIZER = WORKSPACE_ROOT / "tools/image-tools/normalize_indexed_sgdk_png.py"
OUTPUT_ROOT = PROJECT_ROOT / "rascunho/visual_lab"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_lettering_native_probe_20261014.json"

EXPECTED_SOURCE_SHA256 = "d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8"
SOURCE_BACKGROUND = (2, 9, 52)
TRANSPARENT = (255, 0, 255)
MARK_PALETTE = [
    TRANSPARENT,
    (0, 0, 68), (0, 0, 102), (0, 0, 170), (0, 34, 204), (0, 68, 136),
    (0, 68, 204), (0, 102, 170), (0, 102, 238), (34, 136, 238),
    (34, 170, 238), (34, 204, 238), (102, 204, 238), (170, 204, 238),
    (204, 238, 238), (238, 238, 238),
]

# Crops were measured against the persistent V003 board. Padding retains the
# authored outline and shadow without carrying the board's navy field.
DIRECTIONS = {
    "A": {
        "name": "heroic_ice",
        "sgdk_crop": (410, 49, 1254, 205),
        "forge_crop": (510, 212, 1161, 306),
    },
    "B": {
        "name": "faceted_crystal",
        "sgdk_crop": (401, 362, 1276, 518),
        "forge_crop": (512, 523, 1169, 619),
    },
    "C": {
        "name": "forward_energy",
        "sgdk_crop": (346, 667, 1341, 815),
        "forge_crop": (516, 815, 1178, 896),
    },
}
PLATES = {"sgdk": (224, 48), "forge": (192, 32)}
PLACEMENTS = {"sgdk": (48, 72), "forge": (64, 128)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def palette_bytes() -> list[int]:
    colors = [channel for rgb in MARK_PALETTE for channel in rgb]
    return colors + [0] * (768 - len(colors))


def nearest_visible_index(rgb: tuple[int, int, int]) -> int:
    return min(
        range(1, 16),
        key=lambda index: sum((rgb[channel] - MARK_PALETTE[index][channel]) ** 2 for channel in range(3)),
    )


def color_luma(rgb: tuple[int, int, int]) -> int:
    return (299 * rgb[0] + 587 * rgb[1] + 114 * rgb[2]) // 1000


def validate_palette_roles() -> None:
    valid_channels = {0, 34, 68, 102, 136, 170, 204, 238}
    if any(channel not in valid_channels for color in MARK_PALETTE[1:] for channel in color):
        raise ValueError("Lettering palette has colors outside the Mega Drive 9-bit grid")
    outline_max = max(color_luma(color) for color in MARK_PALETTE[1:10])
    fill_min = min(color_luma(color) for color in MARK_PALETTE[10:16])
    if outline_max >= fill_min:
        raise ValueError(f"Palette outline/fill roles overlap: outline max {outline_max}, fill min {fill_min}")


def make_probe_plate(source: Image.Image, box: tuple[int, int, int, int], size: tuple[int, int]) -> Image.Image:
    crop = source.crop(box).convert("RGB")
    target_w, target_h = size
    scale = min(target_w / crop.width, (target_h - 4) / crop.height)
    scaled_size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    reduced = crop.resize(scaled_size, Image.Resampling.LANCZOS)
    offset_x = (target_w - scaled_size[0]) // 2
    offset_y = (target_h - scaled_size[1]) // 2

    image = Image.new("P", size, 0)
    pixels = [0] * (target_w * target_h)
    for y in range(reduced.height):
        for x in range(reduced.width):
            rgb = reduced.getpixel((x, y))
            distance_sq = sum((rgb[channel] - SOURCE_BACKGROUND[channel]) ** 2 for channel in range(3))
            # Antialiased board-background pixels stay transparent; visible
            # outline, face, facet and highlight colors are snapped to 9-bit.
            if distance_sq > 256:
                pixels[(offset_y + y) * target_w + offset_x + x] = nearest_visible_index(rgb)
    image.putdata(pixels)
    image.putpalette(palette_bytes())
    image.info["transparency"] = 0
    return image


def normalize(path: Path) -> None:
    subprocess.run([sys.executable, str(NORMALIZER), "transparent0", str(path)], check=True)


def tile_data(image: Image.Image, tile_x: int, tile_y: int, flip_h: bool = False, flip_v: bool = False) -> bytes:
    return bytes(
        image.getpixel((tile_x * 8 + (7 - x if flip_h else x), tile_y * 8 + (7 - y if flip_v else y)))
        for y in range(8)
        for x in range(8)
    )


def tile_counts(image: Image.Image) -> tuple[int, int]:
    raw_tiles: set[bytes] = set()
    hv_tiles: set[bytes] = set()
    for tile_y in range(image.height // 8):
        for tile_x in range(image.width // 8):
            raw = tile_data(image, tile_x, tile_y)
            raw_tiles.add(raw)
            hv_tiles.add(min(tile_data(image, tile_x, tile_y, h, v) for h in (False, True) for v in (False, True)))
    return len(raw_tiles), len(hv_tiles)


def png_shape(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    bit_depth = raw[24]
    offset = 8
    entries = 0
    while offset + 12 <= len(raw):
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        kind = raw[offset + 4 : offset + 8]
        if kind == b"PLTE":
            entries = length // 3
            break
        offset += length + 12
    with Image.open(path) as image:
        if image.mode != "P" or image.info.get("transparency") != 0:
            raise ValueError(f"{path}: expected indexed PNG with transparent index 0")
        if bit_depth > 4 or image.width % 8 or image.height % 8 or entries > 16:
            raise ValueError(f"{path}: plate does not meet <=4bpp, <=16 colors, and 8x8 alignment")
        used = sorted(set(image.getdata()))
        visible = [index for index in used if index != 0]
        unique_tiles, hv_unique_tiles = tile_counts(image)
        return {
            "path": path.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256(path),
            "size_px": list(image.size),
            "bit_depth": bit_depth,
            "plte_entries": entries,
            "used_indices": used,
            "visible_colors_used": len(visible),
            "visible_pixels": sum(pixel != 0 for pixel in image.getdata()),
            "unique_tiles": unique_tiles,
            "hv_unique_tiles": hv_unique_tiles,
        }


def frame(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    canvas = backdrop.convert("RGBA")
    canvas.alpha_composite(sgdk.convert("RGBA"), PLACEMENTS["sgdk"])
    canvas.alpha_composite(forge.convert("RGBA"), PLACEMENTS["forge"])
    return canvas.convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--activate-b-preview",
        action="store_true",
        help="Back up current runtime wordmarks once, then copy B probe plates to existing WIP res paths.",
    )
    args = parser.parse_args()
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise ValueError("Lettering board source hash mismatch; refusing to use a changed board")
    validate_palette_roles()
    if not BACKDROP.is_file() or not NORMALIZER.is_file():
        raise FileNotFoundError("V005 backdrop or indexed-PNG normalizer missing")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    baseline_sgdk = OUTPUT_ROOT / "splash_sgdk_wordmark_v3_baseline_pre_b_20261014_224x48.png"
    baseline_forge = OUTPUT_ROOT / "splash_forge_wordmark_v3_baseline_pre_b_20261014_192x32.png"
    with Image.open(SOURCE) as source_file:
        source = source_file.convert("RGB")
    if source.size != (1672, 941):
        raise ValueError(f"Unexpected lettering board size: {source.size}")
    with Image.open(BACKDROP) as backdrop_file:
        backdrop = backdrop_file.convert("RGBA")
    if backdrop.size != (320, 224):
        raise ValueError(f"Unexpected V005 backdrop size: {backdrop.size}")

    outputs: dict[str, dict[str, object]] = {}
    frames: dict[str, Image.Image] = {}
    for direction, contract in DIRECTIONS.items():
        sgdk_path = OUTPUT_ROOT / f"splash_v3_wordmark_sgdk_probe_{direction.lower()}_v001_224x48.png"
        forge_path = OUTPUT_ROOT / f"splash_v3_wordmark_forge_probe_{direction.lower()}_v001_192x32.png"
        sgdk = make_probe_plate(source, contract["sgdk_crop"], PLATES["sgdk"])
        forge = make_probe_plate(source, contract["forge_crop"], PLATES["forge"])
        sgdk.save(sgdk_path, format="PNG", optimize=False)
        forge.save(forge_path, format="PNG", optimize=False)
        normalize(sgdk_path)
        normalize(forge_path)
        with Image.open(sgdk_path) as sgdk_png, Image.open(forge_path) as forge_png:
            if sgdk_png.size != PLATES["sgdk"] or forge_png.size != PLATES["forge"]:
                raise ValueError(f"{direction}: plate dimensions changed during normalization")
            if sgdk_png.mode != "P" or forge_png.mode != "P":
                raise ValueError(f"{direction}: normalized plates must remain indexed PNGs")
            frames[direction] = frame(backdrop, sgdk_png.copy(), forge_png.copy())
        outputs[direction] = {
            "direction": contract["name"],
            "source_crop_sgdk": list(contract["sgdk_crop"]),
            "source_crop_forge": list(contract["forge_crop"]),
            "sgdk": png_shape(sgdk_path),
            "forge": png_shape(forge_path),
        }
        frame_path = OUTPUT_ROOT / f"splash_v3_lettering_probe_{direction.lower()}_v001_320x224.png"
        frames[direction].save(frame_path, format="PNG", optimize=False)
        outputs[direction]["viewport_probe"] = {
            "path": frame_path.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256(frame_path),
            "size_px": [320, 224],
        }

    if args.activate_b_preview:
        for runtime_path, backup_path in ((RUNTIME_SGDK, baseline_sgdk), (RUNTIME_FORGE, baseline_forge)):
            if not backup_path.exists():
                shutil.copy2(runtime_path, backup_path)
        shutil.copy2(OUTPUT_ROOT / "splash_v3_wordmark_sgdk_probe_b_v001_224x48.png", RUNTIME_SGDK)
        shutil.copy2(OUTPUT_ROOT / "splash_v3_wordmark_forge_probe_b_v001_192x32.png", RUNTIME_FORGE)
        normalize(RUNTIME_SGDK)
        normalize(RUNTIME_FORGE)

    current_path = OUTPUT_ROOT / "splash_v3_lettering_current_runtime_baseline_320x224.png"
    baseline_source_sgdk = baseline_sgdk if baseline_sgdk.is_file() else RUNTIME_SGDK
    baseline_source_forge = baseline_forge if baseline_forge.is_file() else RUNTIME_FORGE
    with Image.open(baseline_source_sgdk) as sgdk_file, Image.open(baseline_source_forge) as forge_file:
        current = frame(backdrop, sgdk_file.copy(), forge_file.copy())
    current.save(current_path, format="PNG", optimize=False)

    variants_contact = Image.new("RGB", (960, 224), (0, 0, 0))
    comparison_contact = Image.new("RGB", (1280, 224), (0, 0, 0))
    comparison_contact.paste(current, (0, 0))
    for index, direction in enumerate(("A", "B", "C")):
        variants_contact.paste(frames[direction], (index * 320, 0))
        comparison_contact.paste(frames[direction], ((index + 1) * 320, 0))
    variants_path = OUTPUT_ROOT / "splash_v3_lettering_variants_native_v001_960x224.png"
    comparison_path = OUTPUT_ROOT / "splash_v3_lettering_current_vs_variants_native_v001_1280x224.png"
    variants_contact.save(variants_path, format="PNG", optimize=False)
    comparison_contact.save(comparison_path, format="PNG", optimize=False)

    runtime_b_active = (
        sha256(RUNTIME_SGDK) == sha256(OUTPUT_ROOT / "splash_v3_wordmark_sgdk_probe_b_v001_224x48.png")
        and sha256(RUNTIME_FORGE) == sha256(OUTPUT_ROOT / "splash_v3_wordmark_forge_probe_b_v001_192x32.png")
    )
    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "splash_v3_lettering_native_translation_probe",
        "status": "b_candidate_active_wip" if runtime_b_active else "visual_lab_control_not_runtime",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "builder": "data/source_art/branding_v3/build_splash_v3_lettering_native_probes.py",
        "source": {"path": SOURCE.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(SOURCE), "size_px": list(source.size)},
        "backdrop": {"path": BACKDROP.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(BACKDROP), "size_px": list(backdrop.size)},
        "translation": {
            "operations": ["crop source-authored AI lettering", "aspect-preserving LANCZOS reduction", "background-key removal", "snap to 9-bit palette", "normalize to indexed <=4bpp PNG", "composite over exact V005 WIP backdrop"],
            "palette_roles": "indices 1-9 carry the dark/blue contour; indices 10-15 carry the pale fill revealed at runtime.",
            "no_glyph_drawing": True,
            "writes_runtime_resources": bool(args.activate_b_preview),
            "runtime_write_scope": "only the existing isolated WIP wordmark paths when --activate-b-preview is set; pre-B baselines are preserved",
            "human_selection": False,
            "model_sheet_approved": False,
        },
        "runtime_activation": {
            "status": "b_preview_active_wip" if args.activate_b_preview else ("b_preview_already_active_wip" if sha256(RUNTIME_SGDK) == sha256(OUTPUT_ROOT / "splash_v3_wordmark_sgdk_probe_b_v001_224x48.png") else "preview_only"),
            "activated_this_run": args.activate_b_preview,
            "runtime_assets": [
                {"path": RUNTIME_SGDK.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(RUNTIME_SGDK)},
                {"path": RUNTIME_FORGE.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(RUNTIME_FORGE)},
            ],
            "pre_b_baseline": [
                {"path": baseline_sgdk.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(baseline_sgdk)} if baseline_sgdk.is_file() else None,
                {"path": baseline_forge.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(baseline_forge)} if baseline_forge.is_file() else None,
            ],
        },
        "directions": outputs,
        "current_runtime_baseline": {"path": current_path.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(current_path), "size_px": [320, 224]},
        "contact_sheets": {
            "variants_A_B_C": {"path": variants_path.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(variants_path), "size_px": [960, 224], "panel_order": ["A", "B", "C"]},
            "current_then_A_B_C": {"path": comparison_path.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(comparison_path), "size_px": [1280, 224], "panel_order": ["current_runtime_placeholder", "A", "B", "C"]},
        },
        "limitations": ["Derived AI concepts remain placeholders, not authored final lettering.", "Contact sheet panels are 320x224 each at 1:1 source size; the combined sheet is wider for review.", "An active B preview remains placeholder WIP; copying it into isolated /res paths does not approve visual quality or final runtime integration."],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": REPORT.relative_to(PROJECT_ROOT).as_posix(), "variants": list(outputs), "contact_sheet": report["contact_sheets"]["current_then_A_B_C"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
