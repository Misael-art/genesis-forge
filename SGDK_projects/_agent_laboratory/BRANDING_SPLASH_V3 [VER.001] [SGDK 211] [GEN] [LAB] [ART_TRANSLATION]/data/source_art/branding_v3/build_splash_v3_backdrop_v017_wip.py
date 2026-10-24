#!/usr/bin/env python3
"""Translate the V017 concept to a native-size, placeholder-only BG plate.

The builder samples the source on the 320x224 viewport and maps it to the
existing 16-color Mega Drive palette. It does not paint pixels or claim final
native authorship; the result is a comparison WIP and stays outside /res.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/v017/source_backdrop_concept_ai_v017_20261015.png"
SOURCE_SHA256 = "4bb6bc3cf60fff57dc396eafd9d21bdee86b03349800ba6e9c40eec8ebc38033"
KNOWN_FAILED_OUTPUT_SHA256 = "4b5f1a73f28bc41ed5649d0cf553a40d3de8886bb14ed77ba36f66c88bc7827e"
sys.path.insert(0, str(SOURCE.parent))
import build_splash_v3_visual_wip as common  # noqa: E402

V006 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"
V015 = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v015_curated_320x224.png"
V016 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v016_320x224.png"
SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"

OUTPUT = PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v017_curated_320x224.png"
BOARD = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v017_comparison_wip_v001_20261015.png"
REPORT = PROJECT_ROOT / "out/logs/splash_v3_backdrop_v017_translation_report_20261015.json"
MARKS = ((SGDK_MARK, (48, 72)), (FORGE_MARK, (64, 128)))
SAFE_BOX = (48, 72, 272, 160)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hv_canonical(tile: bytes) -> bytes:
    rows = [tile[i * 8 : (i + 1) * 8] for i in range(8)]
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
        "unique_tiles_exact": len(set(tiles)),
        "unique_tiles_hv": len({hv_canonical(tile) for tile in tiles}),
    }


def luma(rgb: tuple[int, int, int]) -> int:
    return (rgb[0] * 3 + rgb[1] * 6 + rgb[2]) // 10


def visual_metrics(image: Image.Image) -> dict[str, object]:
    palette = image.getpalette() or []

    def color(index: int) -> tuple[int, int, int]:
        return tuple(palette[index * 3 : index * 3 + 3])  # type: ignore[return-value]

    left, top, right, bottom = SAFE_BOX
    safe_values = [
        luma(color(image.getpixel((x, y))))
        for y in range(top, bottom)
        for x in range(left, right)
    ]
    word_values: list[int] = []
    for mark_path, (mark_x, mark_y) in MARKS:
        with Image.open(mark_path) as mark_image:
            alpha = mark_image.convert("RGBA").getchannel("A")
        for y in range(alpha.height):
            for x in range(alpha.width):
                if alpha.getpixel((x, y)) > 0:
                    word_values.append(luma(color(image.getpixel((mark_x + x, mark_y + y)))))
    safe_sorted = sorted(safe_values)
    word_sorted = sorted(word_values)

    def stats(values: list[int]) -> dict[str, object]:
        p95 = values[round((len(values) - 1) * 0.95)]
        return {
            "mean_luma_0_255": round(sum(values) / len(values), 2),
            "p95_luma_0_255": p95,
            "max_luma_0_255": max(values),
            "share_over_32": round(sum(value > 32 for value in values) / len(values), 4),
        }

    lower_max_bright_run = 0
    for y in range(176, image.height):
        run = 0
        row_max = 0
        for x in range(image.width):
            if luma(color(image.getpixel((x, y)))) >= 70:
                run += 1
                row_max = max(row_max, run)
            else:
                run = 0
        lower_max_bright_run = max(lower_max_bright_run, row_max)
    return {
        "safe_box_xyxy": list(SAFE_BOX),
        "safe_box_background": stats(safe_values),
        "wordmark_background": stats(word_sorted),
        "longest_lower_half_run_luma_gte_70_px": lower_max_bright_run,
        "used_palette_indices": sorted(set(image.getdata())),
        "visible_colors_used": len(set(image.getdata()) - {0}),
    }


def save_indexed(image: Image.Image) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="splash_v3_v017_", dir=str(PROJECT_ROOT / "out")) as tmp:
        # The shared normalizer preserves opaque VDP black at slot zero only
        # for this canonical basename; use it inside the isolated staging dir.
        staged = Path(tmp) / "splash_backdrop_v3_320x224.png"
        image.save(staged, format="PNG", optimize=False)
        common.normalize_outputs([staged])
        if OUTPUT.exists():
            current_hash = sha256(OUTPUT)
            if current_hash == KNOWN_FAILED_OUTPUT_SHA256:
                shutil.copy2(staged, OUTPUT)
            elif current_hash != sha256(staged):
                raise FileExistsError(f"Refusing to replace a different V017 output: {OUTPUT}")
        else:
            shutil.copy2(staged, OUTPUT)


def render(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    return common.render_with_marks(backdrop, sgdk, forge).convert("RGB")


def build_board(backdrop: Image.Image) -> None:
    with Image.open(SGDK_MARK) as image:
        sgdk = image.convert("RGBA")
    with Image.open(FORGE_MARK) as image:
        forge = image.convert("RGBA")
    panels: list[tuple[str, Image.Image]] = []
    for label, path in (
        ("V006 BASELINE", V006),
        ("V015 DARK FIELD", V015),
        ("V016 OVAL FIELD", V016),
    ):
        with Image.open(path) as source:
            panels.append((label, render(source.copy(), sgdk, forge)))
    panels.append(("V017 FACETS / BROKEN FLOOR", render(backdrop, sgdk, forge)))
    board = Image.new("RGB", (1280, 244), (3, 5, 18))
    draw = ImageDraw.Draw(board)
    for x, (label, panel) in zip((0, 320, 640, 960), panels):
        draw.text((x + 6, 3), label, fill=(174, 214, 255))
        board.paste(panel, (x, 20))
    if BOARD.exists():
        with Image.open(BOARD) as old:
            if old.convert("RGB").tobytes() != board.tobytes():
                raise FileExistsError(f"Refusing to replace a different V017 board: {BOARD}")
    else:
        BOARD.parent.mkdir(parents=True, exist_ok=True)
        board.save(BOARD, format="PNG", optimize=False)


def main() -> int:
    if not SOURCE.is_file() or sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("V017 source missing or hash changed")
    for path in (V006, V015, V016, SGDK_MARK, FORGE_MARK):
        if not path.is_file():
            raise FileNotFoundError(path)
    if REPORT.exists():
        raise FileExistsError(f"Refusing to replace existing V017 report: {REPORT}")

    with Image.open(SOURCE) as source:
        if source.size != (1500, 1049) or source.mode != "RGB":
            raise ValueError(f"Unexpected V017 source format: {source.size}/{source.mode}")
        candidate = common.source_backdrop(SOURCE)
    save_indexed(candidate)
    asset = common.check_asset("backdrop", OUTPUT, 15, (320, 224))
    build_board(candidate)

    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "splash_v3_backdrop_translation_preview",
        "candidate": "V017",
        "status": "lab_translation_needs_visual_and_semantic_review",
        "acceptance_status": "placeholder",
        "source_path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
        "source_sha256": SOURCE_SHA256,
        "translation_method": "Nearest 320x224 sampling with fixed 16-entry Mega Drive 9-bit RGB palette; no vignette, logo, or runtime-authored pixels.",
        "semantic_read": "One BG_B background plate with a low-contrast faceted title center and broken crystalline lower field; generated concept still needs native-size human review.",
        "asset": asset,
        "tile_metrics": tile_metrics(candidate),
        "visual_metrics": visual_metrics(candidate),
        "comparison_board": BOARD.relative_to(PROJECT_ROOT).as_posix(),
        "promotion": {
            "eligible_for_res": False,
            "human_visual_approval": False,
            "template_promotion_authorized": False,
            "forja_v2_archive_authorized": False,
        },
        "limitations": [
            "This is nearest-sampled palette translation, not manual native 8x8 redrawing.",
            "Only a static backdrop translation is reviewed; no ROM, animation, CRT, VRAM, DMA, or runtime claim is made.",
            "The current WIP wordmark masks are not approved final typography.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "asset_sha256": asset["sha256"],
        "tile_metrics": report["tile_metrics"],
        "visual_metrics": report["visual_metrics"],
        "board": report["comparison_board"],
        "report": REPORT.relative_to(PROJECT_ROOT).as_posix(),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
