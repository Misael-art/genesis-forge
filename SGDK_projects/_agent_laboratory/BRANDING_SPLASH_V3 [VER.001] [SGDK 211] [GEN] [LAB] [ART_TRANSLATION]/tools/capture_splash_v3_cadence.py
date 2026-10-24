#!/usr/bin/env python3
"""Pair APP_update boundaries with emulated VDP frames without ROM instrumentation."""
import argparse
from collections import Counter
import json
import re
import shutil
import sys
from pathlib import Path


def decode(text):
    rows = [tuple(map(int, v)) for v in re.findall(r'CADENCE (\d+) (\d+) (\d+)\r?\n', text)]
    brand = [v for v in rows if v[1] == 0]
    if len(rows) != 244 or [v[2] for v in brand] != list(range(242)):
        raise ValueError('update_count_or_logical_sequence_invalid')
    if any(b[0] <= a[0] for a, b in zip(rows, rows[1:])):
        raise ValueError('physical_frame_not_increasing')
    deltas = [b[0] - a[0] for a, b in zip(brand, brand[1:])]
    return rows, deltas


def self_check():
    text = ''.join(f'CADENCE {50+i*2} 0 {i}\n' for i in range(242)) + 'CADENCE 534 2 0\nCADENCE 590 2 0\n'
    rows, deltas = decode(text)
    assert len(rows) == 244 and sum(deltas) == 482 and Counter(deltas) == {2:241}
    try:
        decode(text.replace('CADENCE 52 0 1', 'CADENCE 52 0 2'))
    except ValueError:
        print('cadence decoder self-check passed (known gaps and malformed logical sequence)')
        return
    raise AssertionError('logical_gap_accepted')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom')
    ap.add_argument('--out')
    ap.add_argument('--self-check', action='store_true')
    a = ap.parse_args()
    self_check()
    if a.self_check:
        return 0
    if not a.rom or not a.out:
        ap.error('--rom and --out are required')
    project = Path(__file__).resolve().parents[1]
    workspace = next(p for p in project.parents if (p / 'tools/sgdk_wrapper').is_dir())
    sys.path.insert(0, str(workspace/'tools/sgdk_wrapper'))
    import blastem_native_diagnostic as native
    import blastem_maintenance as maintenance
    from artifact_paths import project_output
    rom = Path(a.rom).resolve()
    out = project_output(project, a.out, allowed=('out',))
    if out.exists():
        raise ValueError('output_must_be_new')
    symbols = {}
    for line in rom.with_name('symbol.txt').read_text().splitlines():
        fields = line.split()
        if len(fields) >= 3:
            symbols[fields[2]] = int(fields[0],16) & 0xffffff
    spec, dest, binary = maintenance.package()
    identity = maintenance.verify(spec,dest,binary)
    sha = maintenance.sha256(rom)
    out.mkdir(parents=True)
    shutil.copyfile(rom,out/'rom.bin')
    script = '\n'.join(['help','variable observed_updates 0',f'breakpoint 0x{symbols["APP_update"]:x}',
        'command 0',f'printf "CADENCE %d %d %d\\n" frame [0x{symbols["gApp"]+2:x}] [0x{symbols["gApp"]+16:x}]',
        'set observed_updates observed_updates+1','if observed_updates<244','continue','end','end','continue',
        'printf "FORGE_STOP %d PC %x MODE %x\\n" frame pc vdp:reg[1]',
        'save/b "work_ram.bin" [0xFF0000] 65536','save/b "vram.bin" vdp:vram',
        'save/w "cram.bin" vdp:cram','save/w "vsram.bin" vdp:vsram','save/b "vdp_regs.bin" vdp:reg',
        'printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame','quit'])+'\n'
    (out/'commands.txt').write_text(script)
    code,expired,display,raw = native.execute(binary,out/'rom.bin',out,script,timeout=60)
    text = raw.decode(errors='replace')
    errors = []
    graceful = bool(re.search(r'FORGE_SNAPSHOT_COMPLETE \d+\r?\n', text)) and 'Saved SRAM to ' in text
    if code or (expired and not graceful):
        errors.append(f'exit:{code}:timeout:{expired}')
    if re.search(r'Failed to eval|not a recognized command|Unexpected TOKEN', text):
        errors.append('debugger_error')
    rows, deltas = decode(text)
    if maintenance.sha256(rom) != sha or maintenance.sha256(out/'rom.bin') != sha:
        errors.append('rom_identity_changed')
    if maintenance.verify(spec,dest,binary) != identity:
        errors.append('emulator_identity_changed')
    phases = []
    for lo,hi in ((0,23),(24,83),(84,119),(120,149),(150,179),(180,209),(210,239)):
        pairs = [(x,y) for x,y in zip(rows,rows[1:]) if x[1] == y[1] == 0 and lo <= x[2] <= hi]
        values = [y[0]-x[0] for x,y in pairs]
        phases.append(dict(scene_frames=[lo,hi],updates=len(values),vblanks=sum(values),histogram=dict(Counter(values))))
    report = dict(schema='splash_v3_debugger_cadence.v2',rom_sha256=sha,
        method='Read-only APP_update breakpoint; external VDP frame paired with ROM scene/sceneFrames. Debugger-local counter only, no ROM/RAM writes.',
        emulator_identity=identity,display=display,exit_code=code,timeout_flag=expired,graceful_sram_log=graceful,
        errors=errors,samples=rows,branding_intervals=len(deltas),physical_vblanks=sum(deltas),
        vblanks_per_update_histogram=dict(Counter(deltas)),phases=phases,
        limitations=['Supplementary native route with dummy host audio; game audio driver active.',
                     'Debugger affects wall clock; intervals measure emulated VDP cadence only.',
                     'Boot before first APP_update and menu loading are outside branding intervals.'])
    report['artifacts'] = [dict(path=str(f.relative_to(out)),sha256=maintenance.sha256(f),size_bytes=f.stat().st_size)
                           for f in sorted(out.rglob('*')) if f.is_file()]
    (out/'cadence_observation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('errors','branding_intervals','physical_vblanks','vblanks_per_update_histogram','phases')},indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
