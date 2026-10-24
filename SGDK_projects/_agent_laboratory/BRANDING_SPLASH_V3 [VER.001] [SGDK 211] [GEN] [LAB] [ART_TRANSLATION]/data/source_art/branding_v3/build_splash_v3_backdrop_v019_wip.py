#!/usr/bin/env python3
"""Translate the isolated V019 concept into a native-size WIP comparison."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/v019/source_backdrop_concept_ai_v019_20261015.png"
SOURCE_SHA256 = "9fc213cc726c3a2fbbfff0ff9e9f9e15023e29f74459398c0a5af9802536840e"
sys.path.insert(0, str(HERE))
import build_splash_v3_visual_wip as common  # noqa: E402
import build_splash_v3_backdrop_v017_wip as metrics_helper  # noqa: E402

V006 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"
V018 = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v018_curated_320x224.png"
SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"
OUTPUT = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v019_curated_320x224.png"
BOARD = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v019_comparison_wip_v001_20261015.png"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v019_translation_report_20261015.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_indexed(image: Image.Image) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_v019_", dir=str(PROJECT_ROOT / "out")) as tmp:
        staged = Path(tmp) / "splash_backdrop_v3_320x224.png"
        image.save(staged, format="PNG", optimize=False)
        common.normalize_outputs([staged])
        if OUTPUT.exists():
            if sha256(OUTPUT) != sha256(staged):
                raise FileExistsError(f"Refusing to replace a different V019 output: {OUTPUT}")
        else:
            shutil.copy2(staged, OUTPUT)


def rendered(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    return common.render_with_marks(backdrop, sgdk, forge).convert("RGB")


def make_board(candidate: Image.Image) -> None:
    with Image.open(SGDK_MARK) as source:
        sgdk = source.convert("RGBA")
    with Image.open(FORGE_MARK) as source:
        forge = source.convert("RGBA")
    panels: list[tuple[str, Image.Image]] = []
    for label, path in (("V006 BASELINE", V006), ("V018 CONTROL", V018)):
        with Image.open(path) as source:
            panels.append((label, rendered(source.copy(), sgdk, forge)))
    panels.append(("V019 CANDIDATE", rendered(candidate, sgdk, forge)))
    board = Image.new("RGB", (960, 244), (3, 5, 18))
    draw = ImageDraw.Draw(board)
    for x, (label, panel) in zip((0, 320, 640), panels):
        draw.text((x + 6, 3), label, fill=(174, 214, 255))
        board.paste(panel, (x, 20))
    if BOARD.exists():
        with Image.open(BOARD) as old:
            if old.convert("RGB").tobytes() != board.tobytes():
                raise FileExistsError(f"Refusing to replace a different V019 board: {BOARD}")
    else:
        BOARD.parent.mkdir(parents=True, exist_ok=True)
        board.save(BOARD, format="PNG", optimize=False)


def main() -> int:
    if not SOURCE.is_file() or sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("V019 source missing or hash changed")
    for path in (V006, V018, SGDK_MARK, FORGE_MARK):
        if not path.is_file():
            raise FileNotFoundError(path)
    if REPORT.exists():
        raise FileExistsError(f"Refusing to replace existing V019 report: {REPORT}")

    with Image.open(SOURCE) as source:
        if source.size != (1499, 1049) or source.mode != "RGB":
            raise ValueError(f"Unexpected V019 source format: {source.size}/{source.mode}")
        candidate = common.source_backdrop(SOURCE)
    save_indexed(candidate)
    asset = common.check_asset("backdrop", OUTPUT, 15, (320, 224))
    make_board(candidate)
    with Image.open(V006) as source:
        v006_tiles = metrics_helper.tile_metrics(source)
    with Image.open(V018) as source:
        v018_tiles = metrics_helper.tile_metrics(source)
    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "splash_v3_backdrop_translation_preview",
        "candidate": "V019",
        "status": "lab_translation_needs_visual_and_semantic_review",
        "acceptance_status": "placeholder",
        "source_path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
        "source_sha256": SOURCE_SHA256,
        "generation_source": "data/source_art/branding_v3/sources/source_backdrop_concept_ai_v006_20261014.png",
        "generation_source_sha256": "f3e924c1580c8ead73b0df84b9b557cef69af45eeff4e311bf236b7b371829b8",
        "translation_method": "Nearest 320x224 sampling and fixed 16-entry Mega Drive 9-bit RGB palette; index 0 stores the VDP background black using the project backdrop convention. No runtime-authored pixels or vignette.",
        "semantic_read": "One BG_B plate with asymmetric side crystal masses, a broad dark logo-safe field, sparse upper-right shards and broken lower diagonal energy seams converging to a small bottom-center ignition; no continuous horizon or floor grid.",
        "asset": asset,
        "tile_metrics": metrics_helper.tile_metrics(candidate),
        "visual_metrics": metrics_helper.visual_metrics(candidate),
        "comparison_controls": {
            "V006_sha256": sha256(V006),
            "V006_unique_hv_tiles": v006_tiles["unique_tiles_hv"],
            "V018_sha256": sha256(V018),
            "V018_unique_hv_tiles": v018_tiles["unique_tiles_hv"],
        },
        "comparison_board": BOARD.relative_to(PROJECT_ROOT).as_posix(),
        "promotion": {
            "eligible_for_res": False,
            "human_visual_approval": False,
            "template_promotion_authorized": False,
            "forja_v2_archive_authorized": False,
        },
        "limitations": [
            "Nearest-sampled concept translation is a WIP, not manual native 8x8 redrawing.",
            "The WIP wordmark masks in the comparison are not approved final typography.",
            "The report measures asset geometry only; ROM, animation, CRT, full VRAM, DMA and runtime remain unmeasured.",
            "No approved quality_reference_board exists; visual status cannot exceed needs_review.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "asset_sha256": asset["sha256"],
        "tile_metrics": report["tile_metrics"],
        "visual_metrics": report["visual_metrics"],
        "comparison_controls": report["comparison_controls"],
        "board": report["comparison_board"],
        "report": REPORT.relative_to(PROJECT_ROOT).as_posix(),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
