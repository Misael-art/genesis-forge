#!/usr/bin/env python3
"""Measure the V3 logo-safe region against the current WIP wordmark plates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAFE_BOX = (48, 72, 272, 160)
LUMA_REVIEW_THRESHOLD = 32
WORDMARKS = (
    ("SGDK", "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png", (48, 72)),
    ("FORGE", "res/branding_v3/splash_forge_wordmark_v3_192x32.png", (64, 128)),
)
CANDIDATES = (
    ("V006", "res/branding_v3/splash_backdrop_v3_v006_320x224.png"),
    ("V009", "rascunho/visual_lab/splash_v3_backdrop_v009_elite_320x224.png"),
    ("V010", "rascunho/visual_lab/splash_v3_backdrop_v010_elite_320x224.png"),
    ("V011", "rascunho/visual_lab/splash_v3_backdrop_v011_elite_320x224.png"),
    ("V012", "rascunho/visual_lab/splash_v3_backdrop_v012_elite_320x224.png"),
)
DEFAULT_OUTPUT = "out/logs/splash_v3_backdrop_safe_area_20261014.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def luma(rgb: tuple[int, int, int]) -> int:
    red, green, blue = rgb
    return (red * 3 + green * 6 + blue) // 10


def summarize(values: Iterable[int]) -> dict[str, float | int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        raise ValueError("Cannot summarize an empty pixel region")
    percentile_95 = ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)]
    return {
        "sample_count": len(ordered),
        "mean_luma_0_255": round(sum(ordered) / len(ordered), 2),
        "p95_luma_0_255": percentile_95,
        "max_luma_0_255": ordered[-1],
        "share_above_review_threshold": round(
            sum(value > LUMA_REVIEW_THRESHOLD for value in ordered) / len(ordered), 4
        ),
    }


def rank_logo_safe_area(candidates: list[dict]) -> list[dict]:
    return sorted(candidates, key=lambda item: (
        item["background_under_wordmark_luma"]["share_above_review_threshold"],
        item["background_under_wordmark_luma"]["mean_luma_0_255"],
        item["background_under_wordmark_luma"]["p95_luma_0_255"],
        item["background_under_wordmark_luma"]["max_luma_0_255"],
    ))


def canonical_hv(tile: bytes, pixel_bytes: int = 1) -> bytes:
    row_bytes = 8 * pixel_bytes
    rows = [tile[row * row_bytes : (row + 1) * row_bytes] for row in range(8)]
    pixels = [
        [row[x * pixel_bytes : (x + 1) * pixel_bytes] for x in range(8)]
        for row in rows
    ]
    variants = []
    for flip_y in (False, True):
        for flip_x in (False, True):
            y_order = range(7, -1, -1) if flip_y else range(8)
            encoded_rows = []
            for y in y_order:
                x_order = range(7, -1, -1) if flip_x else range(8)
                encoded_rows.append(b"".join(pixels[y][x] for x in x_order))
            variants.append(b"".join(encoded_rows))
    return min(variants)


def tile_metrics(image: Image.Image) -> dict[str, int]:
    indexed = image.convert("P")
    values = list(indexed.get_flattened_data())
    width, height = indexed.size
    tiles = []
    for tile_y in range(height // 8):
        for tile_x in range(width // 8):
            tile = bytearray()
            for y in range(tile_y * 8, tile_y * 8 + 8):
                start = y * width + tile_x * 8
                tile.extend(values[start : start + 8])
            tiles.append(bytes(tile))
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": len(set(tiles)),
        "unique_hv_tiles": len({canonical_hv(tile) for tile in tiles}),
        "visible_palette_indices": len({value for value in values if value != 0}),
    }


def wordmark_mask(project_root: Path) -> Image.Image:
    mask = Image.new("L", (320, 224), 0)
    for _, relative, position in WORDMARKS:
        with Image.open(project_root / relative) as source:
            alpha = source.convert("RGBA").getchannel("A")
        mask.paste(alpha, position)
    return mask


def measure_candidate(project_root: Path, version: str, relative: str,
                      mask: Image.Image) -> dict:
    path = project_root / relative
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as source:
        if source.size != (320, 224):
            raise ValueError(f"{relative}: expected 320x224, found {source.size}")
        image = source.convert("RGB")
        indexed_for_tiles = source.copy()

    box_values: list[int] = []
    glyph_values: list[int] = []
    for y in range(SAFE_BOX[1], SAFE_BOX[3]):
        for x in range(SAFE_BOX[0], SAFE_BOX[2]):
            value = luma(image.getpixel((x, y)))
            box_values.append(value)
            if mask.getpixel((x, y)) > 0:
                glyph_values.append(value)

    return {
        "version": version,
        "path": Path(relative).as_posix(),
        "sha256": sha256(path),
        "safe_box_xyxy": list(SAFE_BOX),
        "safe_box_luma": summarize(box_values),
        "background_under_wordmark_luma": summarize(glyph_values),
        "tiles": tile_metrics(indexed_for_tiles),
    }


def self_check() -> dict:
    samples = summarize([0, 0, 64, 128])
    if samples["mean_luma_0_255"] != 48.0:
        raise AssertionError("mean luma fixture failed")
    if samples["p95_luma_0_255"] != 128:
        raise AssertionError("p95 fixture failed")
    if samples["share_above_review_threshold"] != 0.5:
        raise AssertionError("threshold share fixture failed")
    pixels = bytes(range(64))
    flipped = Image.frombytes("L", (8, 8), pixels).transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes()
    if canonical_hv(pixels) != canonical_hv(flipped):
        raise AssertionError("H/V canonical tile fixture failed")
    ranking_fixture = [
        {
            "version": "V011",
            "background_under_wordmark_luma": {
                "share_above_review_threshold": 0.0113,
                "mean_luma_0_255": 4.78,
                "p95_luma_0_255": 3,
                "max_luma_0_255": 238,
            },
        },
        {
            "version": "V012",
            "background_under_wordmark_luma": {
                "share_above_review_threshold": 0.0,
                "mean_luma_0_255": 3.0,
                "p95_luma_0_255": 3,
                "max_luma_0_255": 3,
            },
        },
    ]
    if [item["version"] for item in rank_logo_safe_area(ranking_fixture)] != ["V012", "V011"]:
        raise AssertionError("logo-safe-area candidate ranking fixture failed")
    return {"status": "passed", "fixtures_passed": 5, "fixtures_total": 5}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--out", default=DEFAULT_OUTPUT)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        print(json.dumps(self_check(), indent=2))
        return 0

    project_root = args.project_root.resolve()
    mask = wordmark_mask(project_root)
    results = [
        measure_candidate(project_root, version, path, mask)
        for version, path in CANDIDATES
    ]
    baseline = next(item for item in results if item["version"] == "V006")
    baseline_glyph = baseline["background_under_wordmark_luma"]
    for item in results:
        current = item["background_under_wordmark_luma"]
        item["delta_from_v006_under_wordmark_mean_luma"] = round(
            current["mean_luma_0_255"] - baseline_glyph["mean_luma_0_255"], 2
        )

    logo_safe_candidates = rank_logo_safe_area(
        [item for item in results if item["version"] != "V006"]
    )
    strongest_logo_safe_candidate = logo_safe_candidates[0]["version"]

    report = {
        "schema_version": "1.0.0",
        "report_id": "splash_v3_backdrop_safe_area_20261014",
        "status": "measured_visual_wip_no_selection",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tool": {
            "path": Path(__file__).resolve().relative_to(project_root).as_posix(),
            "sha256": sha256(Path(__file__).resolve()),
            "self_check": self_check(),
        },
        "method": {
            "canvas_px": [320, 224],
            "safe_box_xyxy": list(SAFE_BOX),
            "wordmark_masks": [
                {"name": name, "path": path, "position_xy": list(position)}
                for name, path, position in WORDMARKS
            ],
            "luma_formula": "(3*R + 6*G + B) // 10",
            "review_threshold": LUMA_REVIEW_THRESHOLD,
            "threshold_is_diagnostic_only": True,
            "tile_flips": ["none", "H", "V", "HV"],
        },
        "candidates": results,
        "decision": {
            "runtime_backdrop_unchanged": "V006",
            "V010_status": "comparison_only_safe_area_review_needed",
            "V011_status": "comparison_only_residual_bright_pixels_under_wordmark",
            "V012_status": "strongest_measured_logo_safe_area_wip_candidate" if strongest_logo_safe_candidate == "V012" else "comparison_only",
            "strongest_measured_logo_safe_area_wip_candidate": strongest_logo_safe_candidate,
            "ranking_by_under_wordmark": [item["version"] for item in logo_safe_candidates],
            "human_visual_approval": False,
            "rom_validation": False,
            "promotion_authorized": False,
        },
    }
    output = project_root / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": args.out,
                      "sha256": sha256(output),
                      "strongest_logo_safe_candidate": strongest_logo_safe_candidate,
                      "ranking_by_under_wordmark": [item["version"] for item in logo_safe_candidates]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
