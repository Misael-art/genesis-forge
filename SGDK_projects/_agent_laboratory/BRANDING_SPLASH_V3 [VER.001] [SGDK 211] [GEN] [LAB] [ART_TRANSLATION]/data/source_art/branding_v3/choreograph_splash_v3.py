#!/usr/bin/env python3
"""Generate unmeasured, data-only VDP inputs for the Splash v3 choreography.

This tool emits geometry candidates only. It does not draw pixels and never
invokes the scanline simulator. Simulator-ready per-frame files can be emitted
after the shared measurement gate is cleared.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image
from build_splash_v3_lettering_native_probes import DIRECTIONS as LETTERING_DIRECTIONS
from build_splash_v3_lettering_native_probes import make_probe_plate


COUNTS = (24, 32, 48, 64, 80)
GEOMETRIES = {
    "8x8": (8, 8),
    "16x16": (16, 16),
}
ENERGY_START = 24
OUTLINE_START = 84
PARTICLE_END = 120
PARTICLE_CENTER = (160, 112)
PARTICLE_MAX_RADIUS = 88
SGDK_BOX = (48, 72, 224, 48)
SGDK_WORDMARK_SOURCE = "data/source_art/branding_v3/sources/source_lettering_model_sheet_ai_v003_20261014.png"
SGDK_WORDMARK_SOURCE_SHA256 = "d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8"
SGDK_WORDMARK_SOURCE_CROP = tuple(LETTERING_DIRECTIONS["B"]["sgdk_crop"])
SGDK_WORDMARK_SIZE = (224, 48)
SGDK_WORDMARK_SOURCE_SIZE = (1672, 941)
GLYPH_TILE_MIN_VISIBLE_PIXELS = 24

# Signed 8.8 values for 16 evenly spaced directions. No float math is used.
COS_16 = (256, 237, 181, 98, 0, -98, -181, -237, -256, -237, -181, -98, 0, 98, 181, 237)
SIN_16 = (0, 98, 181, 237, 256, 237, 181, 98, 0, -98, -181, -237, -256, -237, -181, -98)


def div_toward_zero(numerator: int, denominator: int) -> int:
    if numerator < 0:
        return -((-numerator) // denominator)
    return numerator // denominator


def mul_ratio_toward_zero(value: int, numerator: int, denominator: int) -> int:
    return div_toward_zero(value * numerator, denominator)


def particle_birth_frame(index: int, count: int) -> int:
    """Distribute births across the whole energy act, never as a center burst.

    The 8-at-once prototype collapsed many cells onto the same scanlines in its
    first frames. A stretched birth cadence preserves a growing energy field
    while giving every particle a distinct outward path from the first frame.
    """
    span = max(1, OUTLINE_START - ENERGY_START)
    return ENERGY_START + (index * span // max(1, count))


def particle_sector(index: int) -> int:
    # Multiplication by five permutes the sixteen sectors.
    return (index * 5 + (index // 8) * 3) & 15


def radius_for_age(age: int) -> int:
    # Start on a small ring so multiple particles never stack at the exact
    # origin. The expansion, brief apex, and inward turn remain readable.
    if age <= 28:
        return 8 + ((PARTICLE_MAX_RADIUS - 8) * age // 28)
    if age <= 36:
        return PARTICLE_MAX_RADIUS
    if age < 59:
        return PARTICLE_MAX_RADIUS - (74 * (age - 36) // 23)
    return 14


def particle_radial_center(index: int, frame: int, count: int) -> tuple[int, int]:
    birth = particle_birth_frame(index, count)
    age = max(0, frame - birth)
    radius = radius_for_age(age)
    sector = particle_sector(index)
    dx = div_toward_zero(COS_16[sector] * radius, 256)
    dy = div_toward_zero(SIN_16[sector] * radius, 256)
    return PARTICLE_CENTER[0] + dx, PARTICLE_CENTER[1] + dy


def glyph_target_anchors(project_root: Path, count: int) -> tuple[list[dict[str, int]], dict[str, Any]]:
    """Select 8x8 anchors from the authorized B-direction source crop.

    Each target cell contains at least 24 visible logo pixels. The selected
    cells span the source-derived 224x48 mask, then match particles to target
    rows by their frame-83 position to reduce path crossings and scanline
    crowding. The mask is produced in memory by the existing lettering
    translator; no runtime asset is read as a generation source.
    """
    source_path = project_root / SGDK_WORDMARK_SOURCE
    if not source_path.is_file():
        raise FileNotFoundError(f"missing SGDK target source: {source_path}")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if source_hash != SGDK_WORDMARK_SOURCE_SHA256:
        raise ValueError("SGDK lettering source hash changed; review the workset before regenerating anchors")

    with Image.open(source_path) as source:
        if source.size != SGDK_WORDMARK_SOURCE_SIZE:
            raise ValueError(f"SGDK lettering source must remain {SGDK_WORDMARK_SOURCE_SIZE}")
        image = make_probe_plate(source, SGDK_WORDMARK_SOURCE_CROP, SGDK_WORDMARK_SIZE)
        if image.mode != "P" or image.size != SGDK_WORDMARK_SIZE or image.info.get("transparency") != 0:
            raise ValueError(
                f"source-derived SGDK mask must be indexed {SGDK_WORDMARK_SIZE} with index 0 transparent"
            )
        columns = image.width // 8
        rows = image.height // 8
        candidates: list[dict[str, int]] = []
        for tile_y in range(rows):
            for tile_x in range(columns):
                visible = sum(
                    image.getpixel((x, y)) != 0
                    for y in range(tile_y * 8, (tile_y + 1) * 8)
                    for x in range(tile_x * 8, (tile_x + 1) * 8)
                )
                if visible >= GLYPH_TILE_MIN_VISIBLE_PIXELS:
                    candidates.append({"tile_x": tile_x, "tile_y": tile_y, "visible_pixels": visible})

    if count < 1 or count > len(candidates):
        raise ValueError(f"cannot select {count} anchors from {len(candidates)} occupied logo cells")

    if count == 1:
        selected = [candidates[len(candidates) // 2]]
    else:
        selected = [
            candidates[(index * (len(candidates) - 1) + ((count - 1) // 2)) // (count - 1)]
            for index in range(count)
        ]
    start_centers = [particle_radial_center(index, OUTLINE_START - 1, count) for index in range(count)]
    particle_order = sorted(range(count), key=lambda index: (start_centers[index][1], start_centers[index][0], index))
    target_order = sorted(selected, key=lambda point: (point["tile_y"], point["tile_x"]))
    assigned: list[dict[str, int] | None] = [None] * count
    for particle_index, point in zip(particle_order, target_order, strict=True):
        assigned[particle_index] = point
    if any(point is None for point in assigned):
        raise ValueError(f"incomplete glyph anchor assignment for particle count {count}")

    x0, y0, _, _ = SGDK_BOX
    anchors = [
        {
            "particle_index": index,
            "tile_x": assigned[index]["tile_x"],
            "tile_y": assigned[index]["tile_y"],
            "visible_pixels": assigned[index]["visible_pixels"],
            "center_x": x0 + (assigned[index]["tile_x"] * 8) + 4,
            "center_y": y0 + (assigned[index]["tile_y"] * 8) + 4,
        }
        for index in range(count)
    ]
    metadata = {
        "source_path": SGDK_WORDMARK_SOURCE,
        "source_sha256": source_hash,
        "source_size_px": list(SGDK_WORDMARK_SOURCE_SIZE),
        "source_crop_px": list(SGDK_WORDMARK_SOURCE_CROP),
        "derived_mask_pixel_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
        "derived_mask_size_px": list(SGDK_WORDMARK_SIZE),
        "translation": "in-memory B-direction crop through build_splash_v3_lettering_native_probes.make_probe_plate",
        "source_transparency_index": 0,
        "minimum_visible_pixels_per_8x8_cell": GLYPH_TILE_MIN_VISIBLE_PIXELS,
        "eligible_cells": len(candidates),
        "selected_count": count,
        "row_major_even_sampling": True,
        "assignment_policy": "match particles sorted by frame-83 center y/x to glyph cells sorted by tile row/column",
        "particle_start_frame": OUTLINE_START - 1,
        "regenerate_when_source_hash_changes": True,
    }
    return anchors, metadata


def ease_in_out_fraction(step: int, duration: int) -> tuple[int, int]:
    bounded = min(max(step, 0), duration)
    numerator = bounded * bounded * (3 * duration - 2 * bounded)
    denominator = duration * duration * duration
    return numerator, denominator


def particle_center(index: int, frame: int, count: int, target_centers: list[tuple[int, int]]) -> tuple[int, int]:
    if frame < OUTLINE_START:
        return particle_radial_center(index, frame, count)

    start_x, start_y = particle_radial_center(index, OUTLINE_START - 1, count)
    target_x, target_y = target_centers[index]
    step = frame - (OUTLINE_START - 1)
    eased_numerator, eased_denominator = ease_in_out_fraction(step, PARTICLE_END - OUTLINE_START)
    x = start_x + mul_ratio_toward_zero(target_x - start_x, eased_numerator, eased_denominator)
    y = start_y + mul_ratio_toward_zero(target_y - start_y, eased_numerator, eased_denominator)
    return x, y


def particle_frame(count: int, frame: int, geometry_name: str, target_centers: list[tuple[int, int]]) -> dict[str, Any]:
    width, height = GEOMETRIES[geometry_name]
    sprites: list[dict[str, int | str]] = []
    for index in range(count):
        if frame < particle_birth_frame(index, count):
            continue
        center_x, center_y = particle_center(index, frame, count, target_centers)
        sprites.append({
            "name": f"particle_{index:02d}",
            "x": center_x - width // 2,
            "y": center_y - height // 2,
            "w": width,
            "h": height,
        })

    state = "energy" if frame < OUTLINE_START else "outline"
    return {
        "global_frame": frame,
        "state_id": state,
        "simulator_input": {
            "display_mode": "h40",
            "sprites": sprites,
            "headroom_justification": (
                "The shard reveal compares distinct 8x8 particle densities and 16x16 stress "
                "profiles; the 80-particle 8x8 case is an upper-bound candidate that consumes "
                "all 80 hardware sprite links. Each geometry/count pair must be measured against "
                "the independent H40 scanline sprite and pixel limits."
            ),
        },
    }


def make_particle_series(count: int, geometry_name: str, anchors: list[dict[str, int]], anchor_metadata: dict[str, Any]) -> dict[str, Any]:
    target_centers = [(anchor["center_x"], anchor["center_y"]) for anchor in anchors]
    frames = [
        particle_frame(count, frame, geometry_name, target_centers)
        for frame in range(ENERGY_START, PARTICLE_END)
    ]
    return {
        "schema_version": "1.0.0",
        "scene_id": "APP_SCENE_BRANDING",
        "sequence_id": "act1_particle_density_candidates",
        "candidate_count": count,
        "geometry_profile": geometry_name,
        "coordinate_space": {"width": 320, "height": 224, "display_mode": "h40"},
        "timeline": {"start_frame": ENERGY_START, "end_frame_exclusive": PARTICLE_END},
        "target_model": "visible_source_derived_sgdk_b_direction_glyph_mask_tile_centers_wip",
        "measurement_status": "not_run",
        "simulator_invoked": False,
        "target_anchor_metadata": anchor_metadata,
        "target_anchors": anchors,
        "frames": frames,
    }


def make_sweep_series() -> dict[str, Any]:
    # The runtime reuses seven 8x8 crystal frames as a short diagonal trail.
    # It crosses the completed lockup without a broad beam obscuring letterforms.
    frames: list[dict[str, Any]] = []
    for frame in range(180, 210):
        x = (frame - 180) * 10 - 16
        sprites = [
            {"name": f"crystal_trail_{index}", "x": x + (index * 2), "y": 76 + (index * 8), "w": 8, "h": 8}
            for index in range(7)
        ]
        frames.append({
            "global_frame": frame,
            "state_id": "sweep",
            "simulator_input": {
                "display_mode": "h40",
                "sprites": sprites,
                "headroom_justification": (
                    "Seven shared 8x8 crystal sprites form a brief diagonal trail across the "
                    "lockup; the narrow trail preserves wordmark readability."
                ),
            },
        })
    return {
        "schema_version": "1.0.0",
        "scene_id": "APP_SCENE_BRANDING",
        "sequence_id": "act5_crystal_trail_sweep",
        "candidate_sprite_count": 7,
        "sprite_geometry_px": {"width": 8, "height": 8, "y_positions": [76, 84, 92, 100, 108, 116, 124]},
        "timeline": {"start_frame": 180, "end_frame_exclusive": 210, "x_start": -16, "x_step": 10},
        "measurement_status": "not_run",
        "simulator_invoked": False,
        "frames": frames,
    }


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def allocate_output_root(base: Path) -> Path:
    if not base.exists():
        return base
    suffix = 1
    while True:
        candidate = base.with_name(f"{base.name}_r{suffix}")
        if not candidate.exists():
            return candidate
        suffix += 1


def write_json(path: Path, value: Any) -> str:
    data = json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def emit_frame_inputs(project_root: Path, output_root: Path, sequences: list[tuple[str, dict[str, Any]]]) -> list[str]:
    emitted: list[str] = []
    frame_root = output_root / "simulator_inputs"
    for sequence_name, sequence in sequences:
        for frame in sequence.get("frames", []):
            global_frame = int(frame["global_frame"])
            filename = f"{sequence_name}_f{global_frame:03d}.json"
            path = frame_root / filename
            write_json(path, frame["simulator_input"])
            emitted.append(path.relative_to(project_root).as_posix())
    return emitted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument(
        "--emit-frame-inputs",
        action="store_true",
        help="Also emit one simulator-shaped JSON input for every candidate frame; does not run the simulator.",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    if args.output_root is None:
        requested_root = project_root / "out" / "logs" / "choreography_inputs_20261012"
    elif args.output_root.is_absolute():
        requested_root = args.output_root
    else:
        requested_root = project_root / args.output_root

    output_root = allocate_output_root(requested_root.resolve())
    output_root.mkdir(parents=True, exist_ok=False)

    sequences: list[tuple[str, dict[str, Any]]] = []
    file_records: list[dict[str, str]] = []
    target_source_path = project_root / SGDK_WORDMARK_SOURCE
    if not target_source_path.is_file():
        raise SystemExit(f"missing SGDK target source: {target_source_path}")
    target_source_hash = hashlib.sha256(target_source_path.read_bytes()).hexdigest()
    selected_anchors: list[dict[str, int]] | None = None
    selected_anchor_metadata: dict[str, Any] | None = None
    for count in COUNTS:
        anchors, anchor_metadata = glyph_target_anchors(project_root, count)
        if count == 64:
            selected_anchors = anchors
            selected_anchor_metadata = anchor_metadata
        for geometry_name in GEOMETRIES:
            sequence_name = f"act1_particles_{count}_geom_{geometry_name.replace('x', 'by')}"
            sequence = make_particle_series(count, geometry_name, anchors, anchor_metadata)
            path = output_root / f"{sequence_name}.json"
            digest = write_json(path, sequence)
            sequences.append((sequence_name, sequence))
            file_records.append({"path": path.relative_to(project_root).as_posix(), "sha256": digest})

    sweep = make_sweep_series()
    sweep_path = output_root / "act5_sweep_band.json"
    sweep_digest = write_json(sweep_path, sweep)
    sequences.append(("act5_sweep_band", sweep))
    file_records.append({"path": sweep_path.relative_to(project_root).as_posix(), "sha256": sweep_digest})

    if selected_anchors is None or selected_anchor_metadata is None:
        raise SystemExit("selected 64-particle glyph anchor candidate was not generated")
    anchor_contract = {
        "schema_version": "1.0.0",
        "contract_id": "branding_v3_particle_glyph_anchor_v002",
        "status": "development_candidate_pending_visual_review",
        "scene_id": "branding_sequence_v3",
        "runtime_scene_id": "APP_SCENE_BRANDING",
        "coordinate_space": {"width": 320, "height": 224, "display_mode": "h40"},
        "target_source": selected_anchor_metadata,
        "selection_policy": {
            "candidate_cells": "8x8 cells of the indexed B-direction mask derived in memory from the eligible lettering source, with at least 24 nontransparent pixels",
            "sampling": "64 anchors evenly sampled across row-major eligible cells; particles sorted by frame-83 center y/x are matched to cells sorted by tile row/column",
            "cell_center_offset_px": [4, 4],
            "plate_origin_px": [SGDK_BOX[0], SGDK_BOX[1]],
            "source_hash_change_policy": "Review the active workset and retranslate before regenerating anchors from a changed lettering source.",
        },
        "motion": {
            "radial_phase_frames": [ENERGY_START, OUTLINE_START],
            "convergence_frames": [OUTLINE_START, PARTICLE_END],
            "target_reached_frame": PARTICLE_END - 1,
            "curve": "integer smoothstep ease-in-out",
            "particle_count": 64,
            "sprite_size_px": [8, 8],
        },
        "anchors": selected_anchors,
        "review": {
            "human_visual_approval": False,
            "model_sheet_approved": False,
            "final_visual_approval": False,
            "future_review_required": True,
        },
    }
    anchor_contract_path = output_root / "particle_glyph_anchor_contract.json"
    anchor_contract_digest = write_json(anchor_contract_path, anchor_contract)
    file_records.append({"path": anchor_contract_path.relative_to(project_root).as_posix(), "sha256": anchor_contract_digest})

    emitted_inputs: list[str] = []
    if args.emit_frame_inputs:
        emitted_inputs = emit_frame_inputs(project_root, output_root, sequences)

    manifest = {
        "schema_version": "1.0.0",
        "artifact_kind": "unmeasured_choreography_inputs",
        "scene_id": "APP_SCENE_BRANDING",
        "status": "generated_unmeasured",
        "project_root": ".",
        "output_root": output_root.relative_to(project_root).as_posix(),
        "generator": "data/source_art/branding_v3/choreograph_splash_v3.py",
        "display_mode": "h40",
        "candidate_particle_counts": list(COUNTS),
        "particle_geometry_profiles": list(GEOMETRIES),
        "preferred_visual_candidate": {
            "particle_count": 64,
            "geometry_profile": "8x8",
            "status": "measured_pressure_candidate_not_visual_approval",
            "rationale": "The 64x8x8 profile uses tile-sized anchors sampled from visible SGDK glyph cells; pressure and human readability must be remeasured. This is not visual approval.",
        },
        "particle_frame_range": [ENERGY_START, PARTICLE_END],
        "sweep_frame_range": [180, 210],
        "target_model": "WIP visible-glyph tile centers sampled from the authorized B-direction source translation mask; regenerate when the source hash changes.",
        "target_anchor_source": {
            "path": SGDK_WORDMARK_SOURCE,
            "sha256": target_source_hash,
            "minimum_visible_pixels_per_8x8_cell": GLYPH_TILE_MIN_VISIBLE_PIXELS,
        },
        "target_anchor_contract": {
            "path": anchor_contract_path.relative_to(project_root).as_posix(),
            "sha256": anchor_contract_digest,
            "status": anchor_contract["status"],
        },
        "worst_frame_selection": "not computed; no simulator reports were produced",
        "simulator_invoked": False,
        "frame_inputs_emitted": bool(args.emit_frame_inputs),
        "emitted_frame_input_count": len(emitted_inputs),
        "measurement_gate_ref": "out/logs/measurement_gate_report_workspace_20261012.json",
        "source_files": [
            *file_records,
            {"path": SGDK_WORDMARK_SOURCE, "sha256": target_source_hash},
        ],
        "emitted_frame_inputs": emitted_inputs,
    }
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)
    print(json.dumps({
        "status": "generated_unmeasured",
        "output_root": manifest["output_root"],
        "scenario_files": len(file_records),
        "candidate_particle_profiles": len(COUNTS) * len(GEOMETRIES),
        "emitted_frame_inputs": len(emitted_inputs),
        "simulator_invoked": False,
        "manifest": manifest_path.relative_to(project_root).as_posix(),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
