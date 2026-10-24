#!/usr/bin/env python3
"""Render authored, short digital-current cues to PCM16 WAV candidates.

The source JSON is the composition contract. Outputs remain lab candidates;
the generator does not claim final audio quality or runtime playback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import wave
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_PATH = Path(__file__).with_name("splash_v3_pcm_cues.json")
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "out" / "audio" / "splash_v3_pcm"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "out" / "logs" / "splash_v3_pcm_cues_generation_20261012.json"
FPS = 60


def xorshift_noise(seed: int, count: int) -> list[float]:
    state = seed & 0xFFFFFFFF
    if state == 0:
        state = 0xA341316C
    values: list[float] = []
    for _ in range(count):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        state &= 0xFFFFFFFF
        values.append((state / 0xFFFFFFFF) * 2.0 - 1.0)
    return values


def lowpass_noise(noise: list[float], sample_rate: int,
                  cutoff_start: float, cutoff_end: float) -> list[float]:
    state = 0.0
    out: list[float] = []
    denominator = max(1, len(noise) - 1)
    for index, value in enumerate(noise):
        t = index / denominator
        cutoff = cutoff_start + (cutoff_end - cutoff_start) * t
        alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff / sample_rate)
        state += alpha * (value - state)
        out.append(state)
    return out


def normalize(samples: list[float], target_peak: float) -> list[float]:
    mean = sum(samples) / max(1, len(samples))
    centered = [sample - mean for sample in samples]
    peak = max((abs(sample) for sample in centered), default=0.0)
    if peak <= 1e-12:
        return centered
    scale = target_peak / peak
    return [sample * scale for sample in centered]


def envelope_attack_release(t: float, attack: float, release: float) -> float:
    if attack > 0 and t < attack:
        return max(0.0, min(1.0, t / attack))
    if release > 0 and t > 1.0 - release:
        return max(0.0, min(1.0, (1.0 - t) / release))
    return 1.0


def render_rising_current(cue: dict, sample_rate: int) -> list[float]:
    count = round(sample_rate * cue["render_duration_frames"] / FPS)
    noise = xorshift_noise(cue["seed"], count)
    filtered = lowpass_noise(noise, sample_rate,
                             cue["noise_cutoff_start_hz"],
                             cue["noise_cutoff_end_hz"])
    phase = 0.0
    out: list[float] = []
    for index in range(count):
        t = index / max(1, count - 1)
        freq = cue["frequency_start_hz"] + (
            cue["frequency_end_hz"] - cue["frequency_start_hz"]
        ) * (t ** 1.15)
        phase += 2.0 * math.pi * freq / sample_rate
        duration_seconds = count / sample_rate
        attack_seconds = max(0.001, cue.get("attack_seconds", 0.17))
        release_seconds = max(0.0, cue.get("release_seconds", 0.10))
        attack = min(1.0, t / attack_seconds)
        release_start = max(0.0, duration_seconds - release_seconds)
        release = (1.0 if t < release_start else
                   max(0.0, min(1.0, (duration_seconds - t) / max(0.001, release_seconds))))
        rise = 0.16 + 0.84 * (t ** 1.35)
        envelope = attack * release * rise
        sine = math.sin(phase)
        noise_layer = filtered[index]
        out.append(envelope * (0.58 * sine + cue["noise_mix"] * noise_layer))
    return out


def render_fifth_lock(cue: dict, sample_rate: int) -> list[float]:
    count = round(sample_rate * cue["render_duration_frames"] / FPS)
    noise = xorshift_noise(cue["seed"], count)
    phases = [0.0 for _ in cue["frequencies_hz"]]
    out: list[float] = []
    for index in range(count):
        t = index / sample_rate
        normalized_t = index / max(1, count - 1)
        attack = 1.0 - math.exp(-t / max(0.0001, cue["attack_seconds"]))
        decay = math.exp(-t / max(0.001, cue["decay_seconds"]))
        release = envelope_attack_release(normalized_t, 0.002, 0.10)
        tone = 0.0
        for harmonic, (freq, weight) in enumerate(zip(cue["frequencies_hz"], cue["weights"])):
            phases[harmonic] += 2.0 * math.pi * freq / sample_rate
            tone += weight * math.sin(phases[harmonic])
        click_window = math.exp(-t / 0.0018)
        out.append(release * attack * decay * tone
                   + cue["noise_click_mix"] * click_window * noise[index])
    return out


def render_tonal_sweep(cue: dict, sample_rate: int) -> list[float]:
    count = round(sample_rate * cue["render_duration_frames"] / FPS)
    noise = xorshift_noise(cue["seed"], count)
    filtered = lowpass_noise(noise, sample_rate,
                             cue["noise_cutoff_start_hz"],
                             cue["noise_cutoff_end_hz"])
    phase = 0.0
    out: list[float] = []
    for index in range(count):
        t = index / max(1, count - 1)
        freq = cue["frequency_start_hz"] + (
            cue["frequency_end_hz"] - cue["frequency_start_hz"]
        ) * (t ** 0.82)
        phase += 2.0 * math.pi * freq / sample_rate
        envelope = math.sin(math.pi * t) ** 0.72
        high_component = filtered[index] - noise[index] * 0.22
        out.append(envelope * (0.48 * math.sin(phase) + cue["noise_mix"] * high_component))
    return out


def render_soft_resolution(cue: dict, sample_rate: int) -> list[float]:
    count = round(sample_rate * cue["render_duration_frames"] / FPS)
    phases = [0.0 for _ in cue["frequencies_hz"]]
    noise = xorshift_noise(cue["seed"], count)
    out: list[float] = []
    for index in range(count):
        t = index / sample_rate
        normalized_t = index / max(1, count - 1)
        decay = math.exp(-t / max(0.001, cue["decay_seconds"]))
        release = envelope_attack_release(normalized_t, 0.008, cue["fade_out_seconds"])
        tone = 0.0
        for component, (freq, weight) in enumerate(zip(cue["frequencies_hz"], cue["weights"])):
            phases[component] += 2.0 * math.pi * freq / sample_rate
            tone += weight * math.sin(phases[component])
        soft_air = noise[index] * 0.018 * math.exp(-t / 0.035)
        out.append(release * decay * tone + soft_air)
    return out


RENDERERS = {
    "rising_current": render_rising_current,
    "fifth_lock": render_fifth_lock,
    "tonal_sweep": render_tonal_sweep,
    "soft_resolution": render_soft_resolution,
}


def write_pcm16_mono(path: Path, samples: list[float], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        packed = bytearray()
        for sample in samples:
            value = max(-1.0, min(1.0, sample))
            packed += struct.pack("<h", round(value * 32767))
        wav.writeframes(packed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", type=Path, default=DEFAULT_SOURCE_PATH)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    source_path = args.score.resolve()
    output_root = args.output_root.resolve()
    report_path = args.report.resolve()
    source_bytes = source_path.read_bytes()
    source = json.loads(source_bytes)
    builder_bytes = Path(__file__).read_bytes()
    sample_rate = source["authoring_sample_rate_hz"]
    target_peak = source["target_peak"]
    cue_reports = []
    seen_ids: set[str] = set()
    for cue in source["cues"]:
        cue_id = cue["id"]
        if cue_id in seen_ids:
            raise ValueError(f"duplicate cue id: {cue_id}")
        seen_ids.add(cue_id)
        duration_frames = cue["render_duration_frames"]
        if not 1 <= duration_frames <= cue["max_duration_frames"]:
            raise ValueError(f"{cue_id}: duration exceeds event contract")
        if cue["waveform"] not in RENDERERS:
            raise ValueError(f"{cue_id}: unknown authored waveform")
        raw = RENDERERS[cue["waveform"]](cue, sample_rate)
        samples = normalize(raw, target_peak)
        wav_path = output_root / cue["filename"]
        write_pcm16_mono(wav_path, samples, sample_rate)
        peak = max((abs(sample) for sample in samples), default=0.0)
        rms = math.sqrt(sum(sample * sample for sample in samples) / max(1, len(samples)))
        wav_bytes = wav_path.read_bytes()
        sidecar = {
            "schema_version": "1.0.0",
            "artifact_kind": "authored_pcm_cue_render",
            "id": cue_id,
            "source_kind": source["source_kind"],
            "acceptance_status": source["acceptance_status"],
            "source_path": source_path.relative_to(PROJECT_ROOT).as_posix(),
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "builder_path": Path(__file__).relative_to(PROJECT_ROOT).as_posix(),
            "builder_sha256": hashlib.sha256(builder_bytes).hexdigest(),
            "wav_path": wav_path.relative_to(PROJECT_ROOT).as_posix(),
            "wav_sha256": hashlib.sha256(wav_bytes).hexdigest(),
            "sample_rate_hz": sample_rate,
            "xgm2_sample_rate_hz": source["xgm2_sample_rate_hz"],
            "duration_frames": duration_frames,
            "duration_seconds": round(duration_frames / FPS, 6),
            "pcm_samples": len(samples),
            "peak": round(peak, 6),
            "rms": round(rms, 6),
            "clip_free_source": peak < 1.0,
            "runtime_or_human_audio_approval": False,
        }
        sidecar_path = wav_path.with_suffix(".provenance.json")
        sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
        cue_reports.append(sidecar)

    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "splash_v3_pcm_cue_generation_report",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": source_path.relative_to(PROJECT_ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "builder_path": Path(__file__).relative_to(PROJECT_ROOT).as_posix(),
        "builder_sha256": hashlib.sha256(builder_bytes).hexdigest(),
        "status": "lab_candidate",
        "cues": cue_reports,
        "limitations": [
            "This report measures generated WAV integrity only.",
            "XGM2 conversion, ROM mixing, memory budget, cue timing and human listening remain pending."
        ]
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), "cues": len(cue_reports), "status": report["status"]}, indent=2))


if __name__ == "__main__":
    main()
