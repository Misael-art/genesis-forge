#!/usr/bin/env python3
"""Project-owned orchestration of the central private Flatpak session backend."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    project = Path(__file__).resolve().parents[1]
    workspace = next(p for p in project.parents if (p / 'tools/sgdk_wrapper').is_dir())
    sys.path.insert(0, str(workspace / 'tools/sgdk_wrapper'))
    import session_coordinator as sc
    from artifact_paths import project_output
    sc.EVIDENCE_ROOT = project_output(project, a.out, allowed=('out',))
    start = argparse.Namespace(rom=str(Path(a.rom).resolve()), perf=False,
        set=['video/gl=off', 'video/scaling=nearest'], config=None,
        sram_from=None, audio='disk', region='U')
    video = None
    session = None
    report = dict(schema='splash_v3_handoff_av_observation.v1', input_events=[], captures=[],
                  claim_scope='supplementary_replay_menu_demo_with_disk_audio')
    try:
        sc.cmd_start(start)
        session = sc._LIVE[-1]
        sid = session['id']
        ev = Path(session['evidence_dir'])
        report.update(session=sid, rom_sha256=session['rom_sha256'], audio_driver='disk', display=session['display'])
        def capture():
            return sc.cmd_capture(argparse.Namespace(session=sid))
        report['captures'].append(capture())
        rect = sc.window_rect(session)
        args = ['ffmpeg', '-nostdin', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '60',
                '-video_size', f"{rect['w']}x{rect['h']}", '-i', f"{session['display']}+{rect['x']},{rect['y']}",
                '-t', '14', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', '-pix_fmt', 'yuv420p',
                str(ev / 'handoff_replay_video.mp4')]
        env = os.environ.copy()
        env.update(DISPLAY=session['display'], XAUTHORITY=session['xauthority'])
        with open(ev / 'ffmpeg.log', 'w') as log:
            video = subprocess.Popen(args, env=env, stdout=subprocess.DEVNULL, stderr=log)
            origin = time.monotonic()
            time.sleep(.5)
            event = sc.run_seq(session, [(0, 1, sc.MASK['B']), (12, 1, 0)])
            report['input_events'].append(dict(button='B', wall_offset_seconds=time.monotonic() - origin,
                                                bridge_confirmation=event))
            time.sleep(1.5)
            report['captures'].append(capture())
            time.sleep(6)
            report['captures'].append(capture())
            event = sc.run_seq(session, [(0, 1, sc.MASK['START']), (12, 1, 0)])
            report['input_events'].append(dict(button='START', wall_offset_seconds=time.monotonic() - origin,
                                                bridge_confirmation=event))
            time.sleep(2)
            report['captures'].append(capture())
            video.wait(timeout=15)
        report['video_exit_code'] = video.returncode
        report['health_before_stop'] = sc.health(session)
    except Exception as exc:
        report['capture_error'] = repr(exc)
        raise
    finally:
        if video and video.poll() is None:
            video.terminate()
            video.wait(timeout=8)
        if session:
            sc.cmd_stop(argparse.Namespace(session=session['id'], force=False))
            ev = Path(session['evidence_dir'])
            report['shutdown'] = sc.load(session['id']).get('shutdown')
            raw = ev / 'audio.raw'
            if raw.exists():
                subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-f', 'f32le', '-ar', '48000',
                                '-ac', '2', '-i', str(raw), '-c:a', 'pcm_s16le', str(ev / 'session_audio.wav')], check=True)
                report['audio_duration_seconds'] = raw.stat().st_size / (48000 * 2 * 4)
            report['limits'] = [
                'Video and disk audio have independent start times; no sample accurate audiovisual sync claim.',
                'SDL bridge confirmation is external input evidence; native RAM evidence separately checks game-side input.',
                'Human audio and visual approval are pending; no sustained performance claim.']
            report['artifacts'] = [dict(path=str(f.relative_to(ev)), sha256=sc.sha256(f), size_bytes=f.stat().st_size)
                                   for f in sorted(ev.iterdir()) if f.is_file()]
            (ev / 'handoff_av_observation.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(dict(evidence=str(ev), video_exit=report.get('video_exit_code'),
                                  audio_seconds=report.get('audio_duration_seconds'), shutdown=report.get('shutdown')), indent=2))


if __name__ == '__main__':
    main()
