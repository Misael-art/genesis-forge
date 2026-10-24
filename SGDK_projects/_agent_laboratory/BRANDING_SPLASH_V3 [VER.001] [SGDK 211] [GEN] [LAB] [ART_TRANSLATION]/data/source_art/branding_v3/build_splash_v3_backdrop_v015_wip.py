#!/usr/bin/env python3
"""Build source-fit, basic and palette-curated V015 diagnostic translations.

Every output stays in visual_lab/out. Nothing from this script is runtime art.
The curated route protects the logo-safe field and keeps the source palette
roles; native manual redraw and user review remain required.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT_ROOT / "data/source_art/branding_v3/v015/source_backdrop_concept_ai_v015_20261015.png"
SOURCE_SHA256 = "87293cf5275564733d27d5a166f1071f04bb2b447257a07c5a3f0c6b9c0c9188"
sys.path.insert(0, str(SOURCE.parent))
import build_splash_v3_visual_wip as common  # noqa: E402

SGDK_MARK = PROJECT_ROOT / "res/branding_v3/splash_sgdk_wordmark_v3_224x48.png"
FORGE_MARK = PROJECT_ROOT / "res/branding_v3/splash_forge_wordmark_v3_192x32.png"
V006 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v006_320x224.png"
V014 = PROJECT_ROOT / "res/branding_v3/splash_backdrop_v3_v014_320x224.png"

OUTPUTS = {
    "basic": PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v015_basic_320x224.png",
    "elite": PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v015_curated_320x224.png",
    "board": PROJECT_ROOT / "rascunho/visual_lab/splash_v3_backdrop_v015_comparison_wip_v001_20261015.png",
    "palette_strip": PROJECT_ROOT / "out/logs/splash_v3_backdrop_v015_palette_strip_20261015.png",
    "tileset_sheet": PROJECT_ROOT / "out/logs/splash_v3_backdrop_v015_tileset_sheet_20261015.png",
    "report": PROJECT_ROOT / "out/logs/splash_v3_backdrop_v015_translation_report_20261015.json",
}

SAFE_RECT = (45, 67, 275, 166)  # 14..86% x, 30..74% y at 320x224.
PALETTE_ROLES = {
    0: "VDP backdrop black",
    1: "deepest navy",
    2: "navy shadow",
    3: "indigo shadow",
    4: "crystal structural shadow",
    5: "deep cobalt",
    6: "cobalt facet",
    7: "blue facet",
    8: "bright blue facet",
    9: "cyan-blue facet",
    10: "cyan light",
    11: "cyan facet",
    12: "ice-cyan facet",
    13: "ice-blue highlight",
    14: "bright ice highlight",
    15: "sparse pinpoint white",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snap_color(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    levels = (0, 34, 68, 102, 136, 170, 204, 238)
    return tuple(min(levels, key=lambda value: (abs(value - channel), value)) for channel in rgb)


def make_basic(source: Image.Image) -> Image.Image:
    """Blind 15-color median-cut control, snapped to the Mega Drive grid."""
    quantized = source.quantize(colors=15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    raw_palette = quantized.getpalette() or []
    original = [tuple(raw_palette[i * 3 : i * 3 + 3]) for i in range(15)]
    visible = sorted(
        {snap_color(color) for color in original if snap_color(color) != (0, 0, 0)},
        key=lambda color: (color[0] * 3 + color[1] * 6 + color[2], color[2], color[1], color[0]),
    )
    palette = [common.VDP_BACKDROP_BLACK] + visible[:15]
    mapping: dict[tuple[int, int, int], int] = {}
    for color in original:
        snapped = snap_color(color)
        mapping[color] = 0 if snapped == (0, 0, 0) else 1 + palette[1:].index(snapped)
    pixels = [mapping[original[index]] for index in quantized.get_flattened_data()]
    return common.make_indexed((320, 224), pixels, palette)


def make_curated(source: Image.Image) -> Image.Image:
    """Fixed semantic palette, no dithering, dark-only protected logo field."""
    fitted = ImageOps.fit(source.convert("RGB"), (320, 224), method=Image.Resampling.NEAREST, centering=(0.5, 0.5))
    left, top, right, bottom = SAFE_RECT
    pixels: list[int] = []
    for y in range(224):
        for x in range(320):
            rgb = fitted.getpixel((x, y))
            if max(rgb) <= 22:
                pixels.append(0)
                continue
            allowed = range(1, 6) if left <= x < right and top <= y < bottom else range(1, 16)
            index = min(
                allowed,
                key=lambda i: sum((rgb[channel] - common.BG_PALETTE[i][channel]) ** 2 for channel in range(3)),
            )
            pixels.append(index)
    return common.make_indexed((320, 224), pixels, common.BG_PALETTE)


def tile_bytes(image: Image.Image, tile_x: int, tile_y: int) -> bytes:
    return common.tile_bytes(image, tile_x, tile_y)


def canonical_hv(tile: bytes) -> bytes:
    rows = [tile[index * 8 : (index + 1) * 8] for index in range(8)]
    return min((tile, b"".join(row[::-1] for row in rows), b"".join(rows[::-1]), b"".join(row[::-1] for row in rows[::-1])))


def tile_metrics(image: Image.Image) -> dict[str, int]:
    tiles = [tile_bytes(image, x, y) for y in range(28) for x in range(40)]
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": len(set(tiles)),
        "unique_tiles_with_hv_flips": len({canonical_hv(tile) for tile in tiles}),
    }


def save_indexed(image: Image.Image, path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"splash_v3_v015_{label}_", dir=str(PROJECT_ROOT / "out")) as tmp:
        stage_dir = Path(tmp) / "stage"
        stage_dir.mkdir()
        stage = stage_dir / "splash_backdrop_v3_320x224.png"
        image.save(stage, format="PNG", optimize=False)
        common.normalize_outputs([stage])
        if path.exists():
            if sha256(path) != sha256(stage):
                raise FileExistsError(f"Refusing to replace different V015 output: {path}")
        else:
            shutil.copy2(stage, path)


def render(backdrop: Image.Image, sgdk: Image.Image, forge: Image.Image) -> Image.Image:
    return common.render_with_marks(backdrop, sgdk, forge).convert("RGB")


def save_review_image(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with Image.open(path) as existing:
            current = existing.convert("RGBA")
        candidate = image.convert("RGBA")
        if current.size != candidate.size or ImageChops.difference(current, candidate).getbbox():
            raise FileExistsError(f"Refusing to replace a different V015 review image: {path}")
        return
    image.save(path, format="PNG", optimize=False)


def make_palette_strip(path: Path) -> None:
    swatch_w, swatch_h, label_h = 32, 32, 24
    image = Image.new("RGB", (16 * swatch_w, swatch_h + label_h), (8, 12, 24))
    draw = ImageDraw.Draw(image)
    for index, color in enumerate(common.BG_PALETTE):
        x = index * swatch_w
        draw.rectangle((x, 0, x + swatch_w - 1, swatch_h - 1), fill=color)
        draw.text((x + 10, swatch_h + 4), f"{index:02}", fill=(220, 230, 245))
    save_review_image(image, path)


def make_tileset_sheet(image: Image.Image, path: Path) -> dict[str, int]:
    columns = 20
    scale = 3
    cell = 8 * scale
    tiles: dict[bytes, bytes] = {}
    for y in range(28):
        for x in range(40):
            original = tile_bytes(image, x, y)
            tiles.setdefault(canonical_hv(original), canonical_hv(original))
    ordered = sorted(tiles)
    rows = (len(ordered) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell, rows * cell), (3, 5, 18))
    for index, tile in enumerate(ordered):
        tile_image = Image.new("P", (8, 8))
        tile_image.putdata(tile)
        tile_image.putpalette(image.getpalette() or [])
        rgb = tile_image.convert("RGB").resize((cell, cell), Image.Resampling.NEAREST)
        sheet.paste(rgb, ((index % columns) * cell, (index // columns) * cell))
    save_review_image(sheet, path)
    return {"canonical_hv_tile_count": len(ordered), "columns": columns, "pixel_scale": scale}


def checked_asset(label: str, path: Path) -> dict[str, object]:
    return common.check_asset(label, path, 15, (320, 224))


def main() -> int:
    if not SOURCE.is_file() or sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("V015 source missing or hash changed")
    for path in (SGDK_MARK, FORGE_MARK, V006, V014):
        if not path.is_file():
            raise FileNotFoundError(path)
    if OUTPUTS["report"].exists():
        raise FileExistsError(f"Refusing to replace existing V015 report: {OUTPUTS['report']}")

    with Image.open(SOURCE) as source_file:
        source_fit = ImageOps.fit(source_file.convert("RGB"), (320, 224), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        original_for_curated = source_file.copy()
    basic = make_basic(source_fit)
    curated = make_curated(original_for_curated)
    save_indexed(basic, OUTPUTS["basic"], "basic")
    save_indexed(curated, OUTPUTS["elite"], "curated")

    basic_checked = checked_asset("backdrop", OUTPUTS["basic"])
    curated_checked = checked_asset("backdrop", OUTPUTS["elite"])
    with Image.open(SGDK_MARK) as image:
        sgdk = image.convert("RGBA")
    with Image.open(FORGE_MARK) as image:
        forge = image.convert("RGBA")
    with Image.open(OUTPUTS["basic"]) as image:
        basic_image = image.copy()
    with Image.open(OUTPUTS["elite"]) as image:
        curated_image = image.copy()
    with Image.open(V006) as image:
        v006 = image.copy()
    with Image.open(V014) as image:
        v014 = image.copy()

    panels = [
        ("SOURCE FIT", render(source_fit, sgdk, forge)),
        ("BASIC CONTROL", render(basic_image, sgdk, forge)),
        ("CURATED PALETTE", render(curated_image, sgdk, forge)),
        ("V006 BASELINE", render(v006, sgdk, forge)),
        ("V014 CONTROL", render(v014, sgdk, forge)),
    ]
    board = Image.new("RGB", (1600, 244), (3, 5, 18))
    draw = ImageDraw.Draw(board)
    for x, (label, panel) in zip((0, 320, 640, 960, 1280), panels):
        draw.text((x + 8, 3), label, fill=(174, 214, 255))
        board.paste(panel, (x, 20))
    OUTPUTS["board"].parent.mkdir(parents=True, exist_ok=True)
    save_review_image(board, OUTPUTS["board"])

    make_palette_strip(OUTPUTS["palette_strip"])
    tile_sheet_info = make_tileset_sheet(curated_image, OUTPUTS["tileset_sheet"])
    left, top, right, bottom = SAFE_RECT
    safe_indices = [curated_image.getpixel((x, y)) for y in range(top, bottom) for x in range(left, right)]
    usage_counts = Counter(curated_image.get_flattened_data())
    usage = {str(index): usage_counts.get(index, 0) for index in range(16)}
    report = {
        "schema_version": "1.0.0",
        "status": "lab_translation_needs_visual_and_semantic_review",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "path": SOURCE.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": SOURCE_SHA256,
            "canvas_px": [1500, 1049],
            "source_class": "single_frame_background_concept",
            "semantic_parse": "doc/art/splash_v3_v015_source_semantics_manifest.json",
            "automatic_inference": {
                "path": "out/logs/splash_v3_v015_source_inference_20261015/derived_structure_ir.json",
                "layout_type": "stage_board",
                "alignment_audit": "failed",
                "handling": "Not used for decomposition: the heuristic invents sky/ground cuts and a mockup_preview absent from the source."
            },
        },
        "translation": {
            "target_px": [320, 224],
            "hardware_grid": "8x8",
            "basic_method": "LANCZOS fit, median-cut 15-color control, no dithering, snap colors to 9-bit VDP grid",
            "curated_method": "nearest source sampling, fixed BG palette with explicit material roles, no dithering, darkest five palette colors inside x=14..86% / y=30..74% logo-safe rectangle",
            "curated_is_manual_native_redraw": False,
            "manual_native_authoring_complete": False,
            "runtime_candidate": False,
            "production_allowed": False,
        },
        "palette_plan": {
            "palette_role_count": 15,
            "index_0": "VDP backdrop black",
            "visible_roles": PALETTE_ROLES,
            "dithering": "none; retain hard facet edges and avoid texture noise",
            "layer_plan": "single BG_B energy plate; wordmarks stay separate BG_A assets; particles/sweep stay sprites",
            "logo_safe_rect_px": list(SAFE_RECT),
            "logo_safe_rect_policy": "indices 1..5 only; no cyan or ice highlights",
        },
        "candidates": {
            "basic": {**basic_checked, **tile_metrics(basic_image)},
            "curated": {**curated_checked, **tile_metrics(curated_image)},
        },
        "safe_area": {
            "rect_px": list(SAFE_RECT),
            "pixels": len(safe_indices),
            "bright_indices_6_to_15": sum(index >= 6 for index in safe_indices),
            "mean_palette_index": round(sum(safe_indices) / max(1, len(safe_indices)), 4),
        },
        "palette_usage_pixels": usage,
        "structural_review": {
            "tileset_sheet": OUTPUTS["tileset_sheet"].relative_to(PROJECT_ROOT).as_posix(),
            "tileset_sheet_sha256": sha256(OUTPUTS["tileset_sheet"]),
            "palette_strip": OUTPUTS["palette_strip"].relative_to(PROJECT_ROOT).as_posix(),
            "palette_strip_sha256": sha256(OUTPUTS["palette_strip"]),
            **tile_sheet_info,
            "per_tile_palette_conflicts": "not_applicable_single_palette_plane",
            "tile_cap_applied": False,
        },
        "comparison": {
            "path": OUTPUTS["board"].relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256(OUTPUTS["board"]),
            "panels": [label for label, _ in panels],
            "wordmark_overlay": "current SGDK/FORGE WIP plates for composition review only",
            "v006_control": {"path": V006.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(V006), "tiles": tile_metrics(v006)},
            "v014_control": {"path": V014.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256(V014), "tiles": tile_metrics(v014)},
        },
        "findings_to_review": [
            "Does the single-plane reading hold after manual review despite the automated stage_board false positive?",
            "Does V015 preserve its asymmetric crystal silhouette at native 320x224 without cluttering the marks?",
            "Is the protected logo-safe field visually seamless, or does its palette clamp read as an artificial box?",
            "Does the reduced lower reflection still compete with FORGE or the convergence glint?",
            "Compare tile reuse and visual hierarchy with V006 and V014; no tile cap was applied.",
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
    OUTPUTS["report"].write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "board": OUTPUTS["board"].relative_to(PROJECT_ROOT).as_posix(), "report": OUTPUTS["report"].relative_to(PROJECT_ROOT).as_posix(), "curated_tiles": report["candidates"]["curated"]["unique_tiles_with_hv_flips"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
