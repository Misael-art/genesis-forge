#!/usr/bin/env python3
"""Translate the V005 concept to a Mega Drive indexed WIP and comparison board.

This script only crops, snaps colors to the declared palette, and creates a
40-tile comparison from source-authored tiles. It does not draw game pixels or
write to res/; all outputs stay in rascunho/ and out/ until reviewed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/sources/source_backdrop_concept_ai_v005_20261014.png"
SOURCE_SHA256 = "bb32cf3c7e954b99d71fe71ed0197ba10685f1742847ccd1f75e91313016daea"
VISUAL_LAB = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_v005"
FULL_DETAIL = VISUAL_LAB / "full_detail/splash_backdrop_v3_320x224.png"
TILE_CONTROL = VISUAL_LAB / "40_tile_control/splash_backdrop_v3_320x224.png"
COMPARISON = PROJECT_ROOT / "out/branding_v3_visual_curation_20261014/v004_v005_backdrop_comparison.png"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_visual_translation_v005_report_20261014.json"
ASSET_ROOT = PROJECT_ROOT / "res/branding_v3"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_splash_v3_visual_wip as common  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hv_canonical(tile: bytes) -> bytes:
    rows = [tile[index * 8 : (index + 1) * 8] for index in range(8)]
    horizontal = b"".join(row[::-1] for row in rows)
    vertical = b"".join(rows[::-1])
    both = b"".join(row[::-1] for row in rows[::-1])
    return min(tile, horizontal, vertical, both)


def tile_metrics(image: Image.Image) -> dict[str, int]:
    columns, rows = image.width // 8, image.height // 8
    tiles = [common.tile_bytes(image, x, y) for y in range(rows) for x in range(columns)]
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": len(set(tiles)),
        "unique_hv_tiles": len({hv_canonical(tile) for tile in tiles}),
    }


def artifact_record(path: Path, image: Image.Image) -> dict[str, object]:
    return {
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "sha256": sha256(path),
        "size_px": [image.width, image.height],
        "tile_metrics": tile_metrics(image),
        "visible_colors": len({pixel for pixel in image.getdata() if pixel != 0}),
        "status": "wip_candidate_requires_human_visual_review",
    }


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    actual_hash = sha256(SOURCE)
    if actual_hash != SOURCE_SHA256:
        raise ValueError(f"V005 source hash mismatch: expected {SOURCE_SHA256}, got {actual_hash}")

    FULL_DETAIL.parent.mkdir(parents=True, exist_ok=True)
    TILE_CONTROL.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    full = common.source_backdrop(SOURCE)
    reduced, reduced_count, selected = common.reuse_authored_tiles(full, 40)
    full.save(FULL_DETAIL, format="PNG", optimize=False)
    reduced.save(TILE_CONTROL, format="PNG", optimize=False)
    # These directory-local basenames trigger the shared normalizer's opaque
    # black backdrop slot while preserving SGDK-compatible 4bpp indexed PNG.
    common.normalize_outputs([FULL_DETAIL, TILE_CONTROL])

    with Image.open(FULL_DETAIL) as image:
        full_record = artifact_record(FULL_DETAIL, image)
    with Image.open(TILE_CONTROL) as image:
        reduced_record = artifact_record(TILE_CONTROL, image)

    sgdk = Image.open(ASSET_ROOT / "splash_sgdk_wordmark_v3_224x48.png")
    forge = Image.open(ASSET_ROOT / "splash_forge_wordmark_v3_192x32.png")
    current = Image.open(ASSET_ROOT / "splash_backdrop_v3_320x224.png")
    current_preview = common.render_with_marks(current, sgdk, forge).convert("RGB")
    full_preview = common.render_with_marks(Image.open(FULL_DETAIL), sgdk, forge).convert("RGB")
    reduced_preview = common.render_with_marks(Image.open(TILE_CONTROL), sgdk, forge).convert("RGB")
    board = Image.new("RGB", (960, 224), (0, 0, 0))
    board.paste(current_preview, (0, 0))
    board.paste(full_preview, (320, 0))
    board.paste(reduced_preview, (640, 0))
    board.save(COMPARISON, format="PNG", optimize=False)

    report = {
        "schema_version": "1.0.0",
        "status": "development_wip_comparison_only",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": actual_hash,
            "kind": "ai_generated",
            "approval_status": "development_only",
            "source_canvas_px": list(Image.open(SOURCE).size),
        },
        "translation": {
            "target_px": [320, 224],
            "palette": "BG_PALETTE from build_splash_v3_visual_wip.py; black backdrop index 0; 15 visible colors max",
            "method": "center-fit crop, nearest sampling, snap to declared Mega Drive palette",
            "runtime_write": False,
            "human_visual_approval": False,
        },
        "candidates": {
            "full_detail": full_record,
            "40_tile_control": {**reduced_record, "selected_source_tile_count": reduced_count,
                                "selected_source_tile_indices": selected,
                                "purpose": "comparison control; not presumed superior"},
        },
        "comparison_board": {"path": COMPARISON.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(COMPARISON),
                             "order_left_to_right": ["active_v004", "v005_full_detail", "v005_40_tile_control"]},
        "review_points": [
            "Check the logo-safe zone and crystal silhouette at native 320x224.",
            "Check white highlight footprint and lower-center convergence against both wordmarks.",
            "Reject any repeated 40-tile control if it introduces checkerboard texture or fractured facets.",
            "If selected for runtime, rerun VDP residency, DMA/VBlank and exact-ROM BlastEm evidence.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "full_detail": full_record,
                      "40_tile_control": reduced_record, "comparison_board": report["comparison_board"],
                      "report": REPORT.relative_to(PROJECT_ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
