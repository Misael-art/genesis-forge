#!/usr/bin/env python3
"""Freeze real SAT/VRAM at the same logical particle frames for an A/B check."""
import argparse
import json
import re
import shutil
import sys
import subprocess
from pathlib import Path


def sat_chain(vram, registers):
    if len(vram) != 65536 or len(registers) != 24 or not registers[1] & 4:
        raise ValueError('mode5_snapshot_required')
    base = (registers[5] & 0x7e) << 9
    index = 0
    seen = set()
    chain = []
    while True:
        if index in seen or index >= 80:
            raise ValueError('sat_link_invalid')
        seen.add(index)
        data = vram[base + index*8:base + (index+1)*8]
        chain.append(data.hex())
        index = data[3] & 0x7f
        if index == 0:
            return chain


def self_check():
    frames=tuple(range(24,240))
    batches=[frames[i:i+24] for i in range(0,len(frames),24)]
    assert tuple(f for batch in batches for f in batch)==frames and max(map(len,batches))==24
    data = bytearray(65536)
    regs = bytearray(24)
    regs[1] = 4
    data[3] = 1
    assert len(sat_chain(data, regs)) == 2
    assert pressure(['00e40f0000000080']*80)==(80,2560)
    assert pressure(['0000000000000000'])==(0,0)
    data[11] = 1
    try:
        sat_chain(data, regs)
    except ValueError:
        print('SAT decoder self-check passed (linked chain and cycle rejection)')
        return
    raise AssertionError('cycle_accepted')


def pressure(chain):
    cells=[bytes.fromhex(cell) for cell in chain]
    counts=[]
    widths=[]
    for line in range(224):
        count=width=0
        for cell in cells:
            top=(int.from_bytes(cell[:2],'big') & 511)-128
            height=((cell[2]&3)+1)*8
            if top<=line<top+height:
                count+=1
                width+=(((cell[2]>>2)&3)+1)*8
        counts.append(count)
        widths.append(width)
    return max(counts),max(widths)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom')
    ap.add_argument('--out')
    ap.add_argument('--self-check', action='store_true')
    ap.add_argument('--after-probe',action='store_true')
    ap.add_argument('--extended',action='store_true')
    ap.add_argument('--reveal-boundaries',action='store_true')
    ap.add_argument('--all-visible',action='store_true')
    ap.add_argument('--frame-list',help='Comma-separated logical frames; long requests use private batches of24.')
    a = ap.parse_args()
    self_check()
    if a.self_check:
        return
    if not a.rom or not a.out:
        ap.error('--rom and --out required')
    project = Path(__file__).resolve().parents[1]
    workspace = next(p for p in project.parents if (p/'tools/sgdk_wrapper').is_dir())
    sys.path.insert(0,str(workspace/'tools/sgdk_wrapper'))
    import blastem_native_diagnostic as native
    import blastem_maintenance as maintenance
    from artifact_paths import project_output
    rom = Path(a.rom).resolve()
    out = project_output(project,a.out,allowed=('out',))
    if out.exists():
        raise ValueError('output_must_be_new')
    symbols = {}
    for line in rom.with_name('symbol.txt').read_text().splitlines():
        f = line.split()
        if len(f)>=3:
            symbols[f[2]] = int(f[0],16) & 0xffffff
    spec,dest,binary = maintenance.package()
    identity = maintenance.verify(spec,dest,binary)
    sha = maintenance.sha256(rom)
    out.mkdir(parents=True)
    shutil.copyfile(rom,out/'rom.bin')
    frames = (24,40,80,90,99,109,119,120,130,139,185,192,205,210,230) if a.extended else (40,80,90,99,109,119,185,192,205)
    if a.reveal_boundaries:
        frames = tuple(sorted(set(frames) | {10,23,83,84,149,150,179,180,239}))
    if a.all_visible:
        frames = tuple(sorted(set(frames) | set(range(24,240))))
    if a.frame_list:
        if not re.fullmatch(r'\d+(,\d+)*',a.frame_list):
            ap.error('frame-list must contain comma-separated nonnegative integers')
        frames=tuple(sorted(set(map(int,a.frame_list.split(',')))))
        if not frames or frames[-1]>239:
            ap.error('frame-list must be in0..239')
    if len(frames)>24:
        samples=[]; errors=[]; child_reports=[]
        for index in range(0,len(frames),24):
            batch=frames[index:index+24]
            name=f'take_{index//24:02}'
            child=out/name
            command=[sys.executable,str(Path(__file__).resolve()),'--rom',str(rom),
                     '--out',str(child.relative_to(project)),'--frame-list',','.join(map(str,batch))]
            if a.after_probe: command.append('--after-probe')
            result=subprocess.run(command,capture_output=True,text=True)
            print(result.stdout,flush=True,end='')
            if result.returncode:
                errors.append(f'batch_failed:{name}:{result.returncode}')
                (out/f'{name}_failure.txt').write_text(result.stdout+result.stderr)
                break
            report=json.loads((child/'sat_samples.json').read_text())
            if report['rom_sha256']!=sha or report['emulator_identity']!=identity or report['errors']:
                raise ValueError('batch_identity_or_report_invalid')
            child_reports.append(dict(path=f'{name}/sat_samples.json',sha256=maintenance.sha256(child/'sat_samples.json')))
            samples.extend(dict(record,artifact_subdir=name) for record in report['samples'])
        if tuple(record['scene_frame_rendered'] for record in samples)!=frames:
            errors.append('batch_frame_coverage_incomplete')
        if maintenance.sha256(rom)!=sha or maintenance.verify(spec,dest,binary)!=identity:
            errors.append('batch_source_identity_changed')
        pressures=[pressure(record['sat_chain']) for record in samples]
        report=dict(schema='splash_v3_sat_samples.v1',rom_sha256=sha,emulator_identity=identity,errors=errors,
                    method='Private boot per batch, at most24 exact logical post-update states per debugger script.',
                    scope='All requested logical frame states across independent private boots; not uninterrupted capture, host FPS, palette quality or audio proof.',
                    samples=samples,child_reports=child_reports,
                    peak_scanline_sprites=max((v[0] for v in pressures),default=0),
                    peak_scanline_pixels=max((v[1] for v in pressures),default=0))
        report['artifacts']=[dict(path=str(f.relative_to(out)),sha256=maintenance.sha256(f),size_bytes=f.stat().st_size)
                             for f in sorted(out.rglob('*')) if f.is_file()]
        (out/'sat_samples.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(errors=errors,samples=len(samples),peak_sprites=report['peak_scanline_sprites'],peak_pixels=report['peak_scanline_pixels'])),flush=True)
        if errors:raise SystemExit(1)
        return
    stop_symbol='INPUT_update' if a.after_probe else 'MDRuntimeProbe_tick'
    script = ['help',f'breakpoint 0x{symbols[stop_symbol]:x}']
    for frame in frames:
        script += [f'condition 0 [0x{symbols["gApp"]+16:x}]={frame+1}','continue',
                   f'printf "SAT_SAMPLE {frame} %d\\n" frame',
                   f'save/b "vram_f{frame:03}.bin" vdp:vram',
                   f'save/b "regs_f{frame:03}.bin" vdp:reg',
                   f'save/w "cram_f{frame:03}.bin" vdp:cram',
                   f'save/b "ram_f{frame:03}.bin" [0xFF0000] 65536','step']
    script += ['printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame','quit']
    commands = '\n'.join(script)+'\n'
    if len(commands.encode())>8192:
        raise ValueError('native_debugger_script_bound_exceeded')
    (out/'commands.txt').write_text(commands)
    code,expired,display,raw = native.execute(binary,out/'rom.bin',out,commands,timeout=60)
    text = raw.decode(errors='replace')
    errors = []
    graceful = 'Saved SRAM to ' in text and bool(re.search(r'FORGE_SNAPSHOT_COMPLETE \d+\r?\n',text))
    if code or (expired and not graceful):
        errors.append('capture_did_not_finish')
    samples = []
    for frame in frames:
        markers = re.findall(rf'SAT_SAMPLE {frame} (\d+)\r?\n',text)
        if len(markers)!=1:
            errors.append(f'frame_marker_missing:{frame}')
            continue
        data = (out/f'ram_f{frame:03}.bin').read_bytes()
        logical = int.from_bytes(data[(symbols['gApp']+16)&0xffff:((symbols['gApp']+16)&0xffff)+2],'big')
        if logical!=frame+1:
            errors.append(f'logical_phase_mismatch:{frame}:{logical}')
        chain = sat_chain((out/f'vram_f{frame:03}.bin').read_bytes(),(out/f'regs_f{frame:03}.bin').read_bytes())
        record=dict(scene_frame_rendered=frame,logical_counter_after_update=logical,
                    physical_frame=int(markers[0]),sat_chain=chain)
        if a.after_probe:
            registers=(out/f'regs_f{frame:03}.bin').read_bytes()
            base=(registers[5]&0x7e)<<9
            synthetic=bytearray(65536)
            cache=symbols['vdpSpriteCache']&0xffff
            synthetic[base:base+640]=data[cache:cache+640]
            submitted=sat_chain(synthetic,registers)
            count,width=pressure(chain)
            def u16(address):
                index=address&0xffff
                return int.from_bytes(data[index:index+2],'big')
            def u32(address):
                index=address&0xffff
                return int.from_bytes(data[index:index+4],'big')
            probe=symbols['g_mdRuntimeProbe']
            measured=u16(probe+30*2)>0
            current_width=u16(symbols['s_peakWidth'])
            invalid=u16(probe+31*2)
            record.update(submitted_cache_matches_vram=submitted==chain,
                          oracle_scanline_count=count,oracle_scanline_pixels=width,
                          probe_measured_after_warmup=measured,
                          probe_current_width=current_width,probe_peak_count=u16(probe+14*2),
                          probe_invalid_sat_frames=invalid)
            record['probe_measurement_frames']=u16(probe+30*2)
            record['total_frames']=u32(symbols['gApp']+12)
            record['probe_last_export_total_frame']=u32(symbols['s_lastExportFrame'])
            if 'sBrandingFinalExported' in symbols:
                record['branding_final_exported']=bool(data[symbols['sBrandingFinalExported']&0xffff])
            if submitted!=chain:
                errors.append(f'submitted_sat_vram_mismatch:{frame}')
            if measured and (current_width!=width or invalid):
                errors.append(f'probe_pressure_or_validity_mismatch:{frame}')
        samples.append(record)
    if maintenance.sha256(rom)!=sha or maintenance.sha256(out/'rom.bin')!=sha:
        errors.append('rom_identity_changed')
    if maintenance.verify(spec,dest,binary)!=identity:
        errors.append('emulator_identity_changed')
    report = dict(schema='splash_v3_sat_samples.v1',rom_sha256=sha,emulator_identity=identity,errors=errors,
                  method=f'Pause at {stop_symbol} entry; coherent RAM checks logical frame. after_probe={a.after_probe}.',
                  scope='Hardware SAT chains at specified logical frames; optional post-probe submitted-cache/pressure validation. No palette/audio/total-runtime equivalence claim.',
                  samples=samples)
    report['artifacts'] = [dict(path=str(f.relative_to(out)),sha256=maintenance.sha256(f),size_bytes=f.stat().st_size)
                           for f in sorted(out.rglob('*')) if f.is_file()]
    (out/'sat_samples.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(rom_sha256=sha,errors=errors,samples=len(samples)),indent=2))
    if errors:
        raise SystemExit(1)


if __name__=='__main__':
    main()
