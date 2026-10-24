#!/usr/bin/env python3
"""Render the authored Splash V3 FM/PSG score to a deterministic NTSC VGM.

This is an offline composer/export helper. It does not claim human approval,
runtime timing, XGM2 playback quality, or final status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCORE_PATH = Path(__file__).with_name("splash_v3_music_score.json")
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "out" / "audio" / "splash_v3_music.vgm"

VGM_HEADER_BYTES = 0x100
NTSC_FPS = 60
NTSC_SAMPLES_PER_FRAME = 735
YM2612_CLOCK = 7_670_454
SN76489_CLOCK = 3_579_545

OP_REGISTER_OFFSETS = (0, 8, 4, 12)


def checked_integer(value: object, low: int, high: int, field: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{field}: expected integer {low}..{high}")
    return value


def validate_score(score: dict) -> None:
    if score.get("schema_version") != "1.0.0":
        raise ValueError("unsupported score schema")
    if score.get("region") != "ntsc":
        raise ValueError("Splash V3 score must explicitly target NTSC")
    meter = score.get("meter")
    if score.get("tempo_bpm") != 120 or not isinstance(meter, str) or not meter.endswith("/8"):
        raise ValueError("score timing must use 120 BPM and an eighth-note meter")
    try:
        eighths_per_bar = int(meter.split("/", 1)[0])
    except (TypeError, ValueError):
        raise ValueError("meter must be written as numerator/8") from None
    if not 1 <= eighths_per_bar <= 12:
        raise ValueError("meter numerator must be between 1 and 12 eighth notes")
    if score.get("eighth_note_frames") != 15 or score.get("bar_frames") != eighths_per_bar * 15:
        raise ValueError("score grid does not match its eighth-note meter at 120 BPM")
    grouping = score.get("grouping_eighths")
    if not isinstance(grouping, list) or not grouping or sum(grouping) != eighths_per_bar:
        raise ValueError("grouping_eighths must sum to the meter numerator")
    frames = checked_integer(score.get("frames"), 1, NTSC_FPS * 600, "frames")
    bar_count = checked_integer(score.get("bar_count"), 1, 32, "bar_count")
    if frames != score["bar_frames"] * bar_count:
        raise ValueError("score length must equal its authored count of meter-sized bars")
    if score.get("loop_frame") != 0:
        raise ValueError("the exported music loop must begin at frame zero")

    patches = score.get("fm_patches")
    if not isinstance(patches, list) or len(patches) != 4:
        raise ValueError("exactly four authored FM patches are required")
    patch_map: dict[str, dict] = {}
    used_channels: set[int] = set()
    for patch in patches:
        patch_id = patch.get("id")
        if not isinstance(patch_id, str) or patch_id in patch_map:
            raise ValueError("FM patch IDs must be unique strings")
        channel = checked_integer(patch.get("channel"), 0, 3, patch_id + ".channel")
        if channel in used_channels:
            raise ValueError("FM channels 0-3 must have one owner each")
        used_channels.add(channel)
        checked_integer(patch.get("algorithm"), 0, 7, patch_id + ".algorithm")
        checked_integer(patch.get("feedback"), 0, 7, patch_id + ".feedback")
        checked_integer(patch.get("pan"), 1, 3, patch_id + ".pan")
        operators = patch.get("operators")
        if not isinstance(operators, list) or len(operators) != 4:
            raise ValueError(patch_id + ": expected four operators")
        for op_index, operator in enumerate(operators):
            name = f"{patch_id}.operator{op_index + 1}"
            for key, low, high in (
                ("detune", 0, 7), ("multiple", 0, 15),
                ("total_level", 0, 127), ("rate_scale", 0, 3),
                ("attack", 0, 31), ("am_enable", 0, 1),
                ("decay1", 0, 31), ("decay2", 0, 31),
                ("sustain_level", 0, 15), ("release", 0, 15),
                ("ssg_eg", 0, 15),
            ):
                checked_integer(operator.get(key), low, high, name + "." + key)
        patch_map[patch_id] = patch
    if used_channels != {0, 1, 2, 3}:
        raise ValueError("FM channel ownership must cover channels 0-3 exactly")

    occupied: dict[tuple[str, int], list[tuple[int, int]]] = {}
    fm_notes = score.get("fm_notes")
    if not isinstance(fm_notes, list) or not fm_notes:
        raise ValueError("fm_notes must be nonempty")
    for note in fm_notes:
        instrument = note.get("instrument")
        if instrument not in patch_map:
            raise ValueError(f"unknown FM instrument: {instrument}")
        frame = checked_integer(note.get("frame"), 0, frames - 1, "fm.frame")
        duration = checked_integer(note.get("duration"), 1, frames - frame - 1, "fm.duration")
        checked_integer(note.get("midi"), 0, 127, "fm.midi")
        channel = patch_map[instrument]["channel"]
        occupied.setdefault(("fm", channel), []).append((frame, frame + duration))

    psg_notes = score.get("psg_notes")
    if not isinstance(psg_notes, list):
        raise ValueError("psg_notes must be a list")
    for note in psg_notes:
        channel = checked_integer(note.get("channel"), 0, 2, "psg.channel")
        frame = checked_integer(note.get("frame"), 0, frames - 1, "psg.frame")
        duration = checked_integer(note.get("duration"), 1, frames - frame - 1, "psg.duration")
        checked_integer(note.get("midi"), 0, 127, "psg.midi")
        checked_integer(note.get("attenuation", 4), 0, 14, "psg.attenuation")
        occupied.setdefault(("psg", channel), []).append((frame, frame + duration))

    for voice, intervals in occupied.items():
        intervals.sort()
        for prior, current in zip(intervals, intervals[1:]):
            if current[0] < prior[1]:
                raise ValueError(f"overlapping notes on {voice}")


def ym_write(register: int, value: int, port: int = 0) -> bytes:
    return bytes((0x52 if port == 0 else 0x53, register & 0xFF, value & 0xFF))


def psg_write(value: int) -> bytes:
    return bytes((0x50, value & 0xFF))


def psg_off(channel: int) -> bytes:
    return psg_write(0x90 | (channel << 5) | 0x0F)


def psg_note_on(channel: int, midi: int, attenuation: int) -> bytes:
    period = round(SN76489_CLOCK / (32 * 440 * 2 ** ((midi - 69) / 12)))
    if not 1 <= period <= 1023:
        raise ValueError(f"PSG note outside tone range: MIDI {midi}")
    return (
        psg_write(0x80 | (channel << 5) | (period & 0x0F))
        + psg_write((period >> 4) & 0x3F)
        + psg_write(0x90 | (channel << 5) | attenuation)
    )


def midi_fnum_block(midi: int) -> tuple[int, int]:
    hz = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    block = 4
    while hz < 200.0 and block > 0:
        hz *= 2.0
        block -= 1
    while hz > 800.0 and block < 7:
        hz /= 2.0
        block += 1
    fnum = round((hz * 144 * (1 << (20 - block))) / YM2612_CLOCK)
    return max(1, min(0x7FF, fnum)), block


def fm_frequency(channel: int, midi: int) -> bytes:
    port, local_channel = divmod(channel, 3)
    fnum, block = midi_fnum_block(midi)
    high = ((block & 7) << 3) | ((fnum >> 8) & 7)
    return ym_write(0xA4 + local_channel, high, port) + ym_write(0xA0 + local_channel, fnum & 0xFF, port)


def fm_key(channel: int, enabled: bool) -> bytes:
    channel_code = (channel % 3) | (0x04 if channel >= 3 else 0)
    return ym_write(0x28, (0xF0 if enabled else 0) | channel_code)


def fm_patch_registers(patch: dict) -> bytes:
    channel = patch["channel"]
    port, local_channel = divmod(channel, 3)
    stream = bytearray()
    stream += ym_write(0xB0 + local_channel, (patch["feedback"] << 3) | patch["algorithm"], port)
    pan = (0x80 if patch["pan"] & 1 else 0) | (0x40 if patch["pan"] & 2 else 0)
    stream += ym_write(0xB4 + local_channel, pan, port)
    for op_index, operator in enumerate(patch["operators"]):
        base = local_channel + OP_REGISTER_OFFSETS[op_index]
        stream += ym_write(0x30 + base, (operator["detune"] << 4) | operator["multiple"], port)
        stream += ym_write(0x40 + base, operator["total_level"], port)
        stream += ym_write(0x50 + base, (operator["rate_scale"] << 6) | operator["attack"], port)
        stream += ym_write(0x60 + base, (operator["am_enable"] << 7) | operator["decay1"], port)
        stream += ym_write(0x70 + base, operator["decay2"], port)
        stream += ym_write(0x80 + base, (operator["sustain_level"] << 4) | operator["release"], port)
        stream += ym_write(0x90 + base, operator["ssg_eg"], port)
    return bytes(stream)


def compile_vgm(score: dict) -> bytes:
    validate_score(score)
    frames = score["frames"]
    patches = {patch["id"]: patch for patch in score["fm_patches"]}
    timeline: dict[int, dict[str, list[dict]]] = {}

    def add_event(frame: int, kind: str, event: dict) -> None:
        timeline.setdefault(frame, {"off": [], "on": []})[kind].append(event)

    for note in score["fm_notes"]:
        add_event(note["frame"], "on", note)
        add_event(note["frame"] + note["duration"], "off", note)
    for note in score["psg_notes"]:
        add_event(note["frame"], "on", note)
        add_event(note["frame"] + note["duration"], "off", note)

    stream = bytearray()
    stream += ym_write(0x22, 0x00)  # LFO off
    stream += ym_write(0x27, 0x00)  # timers and channel mode reset
    stream += ym_write(0x2B, 0x00)  # DAC disabled; XGM2 owns PCM at runtime
    for channel in range(6):
        stream += fm_key(channel, False)
    for channel in range(4):
        stream += psg_off(channel)
    for patch in score["fm_patches"]:
        stream += fm_patch_registers(patch)

    loop_offset = None
    for frame in range(frames):
        if frame == score["loop_frame"]:
            loop_offset = VGM_HEADER_BYTES + len(stream)
        events = timeline.get(frame, {"off": [], "on": []})
        for event in sorted(events["off"], key=lambda item: (item.get("instrument", ""), item.get("channel", 0))):
            if "instrument" in event:
                stream += fm_key(patches[event["instrument"]]["channel"], False)
            else:
                stream += psg_off(event["channel"])
        for event in sorted(events["on"], key=lambda item: (item.get("instrument", ""), item.get("channel", 0))):
            if "instrument" in event:
                channel = patches[event["instrument"]]["channel"]
                stream += fm_frequency(channel, event["midi"])
                stream += fm_key(channel, True)
            else:
                stream += psg_note_on(event["channel"], event["midi"], event.get("attenuation", 4))
        stream.append(0x62)  # wait exactly one NTSC VGM frame (735 samples)
    stream.append(0x66)

    if loop_offset is None:
        raise ValueError("loop_frame was not emitted")
    header = bytearray(VGM_HEADER_BYTES)
    header[0:4] = b"Vgm "
    values = {
        0x04: VGM_HEADER_BYTES + len(stream) - 4,
        0x08: 0x00000170,
        0x0C: SN76489_CLOCK,
        0x18: frames * NTSC_SAMPLES_PER_FRAME,
        0x1C: loop_offset - 0x1C,
        0x20: frames * NTSC_SAMPLES_PER_FRAME,
        0x24: NTSC_FPS,
        0x2C: YM2612_CLOCK,
        0x34: VGM_HEADER_BYTES - 0x34,
    }
    for offset, value in values.items():
        struct.pack_into("<I", header, offset, value)
    struct.pack_into("<H", header, 0x28, 9)  # SN76489 feedback
    header[0x2A] = 16  # SN76489 shift register width
    return bytes(header + stream)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", type=Path, default=DEFAULT_SCORE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    score_path = args.score.resolve()
    output_path = args.output.resolve()
    provenance_path = output_path.with_suffix(".provenance.json")
    source = score_path.read_bytes()
    score = json.loads(source)
    data = compile_vgm(score)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    metadata = {
        "schema_version": "1.0.0",
        "artifact_kind": "authored_music_render",
        "track_id": score["track_id"],
        "source_kind": "procedural_composed_from_authored",
        "acceptance_status": "lab",
        "score_path": score_path.relative_to(PROJECT_ROOT).as_posix(),
        "score_sha256": hashlib.sha256(source).hexdigest(),
        "builder_path": Path(__file__).relative_to(PROJECT_ROOT).as_posix(),
        "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "vgm_path": output_path.relative_to(PROJECT_ROOT).as_posix(),
        "vgm_sha256": hashlib.sha256(data).hexdigest(),
        "vgm_bytes": len(data),
        "region": "ntsc",
        "frames": score["frames"],
        "loop_frames": score["frames"],
        "loop_seconds": score["frames"] / NTSC_FPS,
        "meter": score["meter"],
        "tempo_bpm": score["tempo_bpm"],
        "scope": "FM channels 0-3 plus PSG tone channels 0-1; no PCM; no XGM2 runtime or human listening proof",
    }
    provenance_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"vgm": str(output_path), **{k: metadata[k] for k in ("vgm_sha256", "vgm_bytes", "frames", "loop_seconds")}}, indent=2))


if __name__ == "__main__":
    main()
