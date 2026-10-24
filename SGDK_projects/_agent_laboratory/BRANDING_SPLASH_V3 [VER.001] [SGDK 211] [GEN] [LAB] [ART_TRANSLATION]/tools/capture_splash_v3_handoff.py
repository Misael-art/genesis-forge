#!/usr/bin/env python3
"""Observe the real menu handoff and emulated pad input, without modifying RAM.

Uses the central isolated native debugger backend. This is supplementary
functional evidence; debugger pauses do not prove audiovisual cadence.
"""
import argparse
import json
import re
import shutil
import struct
import sys
from pathlib import Path


def decode_sample(data, symbols, label, physical_frame):
    if len(data) != 65536:
        raise ValueError('ram_size_invalid')
    def u16(addr):
        return struct.unpack_from('>H', data, addr & 0xffff)[0]
    def u32(addr):
        return struct.unpack_from('>I', data, addr & 0xffff)[0]
    base = symbols['gApp']
    return dict(label=label, physical_frame=physical_frame,
        scene=u32(base), total_frames=u32(base + 12), scene_frames=u16(base + 16),
        hud_countdown=data[(base + 18) & 0xffff], locked=bool(data[(base + 19) & 0xffff]),
        needs_enter=bool(data[(base + 26) & 0xffff]),
        held=u16(symbols['gInput']), pressed=u16(symbols['gInput'] + 2),
        palette_fade=bool(u16(symbols['VBlankProcess']) & 1),
        dma_queue_entries=u16(symbols['queueIndex']))


def self_check():
    data = bytearray(65536)
    data[0:4] = b'\0\0\0\2'
    data[12:20] = b'\0\0\x01\x02\0\x0c\0\x01'
    data[26] = 1
    data[0x66:0x6a] = b'\0\x10\0\x10'
    data[0x80:0x84] = b'\0\x01\0\x03'
    symbols = dict(gApp=0xff0000, gInput=0xff0066, VBlankProcess=0xff0080, queueIndex=0xff0082)
    d = decode_sample(data, symbols, 'fixture', 999)
    assert (d['scene'], d['total_frames'], d['scene_frames'], d['hud_countdown']) == (2, 258, 12, 0)
    assert d['locked'] and d['needs_enter'] and d['palette_fade']
    assert (d['held'], d['pressed'], d['dma_queue_entries']) == (16, 16, 3)
    try:
        decode_sample(data[:-1], symbols, 'bad', 0)
    except ValueError:
        return
    raise AssertionError('short_snapshot_was_accepted')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom')
    ap.add_argument('--out')
    ap.add_argument('--self-check', action='store_true')
    args = ap.parse_args()
    self_check()
    if args.self_check:
        print('handoff capture parser self-check passed (big endian fields, bool offsets, short dump rejection)')
        return 0
    if not args.rom or not args.out:
        ap.error('--rom and --out are required for capture')
    project = Path(__file__).resolve().parents[1]
    workspace = next(p for p in project.parents if (p / 'tools/sgdk_wrapper').is_dir())
    sys.path.insert(0, str(workspace / 'tools/sgdk_wrapper'))
    import blastem_native_diagnostic as native
    import blastem_maintenance as maintenance
    from artifact_paths import project_output

    rom = Path(args.rom).resolve()
    out = project_output(project, args.out, allowed=('out',))
    if out.exists():
        raise ValueError('output_must_be_new')
    symbol_path = rom.with_name('symbol.txt')
    symbols = {}
    for line in symbol_path.read_text().splitlines():
        m = re.fullmatch(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line)
        if m:
            symbols[m[2]] = int(m[1], 16) & 0xffffff
    for required in ('gApp', 'gInput', 'VBlankProcess', 'queueIndex', 'SCENE_menuEnter', 'AUDIO_startBrandBgm'):
        if required not in symbols:
            raise ValueError('symbol_missing:' + required)
    spec, dest, binary = maintenance.package()
    identity = maintenance.verify(spec, dest, binary)
    sha = maintenance.sha256(rom)
    out.mkdir(parents=True)
    shutil.copyfile(rom, out / 'rom.bin')
    shutil.copyfile(symbol_path, out / 'symbol.txt')
    samples = []
    script = ['help', 'printf "FORGE_BEGIN %d\\n" frame',
              f'breakpoint 0x{symbols["SCENE_menuEnter"]:X}', 'continue', 'delete 0']

    def snapshot(label):
        samples.append(label)
        script.extend([f'printf "HANDOFF {label} %d\\n" frame',
                       f'save/b "ram_{label}.bin" [0xFF0000] 65536'])

    snapshot('menu_entry')
    # Stop after the synchronous inherited menu load and after starting its
    # fade, rather than mistaking loader time for the fade/input window.
    script.extend([f'breakpoint 0x{symbols["AUDIO_startBrandBgm"]:X}', 'continue', 'delete 1'])
    snapshot('menu_loader_finished')
    for frame in range(1, 33):
        if frame == 3:
            # Official 1.0 binary uses binddown; its help misspells bindown.
            script.append('binddown "gamepads.1.b"')
        if frame == 8:
            script.append('bindup "gamepads.1.b"')
        script.append('frames 1')
        snapshot(f'menu_step_{frame:02}')
    script.extend(['binddown "gamepads.1.b"', 'frames 4'])
    snapshot('replay_b_held')
    script.extend(['bindup "gamepads.1.b"', 'frames 600'])
    snapshot('menu_after_replay')
    script.extend(['binddown "gamepads.1.start"', 'frames 4'])
    snapshot('start_held')
    script.extend(['bindup "gamepads.1.start"', 'frames 30'])
    snapshot('demo_settled')
    script.extend(['printf "FORGE_STOP %d PC %x MODE %x\\n" frame pc vdp:reg[1]',
                   'save/b "vram.bin" vdp:vram', 'save/w "cram.bin" vdp:cram',
                   'save/w "vsram.bin" vdp:vsram', 'save/b "vdp_regs.bin" vdp:reg',
                   'save/b "work_ram.bin" [0xFF0000] 65536',
                   'printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame', 'quit'])
    commands = '\n'.join(script) + '\n'
    (out / 'commands.txt').write_text(commands)
    code, expired, display, raw = native.execute(binary, out / 'rom.bin', out, commands, timeout=90)
    transcript = raw.decode(errors='replace')
    errors = []
    graceful_logged = bool(re.search(r'FORGE_SNAPSHOT_COMPLETE [0-9]+\r?\n', transcript)) and 'Saved SRAM to ' in transcript
    if code or (expired and not graceful_logged):
        errors.append(f'emulator_exit:{code}:timeout:{expired}')
    if re.search(r'Failed to eval|Failed to open|Unrecognized|not a valid|not a recognized command|Unexpected TOKEN|Breakpoint \d+ does not exist', transcript):
        errors.append('debugger_command_failed')
    records = []
    for label in samples:
        file = out / f'ram_{label}.bin'
        markers = re.findall(rf'HANDOFF {label} (\d+)\r?\n', transcript)
        if not file.is_file() or file.stat().st_size != 65536 or len(markers) != 1:
            errors.append('snapshot_missing:' + label)
            continue
        data = file.read_bytes()
        records.append(decode_sample(data, symbols, label, int(markers[0])))
    by_label = {r['label']: r for r in records}
    steps = [r for r in records if r['label'].startswith('menu_step_')]
    checks = {
        'entry_is_locked_menu': bool(by_label.get('menu_entry', {}).get('locked')) and by_label.get('menu_entry', {}).get('scene') == 2,
        'b_reached_rom_during_lock': any(r['locked'] and r['held'] & 0x10 for r in steps),
        'b_during_fade_did_not_leave_menu': bool(steps) and all(r['scene'] == 2 for r in steps),
        'menu_eventually_unlocked': any(not r['locked'] and not r['palette_fade'] and not r['needs_enter'] for r in steps),
        'b_after_unlock_restarted_splash': by_label.get('replay_b_held', {}).get('scene') == 0,
        'replay_returned_to_menu': by_label.get('menu_after_replay', {}).get('scene') == 2,
        'start_reached_rom': bool(by_label.get('start_held', {}).get('held', 0) & 0x80),
        'start_entered_demo': by_label.get('demo_settled', {}).get('scene') == 3,
    }
    if maintenance.sha256(rom) != sha or maintenance.sha256(out / 'rom.bin') != sha:
        errors.append('rom_identity_changed')
    if maintenance.verify(spec, dest, binary) != identity:
        errors.append('emulator_identity_changed')
    report = dict(schema_version='splash_v3_handoff_observation.v1',
        status='observed' if not errors and all(checks.values()) else 'needs_review',
        rom_sha256=sha, emulator_identity=identity, display=display,
        method='central native debugger, private Xvfb/bwrap; bindown/up emulates controller through BlastEm bindings; no RAM writes',
        audio='driver runs; host audio dummy; no listening or cadence claim',
        collector_exit=dict(code=code, timeout_flag=expired, graceful_sram_log=graceful_logged),
        sampling='Physical VDP frames sampled at debugger stop; each RAM file is one coherent CPU pause. Input held is ROM-side JOY_readJoypad output.',
        struct_layout='SGDK 68000: AppScene 32-bit, bool 8-bit, 2-byte member alignment; see inc/game_vars.h',
        limitations=['Supplementary native route does not close the canonical Flatpak gate.',
                     'Debugger sampling is not sustained performance evidence.',
                     'Finite samples do not prove every state between stops.'],
        symbols={k:hex(symbols[k]) for k in ('gApp','gInput','VBlankProcess','queueIndex','SCENE_menuEnter')},
        checks=checks, errors=errors, samples=records)
    report['artifacts'] = [{'path':str(f.relative_to(out)), 'sha256':maintenance.sha256(f), 'size_bytes':f.stat().st_size}
                           for f in sorted(out.rglob('*')) if f.is_file()]
    (out / 'handoff_observation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:report[k] for k in ('status','rom_sha256','checks','errors')}, indent=2))
    return 0 if report['status'] == 'observed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
