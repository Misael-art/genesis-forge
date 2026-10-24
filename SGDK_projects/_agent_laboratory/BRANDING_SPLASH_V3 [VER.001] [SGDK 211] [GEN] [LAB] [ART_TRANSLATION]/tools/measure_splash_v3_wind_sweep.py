#!/usr/bin/env python3
"""Measure every frame of the Splash V3 wind-sweep choreography against H40."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[2]
SIMULATOR_PATH = (
    WORKSPACE_ROOT
    / "tools"
    / "sgdk_wrapper"
    / ".agent"
    / "scripts"
    / "vdp_scanline_simulator.py"
)
DEFAULT_CONTRACT = (
    PROJECT_ROOT
    / "doc"
    / "curation"
    / "splash_v3_wind_dispersal_contract_v005_20261016.json"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "out" / "logs" / "splash_v3_wind_dispersal_scanline_v005_20261016.json"
)
CORE_BIRTH_FRAMES = (0, 5, 6, 4)
NOISE_TABLE_PX = (-1, -1, 0, 1, 1, 0, -1, -1,
                  0, 1, 1, 0, 0, -1, 0, 1)


def trunc_div(numerator: int, denominator: int) -> int:
    if numerator < 0:
        return -((-numerator) // denominator)
    return numerator // denominator


def load_simulator() -> Any:
    spec = importlib.util.spec_from_file_location("vdp_scanline_simulator", SIMULATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load simulator: {SIMULATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lerp_q8(start: int, end: int, t_q8: int) -> int:
    return start + trunc_div((end - start) * t_q8, 256)


def ease_q8(t_q8: int) -> int:
    return (t_q8 * t_q8 * (768 - (2 * t_q8))) >> 16


def bezier_q8(points: list[int], t_q8: int) -> int:
    a = lerp_q8(points[0], points[1], t_q8)
    b = lerp_q8(points[1], points[2], t_q8)
    c = lerp_q8(points[2], points[3], t_q8)
    d = lerp_q8(a, b, t_q8)
    e = lerp_q8(b, c, t_q8)
    return lerp_q8(d, e, t_q8)


def position(spark: dict[str, Any], elapsed: int) -> tuple[int, int]:
    life = int(spark["lifetime_frames"])
    t_q8 = (elapsed * 256) // max(1, life - 1)
    t_q8 = ease_q8(t_q8)
    points = spark["control_points_px"]
    x = bezier_q8([int(point[0]) for point in points], t_q8)
    y = bezier_q8([int(point[1]) for point in points], t_q8)

    if elapsed >= 2 and life - elapsed > 2:
        noise_step = elapsed // int(spark["noise_period_frames"])
        noise_index = (noise_step + int(spark["noise_phase"])) & 15
        amplitude = int(spark.get("noise_amplitude_px", 1))
        x += NOISE_TABLE_PX[(noise_index + 6) & 15] * amplitude
        y += NOISE_TABLE_PX[noise_index] * amplitude
    return x, y


def core_frame(spark: dict[str, Any], elapsed: int) -> int | None:
    remaining = int(spark["lifetime_frames"]) - elapsed
    if elapsed < len(CORE_BIRTH_FRAMES):
        return CORE_BIRTH_FRAMES[elapsed]
    if remaining == 4:
        return 6
    if remaining == 3:
        return 5
    if remaining == 2:
        return 0
    if remaining <= 1:
        return None

    flicker = spark["flicker"]
    period = int(flicker["period_frames"])
    if period and ((elapsed + int(flicker["phase"])) % period) == 0:
        return 1
    return 4


def trail_frame(spark: dict[str, Any], elapsed: int, delta_y: int) -> int | None:
    remaining = int(spark["lifetime_frames"]) - elapsed
    if elapsed < 3 or remaining <= 2:
        return None
    if remaining == 4:
        return 5
    if remaining == 3:
        return 0
    if delta_y < -1:
        return 3
    if delta_y > 1:
        return 4
    return 2


def particle_instances(spark: dict[str, Any], frame: int) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    start = int(spark["start_frame"])
    elapsed = frame - start
    life = int(spark["lifetime_frames"])
    if elapsed < 0 or elapsed >= life:
        return [], None

    x, y = position(spark, elapsed)
    previous_elapsed = max(0, elapsed - 2)
    previous_x, previous_y = position(spark, previous_elapsed)
    delta_x = max(1, x - previous_x)
    delta_y = y - previous_y
    core_idx = core_frame(spark, elapsed)
    details = {"id": spark["id"], "elapsed": elapsed, "x": x, "y": y,
               "core_frame": core_idx, "delta_y_px_per_two_frames": delta_y}
    sprites: list[dict[str, Any]] = []

    if core_idx is not None:
        sprites.append({"name": f"{spark['id']}_core", "x": x, "y": y,
                        "w": 8, "h": 8, "sprite_links": 1})

    trail_idx = trail_frame(spark, elapsed, delta_y)
    if trail_idx is not None:
        lag = int(spark["trail_lag_px"])
        trail_y = y - trunc_div(delta_y * lag, delta_x)
        trail_y = min(y + 2, max(y - 2, trail_y))
        trail_x = x - lag
        sprites.append({"name": f"{spark['id']}_trail", "x": trail_x, "y": trail_y,
                        "w": 8, "h": 8, "sprite_links": 1})
        details.update({"trail_frame": trail_idx, "trail_x": trail_x, "trail_y": trail_y})
    else:
        details["trail_frame"] = None

    return sprites, details


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    contract_bytes = args.contract.read_bytes()
    contract = json.loads(contract_bytes)
    assert trunc_div(-7, 3) == -2 and lerp_q8(-8, 270, 128) == 131
    # Compare the Python geometry model to the unchanged C reference output,
    # including every active age and both signed axes.
    generation = json.loads((PROJECT_ROOT / "out/logs/splash_v3_motion_lut_generation_20261016.json").read_text())
    reference = [tuple(map(int, line.split())) for line in
                 (PROJECT_ROOT / generation["reference_positions"]).read_text().splitlines()][96 * 64:]
    checked = 0
    for index, spark in enumerate(contract["sparks"]):
        for age in range(int(spark["lifetime_frames"])):
            if position(spark, age) != reference[(index * 30) + age]:
                raise ValueError(f"contract_c_reference_position_mismatch:{index}:{age}")
            checked += 1
    if args.self_check:
        print(f"wind geometry self-check passed: signed integer rounding and {checked} C-reference positions")
        return 0
    simulator = load_simulator()
    start = int(contract["timeline"]["start_frame"])
    end = int(contract["timeline"]["end_frame_exclusive"])
    entries = []

    for frame in range(start, end):
        sprites = []
        positions = []
        for spark in contract["sparks"]:
            instances, detail = particle_instances(spark, frame)
            sprites.extend(instances)
            if detail is not None:
                positions.append(detail)
        pair_distances = []
        for first_index, first in enumerate(positions):
            for second in positions[first_index + 1:]:
                dx = int(first["x"]) - int(second["x"])
                dy = int(first["y"]) - int(second["y"])
                pair_distances.append({
                    "spark_ids": [first["id"], second["id"]],
                    "distance_px": math.sqrt((dx * dx) + (dy * dy)),
                })
        nearest_pair = min(pair_distances, key=lambda pair: pair["distance_px"], default=None)
        result = simulator.simulate({
            "display_mode": "h40",
            "headroom_justification": contract["budget_contract"]["headroom_justification"],
            "sprites": sprites,
        })
        peak_lines = []
        for line in range(224):
            links = sum(1 for sprite in sprites if sprite["y"] <= line < sprite["y"] + 8)
            if links == result["max_sprites_per_scanline"] and links > 0:
                peak_lines.append({
                    "scanline": line,
                    "sprite_links": links,
                    "sprite_pixels": links * 8,
                })
        entries.append({
            "scene_frame": frame,
            "active_sparks": len(positions),
            "visible_sparks": sum(1 for item in positions if item["core_frame"] is not None),
            "visible_sprite_links": len(sprites),
            "minimum_core_center_distance_px": (
                round(nearest_pair["distance_px"], 2) if nearest_pair is not None else None
            ),
            "nearest_pair": nearest_pair,
            "pairs_below_16_px": sum(1 for pair in pair_distances if pair["distance_px"] < 16),
            "pairs_below_20_px": sum(1 for pair in pair_distances if pair["distance_px"] < 20),
            "pairs_below_24_px": sum(1 for pair in pair_distances if pair["distance_px"] < 24),
            "max_sprites_per_scanline": result["max_sprites_per_scanline"],
            "max_sprite_pixels_per_scanline": result["max_sprite_pixels_per_scanline"],
            "peak_lines": peak_lines,
            "status": result["status"],
            "positions": positions,
            "blockers": result["blockers"],
            "warnings": result["warnings"],
        })

    max_sprites = max(row["max_sprites_per_scanline"] for row in entries)
    max_pixels = max(row["max_sprite_pixels_per_scanline"] for row in entries)
    worst_sprites = [row for row in entries if row["max_sprites_per_scanline"] == max_sprites]
    worst_pixels = [row for row in entries if row["max_sprite_pixels_per_scanline"] == max_pixels]
    nearest_approach = min(
        (row for row in entries if row["nearest_pair"] is not None),
        key=lambda row: row["nearest_pair"]["distance_px"],
    )
    min_pair_separation = round(nearest_approach["nearest_pair"]["distance_px"], 2)
    max_pairs_below_16 = max(row["pairs_below_16_px"] for row in entries)
    max_pairs_below_20 = max(row["pairs_below_20_px"] for row in entries)
    max_pairs_below_24 = max(row["pairs_below_24_px"] for row in entries)
    dispersion_pass = min_pair_separation >= 20 and max_pairs_below_16 == 0
    output = {
        "schema_version": "splash_v3_wind_dispersal_scanline_report.v1",
        "status": "measured_geometry_only",
        "contract": str(args.contract.relative_to(PROJECT_ROOT)),
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "simulator": str(SIMULATOR_PATH.relative_to(WORKSPACE_ROOT)),
        "c_reference_position_pairs_checked": checked,
        "display_mode": "h40",
        "measurement_frames": len(entries),
        "frame_range": [start, end],
        "allocated_scene_sprite_links": 64,
        "max_active_sparks_per_frame": max(row["active_sparks"] for row in entries),
        "max_visible_sparks_per_frame": max(row["visible_sparks"] for row in entries),
        "max_visible_sprite_links_per_frame": max(row["visible_sprite_links"] for row in entries),
        "minimum_pair_separation_px": min_pair_separation,
        "minimum_pair_separation_frame": nearest_approach["scene_frame"],
        "minimum_pair_separation_pair": nearest_approach["nearest_pair"]["spark_ids"],
        "max_pairs_below_16_px_per_frame": max_pairs_below_16,
        "max_pairs_below_20_px_per_frame": max_pairs_below_20,
        "max_pairs_below_24_px_per_frame": max_pairs_below_24,
        "dispersion_criterion_px": 20,
        "dispersion_pass": dispersion_pass,
        "max_sprites_per_scanline": max_sprites,
        "max_sprite_pixels_per_scanline": max_pixels,
        "worst_sprite_frames": [row["scene_frame"] for row in worst_sprites],
        "worst_pixel_frames": [row["scene_frame"] for row in worst_pixels],
        "over_limit_frames": [
            row["scene_frame"]
            for row in entries
            if row["status"] != "ok"
        ],
        "frames": entries,
        "interpretation": "This proves only the per-frame geometry and pair separation of the defined six-core/six-trail sweep. It does not prove that the native sprite frames read well, that the user accepts the direction, or that the whole ROM meets runtime budgets.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        f"measured {len(entries)} frames; max {max_sprites} sprites / "
        f"{max_pixels} pixels per line; minimum core separation {min_pair_separation}px "
        f"({ 'pass' if dispersion_pass else 'review' }); report {args.output}"
    )
    return 0 if not output["over_limit_frames"] and dispersion_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
