#!/usr/bin/env python3
"""Measure every emitted Splash V3 sprite frame with the canonical VDP oracle.

The report is deliberately scoped to sprite scanline geometry. It does not
stand in for the workspace measurement gate, tile residency, DMA, CPU, VDP
budget, pixel-art review, or emulator evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def load_simulator(path: Path):
    spec = importlib.util.spec_from_file_location("vdp_scanline_simulator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load canonical simulator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def self_check() -> int:
    project_root = Path(__file__).resolve().parents[3]
    workspace_root = project_root.parents[2]
    simulator_path = workspace_root / "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py"
    simulator = load_simulator(simulator_path)
    if simulator.self_check() != 0:
        print("measure_splash_v3_scanline self-check failed: canonical oracle", file=sys.stderr)
        return 1
    justification = "fixture for exact count boundary"
    legal = simulator.simulate({
        "display_mode": "h40",
        "sprites": [{"x": 0, "y": 80, "w": 8, "h": 8} for _ in range(20)],
        "headroom_justification": justification,
    })
    overflow = simulator.simulate({
        "display_mode": "h40",
        "sprites": [{"x": 0, "y": 80, "w": 8, "h": 8} for _ in range(21)],
        "headroom_justification": justification,
    })
    if legal["status"] != "ok" or legal["max_sprites_per_scanline"] != 20:
        print("measure_splash_v3_scanline self-check failed: legal H40 boundary", file=sys.stderr)
        return 1
    if overflow["status"] != "error" or "sprites_per_scanline_over_20" not in overflow["blockers"]:
        print("measure_splash_v3_scanline self-check failed: H40 overflow", file=sys.stderr)
        return 1
    print("measure_splash_v3_scanline self-check passed (legal 20 and rejected 21 sprites/scanline)")
    return 0


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    workspace_root = project_root.parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root", type=Path,
        default=project_root / "out/logs/choreography_inputs_scoped_20261013_r2",
    )
    parser.add_argument(
        "--output", type=Path,
        default=project_root / "out/logs/splash_v3_scanline_matrix_scoped_20261013.json",
    )
    parser.add_argument(
        "--tool-gate", type=Path,
        default=project_root / "doc/splash_v3_visual_measurement_tools_report_20261013.json",
    )
    parser.add_argument(
        "--workspace-gate", type=Path,
        default=project_root / "out/logs/measurement_gate_report_workspace_20261012.json",
    )
    parser.add_argument("--selected-profile", default="particles_64_8x8")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        return self_check()

    input_root = args.input_root.resolve()
    output_path = args.output.resolve()
    manifest_path = input_root / "manifest.json"
    tool_gate_path = args.tool_gate.resolve()
    workspace_gate_path = args.workspace_gate.resolve()
    simulator_path = workspace_root / "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py"

    tool_gate = load_json(tool_gate_path)
    if tool_gate.get("blocking") or tool_gate.get("passed") != tool_gate.get("tools_checked"):
        raise SystemExit("Scoped measurement-tool self-check gate is not green; refusing to measure.")
    manifest = load_json(manifest_path)
    if manifest.get("status") != "generated_unmeasured" or not manifest.get("frame_inputs_emitted"):
        raise SystemExit("Expected complete unmeasured choreography inputs.")
    emitted = manifest.get("emitted_frame_inputs", [])
    if manifest.get("emitted_frame_input_count") != len(emitted) or not emitted:
        raise SystemExit("Choreography manifest frame count does not match its emitted input list.")
    for source in manifest.get("source_files", []):
        source_path = project_root / source["path"]
        if not source_path.is_file() or sha256(source_path) != source["sha256"]:
            raise SystemExit(f"Choreography source hash mismatch: {source.get('path')}")

    simulator = load_simulator(simulator_path)
    if simulator.self_check() != 0:
        raise SystemExit("Canonical VDP scanline simulator self-check failed; refusing to measure.")

    records: list[dict[str, Any]] = []
    profiles: dict[str, dict[str, Any]] = {}
    particle_pattern = re.compile(r"^act1_particles_(\d+)_geom_(\d+by\d+)_f(\d+)$")
    for rel in emitted:
        path = project_root / rel
        if not path.is_file():
            raise SystemExit(f"Missing frame input: {rel}")
        result = simulator.simulate(load_json(path))
        match = particle_pattern.match(path.stem)
        if match:
            count = int(match.group(1))
            geometry = match.group(2).replace("by", "x")
            frame = int(match.group(3))
            profile_id = f"particles_{count}_{geometry}"
            state_id = "energy" if frame < 84 else "outline_convergence"
        else:
            sweep_match = re.match(r"^act5_sweep_band_f(\d+)$", path.stem)
            if not sweep_match:
                raise SystemExit(f"Unrecognized frame input: {rel}")
            frame = int(sweep_match.group(1))
            profile_id = "sweep_7x8x8"
            state_id = "sweep"

        row = {
            "input": rel,
            "input_sha256": sha256(path),
            "profile_id": profile_id,
            "state_id": state_id,
            "global_frame": frame,
            "status": result["status"],
            "sprite_count": result["sprite_count"],
            "hardware_sprite_count": result["hardware_sprite_count"],
            "max_sprites_per_scanline": result["max_sprites_per_scanline"],
            "max_sprite_pixels_per_scanline": result["max_sprite_pixels_per_scanline"],
            "headroom": result["headroom"],
            "blockers": result["blockers"],
            "warnings": result["warnings"],
        }
        records.append(row)
        profile = profiles.setdefault(profile_id, {
            "profile_id": profile_id,
            "state_ids": [],
            "frames": [],
            "status": "passed",
        })
        profile["state_ids"].append(state_id)
        profile["frames"].append(row)
        if result["status"] != "ok":
            profile["status"] = "blocked"

    summaries = []
    for profile in profiles.values():
        frames = profile.pop("frames")
        profile["frame_count"] = len(frames)
        profile["state_ids"] = sorted(set(profile["state_ids"]))
        profile["status_counts"] = {
            status: sum(1 for frame in frames if frame["status"] == status)
            for status in ("ok", "error")
        }
        profile["max_sprites_per_scanline"] = max(f["max_sprites_per_scanline"] for f in frames)
        profile["max_sprite_pixels_per_scanline"] = max(f["max_sprite_pixels_per_scanline"] for f in frames)
        profile["max_hardware_sprite_count"] = max(f["hardware_sprite_count"] for f in frames)
        profile["peak_utilization"] = max(f["headroom"]["peak_utilization"] for f in frames)
        profile["worst_frame_by_sprites"] = max(
            frames, key=lambda f: (f["max_sprites_per_scanline"], f["max_sprite_pixels_per_scanline"])
        )["global_frame"]
        profile["worst_frame_by_pixels"] = max(
            frames, key=lambda f: (f["max_sprite_pixels_per_scanline"], f["max_sprites_per_scanline"])
        )["global_frame"]
        profile["blockers"] = sorted({b for frame in frames for b in frame["blockers"]})
        profile["warnings"] = sorted({w for frame in frames for w in frame["warnings"]})
        summaries.append(profile)

    def order(profile: dict[str, Any]) -> tuple[bool, int, str]:
        match = re.search(r"particles_(\d+)", profile["profile_id"])
        return (match is None, int(match.group(1)) if match else 0, profile["profile_id"])

    summaries.sort(key=order)
    selected = next((p for p in summaries if p["profile_id"] == args.selected_profile), None)
    if selected is None:
        raise SystemExit(f"Selected profile was not measured: {args.selected_profile}")
    rejected = [p["profile_id"] for p in summaries if p["status"] != "passed"]
    workspace_gate = load_json(workspace_gate_path) if workspace_gate_path.is_file() else {
        "blocking": True,
        "blocking_statuses": ["workspace_gate_report_missing"],
    }
    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "splash_v3_scoped_scanline_matrix",
        "project_id": "BRANDING_SPLASH_V3",
        "generated_from": {
            "choreography_manifest": manifest_path.relative_to(project_root).as_posix(),
            "choreography_manifest_sha256": sha256(manifest_path),
            "choreography_generator": "data/source_art/branding_v3/choreograph_splash_v3.py",
            "choreography_generator_sha256": sha256(project_root / "data/source_art/branding_v3/choreograph_splash_v3.py"),
            "measurement_runner": "data/source_art/branding_v3/measure_splash_v3_scanline.py",
            "measurement_runner_sha256": sha256(Path(__file__).resolve()),
            "storyboard": "doc/branding_v3_cinematic_storyboard.json",
            "storyboard_sha256": sha256(project_root / "doc/branding_v3_cinematic_storyboard.json"),
            "simulator": "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py",
            "simulator_sha256": sha256(simulator_path),
            "simulator_version": simulator.TOOL_VERSION,
            "scoped_measurement_tool_gate": {
                "path": tool_gate_path.relative_to(project_root).as_posix(),
                "sha256": sha256(tool_gate_path),
                "passed": tool_gate.get("passed"),
                "tools_checked": tool_gate.get("tools_checked"),
                "blocking": tool_gate.get("blocking"),
            },
            "workspace_measurement_gate": {
                "path": workspace_gate_path.relative_to(project_root).as_posix(),
                "sha256": sha256(workspace_gate_path) if workspace_gate_path.is_file() else None,
                "blocking": workspace_gate.get("blocking"),
                "blocking_statuses": workspace_gate.get("blocking_statuses", []),
            },
        },
        "status": "measured",
        "candidate_sweep_verdict": "selected_profile_passed" if selected["status"] == "passed" else "selected_profile_rejected",
        "selected_profile": {
            "profile_id": selected["profile_id"],
            "status": selected["status"],
            "max_sprites_per_scanline": selected["max_sprites_per_scanline"],
            "max_sprite_pixels_per_scanline": selected["max_sprite_pixels_per_scanline"],
            "max_hardware_sprite_count": selected["max_hardware_sprite_count"],
            "peak_utilization": selected["peak_utilization"],
            "worst_frame": selected["worst_frame_by_sprites"],
            "visual_approval": False,
        },
        "rejected_stress_profiles": rejected,
        "measurement_scope": (
            "Sprite scanline geometry only for 24/32/48/64/80 particle profiles at 8x8 and 16x16, "
            "plus the seven-segment sweep. No VRAM, DMA, CPU, tile residency, pixel-art, or runtime claim."
        ),
        "display_mode": "h40",
        "limits": {"sprites_per_scanline": 20, "pixels_per_scanline": 320, "sprite_links_total": 80},
        "input_count": len(records),
        "candidate_particle_counts": [24, 32, 48, 64, 80],
        "geometry_profiles": ["8x8", "16x16"],
        "profile_summaries": summaries,
        "frame_results": records,
        "limitations": [
            "Scoped result requires the canonical simulator self-check and all six local measurement-tool checks to pass.",
            "The workspace measurement gate is reported separately and may remain blocked by unrelated project-source mirrors.",
            "Glyph-mask tile centers are provisional anchors from the current WIP wordmark; they do not approve its lettering, model sheet, or composition.",
            "Profiles omit any additional sprite load not declared in the storyboard.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "input_count": report["input_count"],
        "report": output_path.relative_to(project_root).as_posix(),
        "profiles": [{
            key: profile[key] for key in (
                "profile_id", "frame_count", "status", "max_sprites_per_scanline",
                "max_sprite_pixels_per_scanline", "max_hardware_sprite_count",
                "peak_utilization", "worst_frame_by_sprites", "blockers", "warnings",
            )
        } for profile in summaries],
        "workspace_gate_blocked": workspace_gate.get("blocking"),
        "workspace_gate_blockers": workspace_gate.get("blocking_statuses", []),
    }, indent=2))
    return 0 if report["candidate_sweep_verdict"] == "selected_profile_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
