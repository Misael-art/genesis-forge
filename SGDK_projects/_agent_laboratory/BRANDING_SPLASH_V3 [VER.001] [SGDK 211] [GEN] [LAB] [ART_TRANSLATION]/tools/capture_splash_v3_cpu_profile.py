#!/usr/bin/env python3
"""Read-only block elapsed-time profile using BlastEm 1.0's cycle variable."""
import argparse
import json
import re
import shutil
import statistics
import sys
from pathlib import Path

EVENTS = ['INPUT_update', 'APP_update', 'SPR_update', 'MDRuntimeProbe_sampleDmaQueue',
          'SYS_doVBlankProcess', 'MDRuntimeProbe_tick']
FRAME_MCLKS = 3420 * 262


def decode(text, start, end):
    rows = [dict(event=m[0], frame=int(m[1]), cycle=int(m[2]), logical=int(m[3]))
            for m in re.findall(r'CPROF (\w+) (\d+) (\d+) (\d+)\r?\n', text)]
    if not rows or any(b['cycle'] < a['cycle'] for a,b in zip(rows,rows[1:])):
        raise ValueError('cycle_counter_missing_or_renormalized')
    inputs = [i for i,row in enumerate(rows) if row['event']=='INPUT_update']
    if [rows[i]['logical'] for i in inputs] != list(range(start,end+1)):
        raise ValueError('logical_window_incomplete')
    records = []
    for i,j in zip(inputs,inputs[1:]):
        group = rows[i:j]
        if [r['event'] for r in group] != EVENTS:
            raise ValueError('block_event_order_or_coverage_invalid')
        next_input = rows[j]
        values = group+[next_input]
        deltas = [b['cycle']-a['cycle'] for a,b in zip(values,values[1:])]
        if any(v<0 for v in deltas):
            raise ValueError('negative_elapsed_time')
        records.append(dict(scene_frame=group[0]['logical'],physical_start_frame=group[0]['frame'],
            physical_end_frame=next_input['frame'],mclks_total=sum(deltas),
            elapsed_mclks=dict(zip(['input','app_scene_audio','sprite_engine','dma_queue_sample','vblank_wait_and_work','probe_and_loop'],deltas))))
    return rows, records


def self_check():
    rows=[]
    for logical in range(2):
        for index,event in enumerate(EVENTS):
            rows.append(f'CPROF {event} {logical} {logical*FRAME_MCLKS+index*100} {logical}\n')
    rows.append(f'CPROF INPUT_update 2 {2*FRAME_MCLKS} 2\n')
    text=''.join(rows)
    _, records=decode(text,0,2)
    assert all(r['mclks_total']==FRAME_MCLKS for r in records)
    assert records[0]['elapsed_mclks']['probe_and_loop']==FRAME_MCLKS-500
    for bad in [text.replace('CPROF APP_update 0 100 0\n',''),text.replace('CPROF APP_update 0 100 0','CPROF APP_update 0 1 0').replace('CPROF INPUT_update 0 0 0','CPROF INPUT_update 0 2 0')]:
        try:
            decode(bad,0,2)
        except ValueError:
            continue
        raise AssertionError('broken_profile_was_accepted')
    good=f'CLOCK_BEGIN 240 1000000\nCLOCK_END 245 {1000000+5*FRAME_MCLKS}\n'
    assert decode_calibration(good)['residual_masterclocks']==0
    try:
        decode_calibration(good.replace(str(1000000+5*FRAME_MCLKS),'1000010'))
    except ValueError:
        pass
    else:
        raise AssertionError('wrong_clock_scale_accepted')
    print('cycle profile self-check passed (known totals, missing block, counter reversal, clock scale)')


def decode_calibration(text):
    matches=re.findall(r'CLOCK_(BEGIN|END) (\d+) (\d+)\r?\n',text)
    if len(matches)!=2 or [m[0] for m in matches]!=['BEGIN','END']:
        raise ValueError('clock_markers_missing')
    frames=int(matches[1][1])-int(matches[0][1])
    clocks=int(matches[1][2])-int(matches[0][2])
    if frames!=5 or abs(clocks-frames*FRAME_MCLKS)>3420:
        raise ValueError('fixed_frame_clock_calibration_failed')
    return dict(physical_frames=frames,masterclocks=clocks,expected_masterclocks=frames*FRAME_MCLKS,
                residual_masterclocks=clocks-frames*FRAME_MCLKS)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom')
    ap.add_argument('--out')
    ap.add_argument('--start',type=int,default=80)
    ap.add_argument('--end',type=int,default=140)
    ap.add_argument('--self-check',action='store_true')
    ap.add_argument('--calibrate',action='store_true')
    ap.add_argument('--calibration',type=Path)
    a=ap.parse_args()
    self_check()
    if a.self_check:
        return 0
    if not a.rom or not a.out or not 0<=a.start<a.end<=240:
        ap.error('--rom/--out and 0<=start<end<=240 required')
    project=Path(__file__).resolve().parents[1]
    workspace=next(p for p in project.parents if (p/'tools/sgdk_wrapper').is_dir())
    sys.path.insert(0,str(workspace/'tools/sgdk_wrapper'))
    import blastem_native_diagnostic as native
    import blastem_maintenance as maintenance
    from artifact_paths import project_output
    rom=Path(a.rom).resolve();out=project_output(project,a.out,allowed=('out',))
    if out.exists():
        raise ValueError('output_must_be_new')
    symbols={}
    for line in rom.with_name('symbol.txt').read_text().splitlines():
        f=line.split()
        if len(f)>=3:
            symbols[f[2]]=int(f[0],16)&0xffffff
    spec,dest,binary=maintenance.package();identity=maintenance.verify(spec,dest,binary)
    sha=maintenance.sha256(rom);out.mkdir(parents=True);shutil.copyfile(rom,out/'rom.bin')
    if a.calibrate:
        commands='\n'.join(['frames 240','printf "CLOCK_BEGIN %d %d\\n" frame cycle','frames 5',
                            'printf "CLOCK_END %d %d\\n" frame cycle',
                            'save/b "work_ram.bin" [0xFF0000] 65536',
                            'printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame','quit'])+'\n'
        (out/'commands.txt').write_text(commands)
        code,expired,display,raw=native.execute(binary,out/'rom.bin',out,commands,timeout=60)
        text=raw.decode(errors='replace')
        values=decode_calibration(text)
        if code or (expired and 'Saved SRAM to ' not in text):
            raise ValueError('calibration_collector_failed')
        if maintenance.sha256(rom)!=sha or maintenance.sha256(out/'rom.bin')!=sha:
            raise ValueError('calibration_rom_identity_changed')
        report=dict(schema='splash_v3_debugger_clock_calibration.v1',status='passed',rom_sha256=sha,
                    emulator_identity=identity,measurement=values,
                    method='Five explicit VDP frames after boot; instruction-boundary tolerance one scanline, not arbitrary APP_update phases.')
        (out/'clock_calibration.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
        return 0
    if not a.calibration:
        raise ValueError('explicit_clock_calibration_report_required')
    calibration=json.loads(a.calibration.read_text())
    if calibration['status']!='passed' or calibration['emulator_identity']!=identity:
        raise ValueError('clock_calibration_identity_invalid')
    frame_address=symbols['gApp']+16
    condition=f'([0x{symbols["gApp"]+2:x}]=0)&([0x{frame_address:x}]>={a.start})&([0x{frame_address:x}]<={a.end})'
    script=['help']
    for index,event in enumerate(EVENTS):
        script += [f'breakpoint 0x{symbols[event]:x}',f'condition {index} {condition}',f'command {index}',
                   f'printf "CPROF {event} %d %d %d\\n" frame cycle [0x{frame_address:x}]']
        if event=='INPUT_update':
            script += [f'if [0x{frame_address:x}]<{a.end}','continue','end']
        else:
            script += ['continue']
        script += ['end']
    script += ['continue','save/b "work_ram.bin" [0xFF0000] 65536',
               'save/b "vram.bin" vdp:vram','save/w "cram.bin" vdp:cram',
               'save/w "vsram.bin" vdp:vsram','save/b "vdp_regs.bin" vdp:reg',
               'printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame','quit']
    commands='\n'.join(script)+'\n';(out/'commands.txt').write_text(commands)
    code,expired,display,raw=native.execute(binary,out/'rom.bin',out,commands,timeout=60)
    text=raw.decode(errors='replace');errors=[]
    if code or (expired and 'Saved SRAM to ' not in text):
        errors.append('collector_did_not_finish')
    if re.search(r'Failed to eval|not a recognized command|Unexpected TOKEN|does not exist',text):
        errors.append('debugger_command_failed')
    rows,records=decode(text,a.start,a.end)
    if maintenance.sha256(rom)!=sha or maintenance.sha256(out/'rom.bin')!=sha:
        errors.append('rom_identity_changed')
    if maintenance.verify(spec,dest,binary)!=identity:
        errors.append('emulator_identity_changed')
    convergence=[r for r in records if 90<=r['scene_frame']<=119]
    keys=list(records[0]['elapsed_mclks'])
    medians={k:statistics.median(r['elapsed_mclks'][k] for r in convergence) for k in keys} if convergence else {}
    report=dict(schema='splash_v3_external_cycle_profile.v1',rom_sha256=sha,emulator_identity=identity,
        unit='Master clock cycles from debugger m68k cycle variable. Default divider 7; includes interrupts and bus waits.',
        method='Six read-only function-entry breakpoints. No ROM/RAM writes or ROM instrumentation. Values between successive entries include call/loop overhead.',
        reference='rascunho/blastem_v1_0_debug_reference/source_manifest.json',
        interval=[a.start,a.end],errors=errors,ntsc_frame_masterclocks=FRAME_MCLKS,
        fixed_frame_clock_calibration=str(a.calibration),convergence_median_elapsed_mclks=medians,samples=rows,records=records,
        limitations=['Private native diagnostic route, dummy host audio, game audio driver active.',
                     'Elapsed block time includes any interrupt or wait inside it; this is not an exclusive instruction-cycle profile.',
                     'No delivery gate or quality approval follows from profiling.'])
    report['artifacts']=[dict(path=str(f.relative_to(out)),sha256=maintenance.sha256(f),size_bytes=f.stat().st_size)
                         for f in sorted(out.rglob('*')) if f.is_file()]
    (out/'cpu_block_profile.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('rom_sha256','errors','fixed_frame_clock_calibration','convergence_median_elapsed_mclks')},indent=2))
    return 1 if errors else 0


if __name__=='__main__':
    raise SystemExit(main())
