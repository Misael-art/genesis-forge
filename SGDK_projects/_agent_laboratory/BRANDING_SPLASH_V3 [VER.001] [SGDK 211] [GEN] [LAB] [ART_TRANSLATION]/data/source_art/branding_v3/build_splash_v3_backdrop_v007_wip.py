#!/usr/bin/env python3
"""Build basic and curated VDP-grid WIP translations for backdrop source V007."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/sources/source_backdrop_concept_ai_v007_20261014.png"
SOURCE_SHA256 = "3888fb24313aa17a8f246fd769db07e22cfe93ecae6e62ac28b8a323992f04ac"
COMMON_PATH = PROJECT_ROOT / "data/source_art/branding_v3/build_splash_v3_visual_wip.py"
sys.path.insert(0, str(COMMON_PATH.parent))
import build_splash_v3_visual_wip as common  # noqa: E402

SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"
OUTPUTS = {
    "basic": PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v007_basic_320x224.png",
    "elite": PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v007_elite_320x224.png",
    "board": PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v007_comparison_wip_v002_20261014.png",
    "report": PROJECT_ROOT / "out/logs/splash_v3_backdrop_v007_translation_report_v002_20261014.json",
}
LEVELS = (0, 34, 68, 102, 136, 170, 204, 238)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snap_color(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(min(LEVELS, key=lambda value: (abs(value - channel), value)) for channel in rgb)


def make_basic(source: Image.Image) -> Image.Image:
    """Median-cut 15-color control, snapped to the Mega Drive's 9-bit grid."""
    quantized = source.quantize(colors=15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    raw_palette = quantized.getpalette() or []
    original_colors = [tuple(raw_palette[i * 3 : i * 3 + 3]) for i in range(15)]
    mapped: dict[tuple[int, int, int], int] = {}
    visible: list[tuple[int, int, int]] = []
    for color in original_colors:
        snapped = snap_color(color)
        if snapped != (0, 0, 0) and snapped not in visible:
            visible.append(snapped)
    visible.sort(key=lambda c: (c[0] * 3 + c[1] * 6 + c[2], c[2], c[1], c[0]))
    palette = [common.VDP_BACKDROP_BLACK] + visible[:15]
    for index, color in enumerate(original_colors):
        snapped = snap_color(color)
        if snapped == (0, 0, 0):
            mapped[color] = 0
        else:
            mapped[color] = 1 + palette[1:].index(snapped)
    pixels = [mapped[original_colors[index]] for index in quantized.get_flattened_data()]
    return common.make_indexed((320, 224), pixels, palette)


def canonical_hv(tile: bytes) -> bytes:
    rows = [tile[index * 8 : (index + 1) * 8] for index in range(8)]
    variants = (
        tile,
        b"".join(row[::-1] for row in rows),
        b"".join(rows[::-1]),
        b"".join(row[::-1] for row in rows[::-1]),
    )
    return min(variants)


def tile_counts(image: Image.Image) -> dict[str, int]:
    tiles = [
        common.tile_bytes(image, x, y)
        for y in range(image.height // 8)
        for x in range(image.width // 8)
    ]
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": len(set(tiles)),
        "unique_hv_tiles": len({canonical_hv(tile) for tile in tiles}),
    }


def render(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    return common.render_with_marks(backdrop, sgdk, forge).convert("RGB")


def normalize_and_save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_v007_", dir=str(PROJECT_ROOT / "out")) as tmp:
        stage_dir = Path(tmp) / path.stem
        stage_dir.mkdir()
        stage = stage_dir / "splash_backdrop_v3_320x224.png"
        image.save(stage, format="PNG", optimize=False)
        common.normalize_outputs([stage])
        if path.exists():
            if sha256(path) != sha256(stage):
                raise FileExistsError(f"Refusing to replace a different V007 review output: {path}")
        else:
            shutil.copy2(stage, path)


def main() -> int:
    if not SOURCE.is_file() or sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("V007 source missing or hash changed")
    if not SGDK_MARK.is_file() or not FORGE_MARK.is_file():
        raise FileNotFoundError("Current WIP wordmark plates are required for comparison")

    with Image.open(SOURCE) as source_file:
        source = ImageOps.fit(
            source_file.convert("RGB"), (320, 224),
            method=Image.Resampling.LANCZOS, centering=(0.5, 0.5),
        )
    basic = make_basic(source)
    elite = common.source_backdrop(SOURCE)
    normalize_and_save(basic, OUTPUTS["basic"])
    normalize_and_save(elite, OUTPUTS["elite"])

    basic_checked = common.check_asset("backdrop", OUTPUTS["basic"], 15, (320, 224))
    elite_checked = common.check_asset("backdrop", OUTPUTS["elite"], 15, (320, 224))
    with Image.open(SGDK_MARK) as sgdk_file, Image.open(FORGE_MARK) as forge_file:
        sgdk = sgdk_file.convert("RGBA")
        forge = forge_file.convert("RGBA")
    with Image.open(OUTPUTS["elite"]) as elite_file:
        elite_image = elite_file.copy()
    with Image.open(PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png") as v006_file:
        v006 = v006_file.copy()

    board = Image.new("RGB", (1280, 244), (3, 5, 18))
    draw = ImageDraw.Draw(board)
    panels = [
        (0, "SOURCE FIT", render(source, sgdk, forge)),
        (320, "BASIC 15 COLOR", render(basic, sgdk, forge)),
        (640, "CURATED PALETTE", render(elite_image, sgdk, forge)),
        (960, "V006 CONTROL", render(v006, sgdk, forge)),
    ]
    for x, label, panel in panels:
        draw.text((x + 8, 3), label, fill=(174, 214, 255))
        board.paste(panel, (x, 20))
    OUTPUTS["board"].parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_v007_board_", dir=str(PROJECT_ROOT / "out")) as tmp:
        staged_board = Path(tmp) / "comparison.png"
        board.save(staged_board, format="PNG", optimize=False)
        if OUTPUTS["board"].exists():
            if sha256(OUTPUTS["board"]) != sha256(staged_board):
                raise FileExistsError(f"Refusing to replace a different V007 comparison board: {OUTPUTS['board']}")
        else:
            shutil.copy2(staged_board, OUTPUTS["board"])

    center_roi = elite_image.convert("RGB").crop((80, 56, 240, 164))
    center_luma = sum((r * 3 + g * 6 + b) // 10 for r, g, b in center_roi.get_flattened_data()) / (160 * 108)
    report = {
        "schema_version": "1.0.0",
        "status": "lab_translation_needs_visual_review",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": SOURCE_SHA256,
            "canvas_px": [1499, 1049],
            "source_class": "single_frame_background_concept",
            "semantic_parse": {
                "must_keep": ["broad dark center", "large asymmetric left crystal mass", "sparse right shards", "diagonal blue energy streaks", "compact ignition below center"],
                "can_simplify": ["microtexture", "isolated subpixel shards", "tiny specular noise"],
                "must_drop": ["photographic texture", "haze", "checkerboard-like repetition", "any detail that intrudes into the wordmark safe area"],
                "palette_roles": ["index 0: VDP black", "deep navy shadow", "cobalt structure", "blue/cyan facets", "ice-blue highlight", "sparse white pinpoint"],
            },
        },
        "translation": {
            "target_px": [320, 224],
            "basic_method": "LANCZOS fit to target, median-cut 15-color control, then RGB channels snapped to the 9-bit VDP grid",
            "elite_method": "curated fixed BG_PALETTE with per-pixel nearest color assignment and a near-black-to-index-zero threshold from the shared V3 translation helper",
            "human_visual_approval": False,
            "runtime_candidate": False,
        },
        "candidates": {
            "basic": {**basic_checked, **tile_counts(basic)},
            "elite": {**elite_checked, **tile_counts(elite_image)},
        },
        "comparison": {
            "path": OUTPUTS["board"].relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256(OUTPUTS["board"]),
            "panels": ["source fit", "basic 15-color control", "curated fixed palette", "current V006 control"],
            "wordmark_overlay": "current SGDK/FORGE WIP plates, comparison only",
            "v006_control": {
                "path": "res/branding_v3/splash_backdrop_v3_v006_320x224.png",
                "sha256": sha256(PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"),
                "tiles": tile_counts(v006),
            },
            "elite_center_roi_mean_luma_0_255": round(center_luma, 2),
        },
        "findings_to_review": [
            "Does the asymmetric silhouette survive at native 320x224, or do the left facets collapse into noise?",
            "Do the diagonal streaks read as purposeful motion without cutting through SGDK/FORGE?",
            "Is the dark logo window wide and dark enough during outline, fill, sweep, and final hold?",
            "Do the lower ignition and white/cyan clusters stay subordinate to FORGE?",
            "Compare V007 basic and curated palette against V006; the tile count is not a quality score.",
        ],
        "promotion": {
            "translation_source_selected": False,
            "runtime_asset_promoted": False,
            "final_visual_approval": False,
            "model_sheet_approved": False,
            "template_promotion_authorized": False,
            "forja_v2_archive_authorized": False,
            "future_review_required": True,
        },
    }
    OUTPUTS["report"].parent.mkdir(parents=True, exist_ok=True)
    report_text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if OUTPUTS["report"].exists():
        raise FileExistsError(f"Refusing to replace existing V007 translation report: {OUTPUTS['report']}")
    OUTPUTS["report"].write_text(report_text, encoding="utf-8")
    print(json.dumps({"status": report["status"], "comparison": report["comparison"], "report": OUTPUTS["report"].relative_to(PROJECT_ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
