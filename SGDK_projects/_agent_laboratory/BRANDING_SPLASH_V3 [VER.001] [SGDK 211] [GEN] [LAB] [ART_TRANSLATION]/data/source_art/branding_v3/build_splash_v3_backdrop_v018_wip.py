#!/usr/bin/env python3
"""Translate V018 into a native-size comparison plate and measure its fit."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/v018/source_backdrop_concept_ai_v018_20261015.png"
SOURCE_SHA256 = "93ddcafa8e4fcff6cf2e28b206f0a262cf7171aa149c25c9d4ce12b2220c52f0"
sys.path.insert(0, str(SOURCE.parent))
import build_splash_v3_visual_wip as common  # noqa: E402
import build_splash_v3_backdrop_v017_wip as metrics_helper  # noqa: E402

V006 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"
V015 = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v015_curated_320x224.png"
V016 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v016_320x224.png"
V017 = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v017_curated_320x224.png"
SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"
OUTPUT = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v018_curated_320x224.png"
BOARD = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v018_comparison_wip_v001_20261015.png"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v018_translation_report_20261015.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_indexed(image: Image.Image) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_v018_", dir=str(PROJECT_ROOT / "out")) as tmp:
        # The shared normalizer preserves opaque VDP black at index 0 only for
        # this canonical basename; the staging directory keeps that special case local.
        staged = Path(tmp) / "splash_backdrop_v3_320x224.png"
        image.save(staged, format="PNG", optimize=False)
        common.normalize_outputs([staged])
        if OUTPUT.exists():
            if sha256(OUTPUT) != sha256(staged):
                raise FileExistsError(f"Refusing to replace a different V018 output: {OUTPUT}")
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
    controls = (
        ("V006 BASELINE", V006),
        ("V015 DARK FIELD", V015),
        ("V016 OVAL FIELD", V016),
        ("V017 DENSE CONTROL", V017),
    )
    for label, path in controls:
        with Image.open(path) as source:
            panels.append((label, rendered(source.copy(), sgdk, forge)))
    panels.append(("V018 BROAD FACETS", rendered(candidate, sgdk, forge)))
    board = Image.new("RGB", (1600, 244), (3, 5, 18))
    draw = ImageDraw.Draw(board)
    for x, (label, panel) in zip((0, 320, 640, 960, 1280), panels):
        draw.text((x + 6, 3), label, fill=(174, 214, 255))
        board.paste(panel, (x, 20))
    if BOARD.exists():
        with Image.open(BOARD) as old:
            if old.convert("RGB").tobytes() != board.tobytes():
                raise FileExistsError(f"Refusing to replace a different V018 board: {BOARD}")
    else:
        BOARD.parent.mkdir(parents=True, exist_ok=True)
        board.save(BOARD, format="PNG", optimize=False)


def main() -> int:
    if not SOURCE.is_file() or sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("V018 source missing or hash changed")
    for path in (V006, V015, V016, V017, SGDK_MARK, FORGE_MARK):
        if not path.is_file():
            raise FileNotFoundError(path)
    if REPORT.exists():
        raise FileExistsError(f"Refusing to replace existing V018 report: {REPORT}")

    with Image.open(SOURCE) as source:
        if source.size != (1499, 1049) or source.mode != "RGB":
            raise ValueError(f"Unexpected V018 source format: {source.size}/{source.mode}")
        candidate = common.source_backdrop(SOURCE)
    save_indexed(candidate)
    asset = common.check_asset("backdrop", OUTPUT, 15, (320, 224))
    make_board(candidate)
    with Image.open(V017) as source:
        v017_tiles = metrics_helper.tile_metrics(source)
    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "splash_v3_backdrop_translation_preview",
        "candidate": "V018",
        "status": "lab_translation_needs_visual_and_semantic_review",
        "acceptance_status": "placeholder",
        "source_path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
        "source_sha256": SOURCE_SHA256,
        "translation_method": "Nearest 320x224 sampling and fixed 16-entry Mega Drive 9-bit RGB palette; no runtime-authored pixels or vignette.",
        "semantic_read": "One BG_B background plate, with broad central facets, asymmetric crystal clusters and an irregular broken lower shelf.",
        "asset": asset,
        "tile_metrics": metrics_helper.tile_metrics(candidate),
        "visual_metrics": metrics_helper.visual_metrics(candidate),
        "comparison_controls": {
            "V017_sha256": sha256(V017),
            "V017_unique_hv_tiles": v017_tiles["unique_tiles_hv"],
        },
        "comparison_board": BOARD.relative_to(PROJECT_ROOT).as_posix(),
        "promotion": {
            "eligible_for_res": False,
            "human_visual_approval": False,
            "template_promotion_authorized": False,
            "forja_v2_archive_authorized": False,
        },
        "limitations": [
            "Nearest-sampled palette translation is a WIP, not manual native 8x8 redrawing.",
            "The current WIP wordmark masks are not approved final typography.",
            "The report measures asset geometry only; ROM, animation, CRT, full VRAM, DMA and runtime remain unmeasured.",
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
