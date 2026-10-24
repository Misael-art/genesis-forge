#!/usr/bin/env python3
"""Build a V016 translation challenger with a feathered logo-field vignette.

V015's hard rectangular palette clamp is preserved as a comparison. V016 uses
the same eligible concept source and palette, with a smooth oval luminance field
to protect the wordmarks without drawing a rectangular hole in the crystal art.
The result remains a WIP translation, not native hand-authored final art.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/v015/source_backdrop_concept_ai_v015_20261015.png"
SOURCE_SHA256 = "87293cf5275564733d27d5a166f1071f04bb2b447257a07c5a3f0c6b9c0c9188"
sys.path.insert(0, str(SOURCE.parent))
import build_splash_v3_visual_wip as common  # noqa: E402

V006 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"
V014 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v014_320x224.png"
V015 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v015_320x224.png"
SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"

OUTPUT = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v016_curated_320x224.png"
BOARD = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v016_comparison_wip_v001_20261015.png"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v016_translation_report_20261015.json"

MARKS = (
    (SGDK_MARK, (48, 72)),
    (FORGE_MARK, (64, 128)),
)
FIELD_CENTER = (160.0, 116.0)
FIELD_RADII = (128.0, 62.0)
FIELD_INNER = 0.68
FIELD_OUTER = 1.18
FIELD_STRENGTH = 0.78
FIELD_COLOR = common.BG_PALETTE[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def logo_mask() -> Image.Image:
    mask = Image.new("L", (320, 224), 0)
    for path, position in MARKS:
        with Image.open(path) as source:
            alpha = source.convert("RGBA").getchannel("A")
        mask.paste(alpha, position)
    return mask


def make_vignette(source: Image.Image) -> tuple[Image.Image, dict[str, object]]:
    fitted = ImageOps.fit(
        source.convert("RGB"), (320, 224), method=Image.Resampling.NEAREST,
        centering=(0.5, 0.5),
    )
    pixels: list[int] = []
    for y in range(224):
        for x in range(320):
            rgb = fitted.getpixel((x, y))
            if max(rgb) <= 22:
                pixels.append(0)
                continue
            dx = (x - FIELD_CENTER[0]) / FIELD_RADII[0]
            dy = (y - FIELD_CENTER[1]) / FIELD_RADII[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= FIELD_INNER:
                strength = FIELD_STRENGTH
            elif distance >= FIELD_OUTER:
                strength = 0.0
            else:
                t = (FIELD_OUTER - distance) / (FIELD_OUTER - FIELD_INNER)
                strength = FIELD_STRENGTH * (t * t * (3.0 - 2.0 * t))
            adjusted = tuple(
                round(rgb[channel] * (1.0 - strength) + FIELD_COLOR[channel] * strength)
                for channel in range(3)
            )
            pixels.append(common.nearest_visible_index(adjusted, common.BG_PALETTE))

    image = common.make_indexed((320, 224), pixels, common.BG_PALETTE)
    mask = logo_mask()
    values: list[int] = []
    for path, (left, top) in MARKS:
        with Image.open(path) as mark:
            alpha = mark.convert("RGBA").getchannel("A")
        for my in range(alpha.height):
            for mx in range(alpha.width):
                if alpha.getpixel((mx, my)) == 0:
                    continue
                x, y = left + mx, top + my
                color = common.BG_PALETTE[image.getpixel((x, y))]
                values.append((color[0] * 3 + color[1] * 6 + color[2]) // 10)
    stats = {
        "mask_pixels": sum(1 for value in mask.get_flattened_data() if value > 0),
        "wordmark_sample_pixels": len(values),
        "wordmark_underlay_mean_luma_0_255": round(sum(values) / max(1, len(values)), 2),
        "wordmark_underlay_share_above_32": round(sum(value > 32 for value in values) / max(1, len(values)), 4),
    }
    return image, stats


def tile_bytes(image: Image.Image, tile_x: int, tile_y: int) -> bytes:
    return common.tile_bytes(image, tile_x, tile_y)


def canonical_hv(tile: bytes) -> bytes:
    rows = [tile[index * 8 : (index + 1) * 8] for index in range(8)]
    return min((tile, b"".join(row[::-1] for row in rows), b"".join(rows[::-1]),
                b"".join(row[::-1] for row in rows[::-1])))


def tile_metrics(image: Image.Image) -> dict[str, int]:
    tiles = [tile_bytes(image, x, y) for y in range(28) for x in range(40)]
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": len(set(tiles)),
        "unique_tiles_with_hv_flips": len({canonical_hv(tile) for tile in tiles}),
    }


def save_indexed(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_v016_", dir=str(PROJECT_ROOT / "out")) as tmp:
        staged = Path(tmp) / "splash_backdrop_v3_320x224.png"
        image.save(staged, format="PNG", optimize=False)
        common.normalize_outputs([staged])
        if path.exists():
            if sha256(path) != sha256(staged):
                raise FileExistsError(f"Refusing to replace a different V016 output: {path}")
        else:
            shutil.copy2(staged, path)


def render(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    return common.render_with_marks(backdrop, sgdk, forge).convert("RGB")


def save_board(image: Image.Image) -> None:
    if BOARD.exists():
        with Image.open(BOARD) as existing:
            if ImageChops.difference(existing.convert("RGB"), image.convert("RGB")).getbbox():
                raise FileExistsError(f"Refusing to replace a different V016 comparison: {BOARD}")
        return
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    image.save(BOARD, format="PNG", optimize=False)


def main() -> int:
    if not SOURCE.is_file() or sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("V015 source missing or hash changed")
    for path in (V006, V014, V015, SGDK_MARK, FORGE_MARK):
        if not path.is_file():
            raise FileNotFoundError(path)
    if REPORT.exists():
        raise FileExistsError(f"Refusing to replace existing V016 report: {REPORT}")

    with Image.open(SOURCE) as source:
        candidate, wordmark_stats = make_vignette(source)
    save_indexed(candidate, OUTPUT)
    checked = common.check_asset("backdrop", OUTPUT, 15, (320, 224))

    with Image.open(SGDK_MARK) as image:
        sgdk = image.convert("RGBA")
    with Image.open(FORGE_MARK) as image:
        forge = image.convert("RGBA")
    panels: list[tuple[str, Image.Image]] = []
    for label, path in (("V006 BASELINE", V006), ("V014 CONTROL", V014), ("V015 RECTANGLE", V015), ("V016 SOFT OVAL", OUTPUT)):
        with Image.open(path) as image:
            panels.append((label, render(image.copy(), sgdk, forge)))
    board = Image.new("RGB", (1280, 244), (3, 5, 18))
    draw = ImageDraw.Draw(board)
    for x, (label, panel) in zip((0, 320, 640, 960), panels):
        draw.text((x + 8, 3), label, fill=(174, 214, 255))
        board.paste(panel, (x, 20))
    save_board(board)

    report = {
        "schema_version": "1.0.0",
        "status": "lab_translation_needs_visual_and_semantic_review",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": SOURCE_SHA256,
            "source_class": "single_frame_background_concept",
            "semantic_parse": "doc/art/splash_v3_v015_source_semantics_manifest.json",
            "automatic_inference_disposition": "Rejected stage_board false positive; no cuts or preview panels were inferred from this source.",
        },
        "translation": {
            "target_px": [320, 224],
            "hardware_grid": "8x8",
            "method": "nearest source sampling; fixed 15-color BG palette; no dithering; radial smoothstep darkening inside a feathered oval logo field",
            "field_center_px": list(FIELD_CENTER),
            "field_radii_px": list(FIELD_RADII),
            "field_inner_radius_normalized": FIELD_INNER,
            "field_outer_radius_normalized": FIELD_OUTER,
            "field_strength": FIELD_STRENGTH,
            "field_target_palette_index": 1,
            "replaces_v015_policy": "Hard rectangular clamp x=45..274/y=67..165 caused a visible rectangular cutout in the BlastEm screenshot.",
            "curated_is_manual_native_redraw": False,
            "manual_native_authoring_complete": False,
            "runtime_candidate": False,
            "production_allowed": False,
        },
        "candidate": {**checked, **tile_metrics(candidate)},
        "wordmark_readability_probe": wordmark_stats,
        "comparison": {
            "path": BOARD.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256(BOARD),
            "panels": [label for label, _ in panels],
            "rendering": "native 320x224, SGDK/FORGE WIP plates over each background",
        },
        "review_findings": [
            "Does the feathered oval preserve wordmark contrast without looking like a vignette sticker?",
            "Does the asymmetric crystal frame remain energetic at native 320x224?",
            "Does the lower reflection still compete with FORGE or the convergence point?",
            "Compare V016's tile cost and hierarchy against the V006 baseline; no tile cap was applied.",
        ],
        "promotion": {
            "translation_source_selected": False,
            "runtime_asset_promoted": False,
            "final_visual_approval": False,
            "template_promotion_authorized": False,
            "forja_v2_archive_authorized": False,
            "future_review_required": True,
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "candidate": OUTPUT.relative_to(PROJECT_ROOT).as_posix(),
                      "sha256": checked["sha256"], "tiles_hv": report["candidate"]["unique_tiles_with_hv_flips"],
                      "board": BOARD.relative_to(PROJECT_ROOT).as_posix(),
                      "wordmark_probe": wordmark_stats}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
