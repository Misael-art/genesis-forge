#!/usr/bin/env python3
"""Translate the V006 crystal backdrop concept to an isolated Mega Drive WIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/sources/source_backdrop_concept_ai_v006_20261014.png"
SOURCE_SHA256 = "f3e924c1580c8ead73b0df84b9b557cef69af45eeff4e311bf236b7b371829b8"
RUNTIME_CANDIDATE = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"
REVIEW_CANDIDATE = PROJECT_ROOT / "rascunho/visual_lab/splash_backdrop_v3_v006_320x224.png"
V005_RUNTIME = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v005_320x224.png"
SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v006_translation_20261014.json"
COMPARISON = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v005_vs_v006_320x224.png"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_splash_v3_visual_wip as common  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hv(tile: bytes) -> bytes:
    rows = [tile[index * 8 : (index + 1) * 8] for index in range(8)]
    variants = (
        tile,
        b"".join(row[::-1] for row in rows),
        b"".join(rows[::-1]),
        b"".join(row[::-1] for row in rows[::-1]),
    )
    return min(variants)


def tile_metrics(image: Image.Image) -> dict[str, int]:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--activate-runtime-candidate",
        action="store_true",
        help="Copy the translated WIP backdrop to its isolated res/ candidate path.",
    )
    args = parser.parse_args()

    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    actual_source_hash = sha256(SOURCE)
    if actual_source_hash != SOURCE_SHA256:
        raise ValueError(f"V006 source hash mismatch: {actual_source_hash}")

    for path in (V005_RUNTIME, SGDK_MARK, FORGE_MARK):
        if not path.is_file():
            raise FileNotFoundError(path)

    with tempfile.TemporaryDirectory(
        prefix="splash_v3_backdrop_v006_",
        dir=str(PROJECT_ROOT / "out"),
    ) as temp_name:
        staging = Path(temp_name) / "splash_backdrop_v3_320x224.png"
        translated = common.source_backdrop(SOURCE)
        translated.save(staging, format="PNG", optimize=False)
        # This canonical basename tells the shared normalizer that palette
        # index 0 is opaque VDP black for a full-screen background.
        common.normalize_outputs([staging])
        candidate_hash = sha256(staging)

        REVIEW_CANDIDATE.parent.mkdir(parents=True, exist_ok=True)
        if REVIEW_CANDIDATE.exists():
            if sha256(REVIEW_CANDIDATE) != candidate_hash:
                raise FileExistsError(
                    f"Refusing to replace an existing review candidate with a different hash: {REVIEW_CANDIDATE}"
                )
        else:
            shutil.copy2(staging, REVIEW_CANDIDATE)
        checked = common.check_asset("backdrop", REVIEW_CANDIDATE, 15, (320, 224))

        if args.activate_runtime_candidate:
            if RUNTIME_CANDIDATE.exists():
                if sha256(RUNTIME_CANDIDATE) != candidate_hash:
                    raise FileExistsError(
                        f"Refusing to replace an existing candidate with a different hash: {RUNTIME_CANDIDATE}"
                    )
            else:
                shutil.copy2(staging, RUNTIME_CANDIDATE)

        current = Image.open(V005_RUNTIME)
        candidate = Image.open(staging)
        sgdk = Image.open(SGDK_MARK)
        forge = Image.open(FORGE_MARK)
        source_rgb = Image.open(SOURCE).convert("RGB")
        source_view = ImageOps.fit(
            source_rgb,
            (320, 224),
            method=Image.Resampling.NEAREST,
            centering=(0.5, 0.5),
        )

        board = Image.new("RGB", (960, 224), (0, 0, 0))
        board.paste(common.render_with_marks(source_view, sgdk, forge).convert("RGB"), (0, 0))
        board.paste(common.render_with_marks(current, sgdk, forge).convert("RGB"), (320, 0))
        board.paste(common.render_with_marks(candidate, sgdk, forge).convert("RGB"), (640, 0))
        COMPARISON.parent.mkdir(parents=True, exist_ok=True)
        board.save(COMPARISON, format="PNG", optimize=False)

        report = {
            "schema_version": "1.0.0",
            "status": "development_wip_candidate_built",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "builder": "data/source_art/branding_v3/build_splash_v3_backdrop_v006_wip.py",
            "source": {
                "path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
                "sha256": actual_source_hash,
                "kind": "ai_generated",
                "edit_parent": {
                    "path": "data/source_art/branding_v3/sources/source_backdrop_concept_ai_v005_20261014.png",
                    "sha256": "bb32cf3c7e954b99d71fe71ed0197ba10685f1742847ccd1f75e91313016daea",
                },
            },
            "translation": {
                "target_px": [320, 224],
                "method": "center-fit crop, nearest sampling, declared 16-color palette, then shared 4bpp indexed-PNG normalizer",
                "palette_index0_rgb": [0, 0, 0],
                "runtime_res_write": bool(args.activate_runtime_candidate),
                "human_visual_approval": False,
            },
            "candidate": {
                **checked,
                **tile_metrics(candidate),
                "runtime_path": RUNTIME_CANDIDATE.relative_to(PROJECT_ROOT).as_posix(),
                "acceptance_status": "placeholder",
                "runtime_res_write": bool(args.activate_runtime_candidate),
            },
            "comparison": {
                "path": COMPARISON.relative_to(PROJECT_ROOT).as_posix(),
                "sha256": sha256(COMPARISON),
                "panel_order": ["v006_source_downsample", "v005_runtime", "v006_translated"],
                "wordmark_overlay": "current B WIP plates at (48,72) and (64,128); comparison only",
            },
            "curation_findings": [
                "Check that the dark center stays clear across contour, fill, FORGE, and sweep.",
                "Check lower convergence height and luminance against the FORGE plate.",
                "Check edge-crystal density, asymmetric balance, and white highlight footprint at 320x224.",
                "Compare V005 and V006 as WIP candidates; do not infer final quality from tile savings or a single still.",
            ],
            "promotion": {
                "final_visual_approval": False,
                "model_sheet_approved": False,
                "template_promotion_authorized": False,
                "forja_v2_archive_authorized": False,
                "future_review_required": True,
            },
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": report["status"],
                "candidate": report["candidate"],
                "comparison": report["comparison"],
                "report": REPORT.relative_to(PROJECT_ROOT).as_posix(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
