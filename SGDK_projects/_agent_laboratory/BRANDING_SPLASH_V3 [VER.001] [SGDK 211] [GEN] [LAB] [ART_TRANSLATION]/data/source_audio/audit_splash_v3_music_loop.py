#!/usr/bin/env python3
"""Check VGM loop duration and muted channel state at the structural seam.

This is a byte-level loop check. It cannot approve the audible seam or the
music in the final BlastEm ROM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VGM = PROJECT_ROOT / "out" / "audio" / "splash_v3_music.vgm"
DEFAULT_SCORE = Path(__file__).with_name("splash_v3_music_score.json")
DEFAULT_REPORT = PROJECT_ROOT / "out" / "logs" / "splash_v3_audio_loop_report.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def analyze(data: bytes, expected_frames: int) -> dict:
    if len(data) < 0x100 or data[:4] != b"Vgm ":
        raise ValueError("missing VGM 1.x header")
    eof_abs = int.from_bytes(data[0x04:0x08], "little") + 4
    version = int.from_bytes(data[0x08:0x0C], "little")
    total_samples = int.from_bytes(data[0x18:0x1C], "little")
    loop_rel = int.from_bytes(data[0x1C:0x20], "little")
    loop_samples = int.from_bytes(data[0x20:0x24], "little")
    rate = int.from_bytes(data[0x24:0x28], "little")
    data_rel = int.from_bytes(data[0x34:0x38], "little")
    data_start = 0x34 + data_rel if data_rel else 0x40
    loop_abs = 0x1C + loop_rel if loop_rel else None

    if eof_abs != len(data):
        raise ValueError(f"declared EOF {eof_abs} differs from file size {len(data)}")
    if loop_abs is None or not data_start <= loop_abs < len(data):
        raise ValueError("loop pointer is absent or outside the command stream")

    total_waits = 0
    loop_waits = None
    loop_seen = False
    fm_key_state = {channel: 0 for channel in range(6)}
    psg_volume = {channel: 15 for channel in range(4)}
    loop_fm_state = None
    loop_psg_state = None
    ended = False
    position = data_start
    while position < len(data):
        if position == loop_abs:
            loop_seen = True
            loop_waits = 0
            loop_fm_state = dict(fm_key_state)
            loop_psg_state = dict(psg_volume)
        command = data[position]
        if command in (0x52, 0x53):
            if position + 2 >= len(data):
                raise ValueError("truncated YM2612 write")
            register = data[position + 1]
            value = data[position + 2]
            if command == 0x52 and register == 0x28:
                channel_code = value & 0x07
                local_channel = channel_code & 0x03
                channel = local_channel + (3 if channel_code & 0x04 else 0)
                if local_channel <= 2:
                    fm_key_state[channel] = value & 0xF0
            position += 3
        elif command == 0x50:
            if position + 1 >= len(data):
                raise ValueError("truncated PSG write")
            value = data[position + 1]
            if (value & 0x80) and (value & 0x10):
                channel = (value >> 5) & 0x03
                psg_volume[channel] = value & 0x0F
            position += 2
        elif command == 0x62:
            total_waits += 1
            if loop_seen:
                loop_waits += 1
            position += 1
        elif command == 0x66:
            ended = True
            position += 1
            break
        else:
            raise ValueError(f"unsupported VGM command 0x{command:02x} at {position}")

    loop_frames_by_samples = loop_samples // 735 if loop_samples % 735 == 0 else None
    total_frames_by_samples = total_samples // 735 if total_samples % 735 == 0 else None
    start_silent = (
        loop_fm_state is not None
        and all(value == 0 for value in loop_fm_state.values())
        and loop_psg_state is not None
        and all(value == 15 for value in loop_psg_state.values())
    )
    end_silent = (
        all(value == 0 for value in fm_key_state.values())
        and all(value == 15 for value in psg_volume.values())
    )
    checks = {
        "vgm_magic_and_eof": True,
        "ntsc_rate_60hz": rate == 60,
        "loop_pointer_found": loop_seen,
        "command_waits_match_expected_frames": total_waits == expected_frames,
        "loop_waits_match_expected_frames": loop_waits == expected_frames,
        "header_total_samples_match_expected_frames": total_samples == expected_frames * 735,
        "header_loop_samples_match_expected_frames": loop_samples == expected_frames * 735,
        "fm_key_state_muted_at_loop_start": start_silent,
        "fm_and_psg_muted_at_file_end": end_silent,
        "end_command_present": ended,
    }
    return {
        "vgm_version": f"{(version >> 8) & 255}.{version & 255:02x}",
        "playback_rate_hz": rate,
        "data_start": data_start,
        "loop_offset_absolute": loop_abs,
        "expected_loop_frames": expected_frames,
        "command_wait_frames": total_waits,
        "loop_command_wait_frames": loop_waits,
        "header_total_samples": total_samples,
        "header_loop_samples": loop_samples,
        "total_frames_from_header": total_frames_by_samples,
        "loop_frames_from_header": loop_frames_by_samples,
        "fm_state_at_loop_start": loop_fm_state,
        "psg_attenuation_at_loop_start": loop_psg_state,
        "fm_state_at_end": fm_key_state,
        "psg_attenuation_at_end": psg_volume,
        "checks": checks,
        "all_structural_checks_pass": all(checks.values()),
        "human_audible_seam_approved": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vgm", type=Path, default=DEFAULT_VGM)
    parser.add_argument("--score", type=Path, default=DEFAULT_SCORE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    vgm_bytes = args.vgm.read_bytes()
    score_bytes = args.score.read_bytes()
    score = json.loads(score_bytes)
    result = analyze(vgm_bytes, score["frames"])
    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "seamless_loop_report",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scene_id": "branding_sequence_v3",
        "track_id": score["track_id"],
        "status": "structure_checked_pending_human_audition",
        "score_path": args.score.relative_to(PROJECT_ROOT).as_posix(),
        "score_sha256": sha256(score_bytes),
        "vgm_path": args.vgm.relative_to(PROJECT_ROOT).as_posix(),
        "vgm_sha256": sha256(vgm_bytes),
        "structural_analysis": result,
        "audition": {
            "two_complete_cycles_listened": False,
            "click_or_pop_review": "pending human listening",
            "blastem_rom_hash": None,
            "runtime_reentry_observed": False
        },
        "blockers": ["human_two_cycle_audition_pending", "hash_bound_blastem_rom_audio_pending", "scene_reentry_pending"]
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "structural_checks_pass": result["all_structural_checks_pass"], "report": str(args.report)}, indent=2))
    if not result["all_structural_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
