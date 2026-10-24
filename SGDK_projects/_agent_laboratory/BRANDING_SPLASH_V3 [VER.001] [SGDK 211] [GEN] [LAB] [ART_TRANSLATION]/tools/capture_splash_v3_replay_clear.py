#!/usr/bin/env python3
"""Verify queued clears against real nonzero menu planes during splash replay."""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def planes(vram,regs):
    if len(vram)!=65536 or len(regs)!=24 or not regs[1]&4 or regs[12]&0x81!=0x81 or regs[16]!=1:
        raise ValueError('H40_64x32_snapshot_required')
    bases=((regs[2]&0x38)<<10,(regs[4]&7)<<13)
    return bases,tuple(vram[a:a+4096] for a in bases)


def scene_id(ram,address):
    start=address&0xffff
    if len(ram)!=65536 or start+4>65536:raise ValueError('scene_field_out_of_bounds')
    return int.from_bytes(ram[start:start+4],'big')


def self_check():
    ram=bytearray(65536)
    for value in [0,2,65536]:
        ram[16:20]=value.to_bytes(4,'big');assert scene_id(ram,16)==value
    regs=bytearray(24);regs[1]=4;regs[12]=0x81;regs[16]=1;regs[2]=0x30;regs[4]=7
    data=bytearray(65536);data[0xc000:0xd000]=b'\x12'*4096;data[0xe000:0xf000]=b'\x34'*4096
    bases,values=planes(data,regs);assert bases==(0xc000,0xe000) and values==(b'\x12'*4096,b'\x34'*4096)
    try:planes(data[:-1],regs)
    except ValueError:return
    raise AssertionError('short_dump_accepted')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rom',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();self_check()
    project=Path(__file__).resolve().parents[1];workspace=next(p for p in project.parents if (p/'tools/sgdk_wrapper').is_dir());sys.path.insert(0,str(workspace/'tools/sgdk_wrapper'))
    import blastem_native_diagnostic as native
    import blastem_maintenance as maintenance
    from artifact_paths import project_output
    rom=Path(a.rom).resolve();out=project_output(project,a.out,allowed=('out',))
    if out.exists():raise ValueError('output_must_be_new')
    symbols={f[2]:int(f[0],16)&0xffffff for line in rom.with_name('symbol.txt').read_text().splitlines() if len(f:=line.split())>=3}
    spec,dest,binary=maintenance.package();identity=maintenance.verify(spec,dest,binary);sha=maintenance.sha256(rom);out.mkdir(parents=True);shutil.copyfile(rom,out/'rom.bin')
    script=['help',f'breakpoint 0x{symbols["SCENE_menuEnter"]:x}','continue','delete 0',
            f'breakpoint 0x{symbols["AUDIO_startBrandBgm"]:x}','continue','delete 1','frames 40',
            f'breakpoint 0x{symbols["SCENE_brandingV3Enter"]:x}','binddown "gamepads.1.b"','continue','delete 2']
    def snap(label):
        script.extend([f'printf "CLEAR_STATE {label} %d\\n" frame',f'save/b "ram_{label}.bin" [0xFF0000] 65536',
                       f'save/b "vram_{label}.bin" vdp:vram',f'save/b "regs_{label}.bin" vdp:reg',f'save/w "cram_{label}.bin" vdp:cram'])
    snap('before_enter');script.append(f'breakpoint 0x{symbols["INPUT_update"]:x}')
    for frame in range(9):
        script.extend([f'condition 3 ([0x{symbols["gApp"]:x}]=0)&([0x{symbols["gApp"]+2:x}]=0)&([0x{symbols["gApp"]+16:x}]={frame+1})','continue'])
        snap(f'f{frame:02}')
        if frame==3:script.append('bindup "gamepads.1.b"')
        script.append('step')
    script.extend(['printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame','quit']);commands='\n'.join(script)+'\n'
    if len(commands.encode())>8192:raise ValueError('debugger_script_bound_exceeded')
    (out/'commands.txt').write_text(commands);code,expired,display,raw=native.execute(binary,out/'rom.bin',out,commands,timeout=60);text=raw.decode(errors='replace');errors=[]
    if code or (expired and 'Saved SRAM to ' not in text):errors.append('collector_incomplete')
    if re.search(r'Failed to eval|not a recognized command|Unexpected TOKEN',text):errors.append('debugger_command_error')
    bases,old=planes((out/'vram_before_enter.bin').read_bytes(),(out/'regs_before_enter.bin').read_bytes())
    nonzero=[sum(bool(int.from_bytes(v[i:i+2],'big')) for i in range(0,4096,2)) for v in old]
    if not all(nonzero):errors.append('nonzero_reference_planes_required')
    states=[]
    for frame in range(9):
        label=f'f{frame:02}';ram=(out/f'ram_{label}.bin').read_bytes();b,new=planes((out/f'vram_{label}.bin').read_bytes(),(out/f'regs_{label}.bin').read_bytes());rows=min((frame+1)*4,32);size=rows*128
        def u16(name,offset=0):
            start=(symbols[name]+offset)&0xffff;return int.from_bytes(ram[start:start+2],'big')
        logical=u16('gApp',16);scene=scene_id(ram,symbols['gApp']);accepted=[u16('sPlaneClearARows'),u16('sPlaneClearBRows')];queue=u16('queueIndex')
        if scene!=0 or logical!=frame+1 or accepted!=[rows,rows] or queue or b!=bases:errors.append(f'phase_admission_or_drain:{frame}')
        if any((out/f'cram_{label}.bin').read_bytes()):errors.append(f'palette_not_black:{frame}')
        for index,v in enumerate(new):
            if v[:size]!=bytes(size) or v[size:]!=old[index][size:]:errors.append(f'plane_clear_or_untouched_region_mismatch:{frame}:{index}')
        markers=re.findall(rf'CLEAR_STATE {label} (\d+)\r?\n',text)
        if len(markers)!=1:errors.append(f'physical_marker_missing:{frame}')
        states.append(dict(scene_id=scene,scene_frame_rendered=frame,logical_counter=logical,rows_cleared=rows,submitted_rows=accepted,queue_after_vblank=queue,physical_frame=int(markers[0]) if markers else None))
    if maintenance.sha256(rom)!=sha or maintenance.verify(spec,dest,binary)!=identity:errors.append('source_identity_changed')
    report=dict(schema='splash_v3_replay_clear.v1',status='passed' if not errors else 'needs_review',rom_sha256=sha,emulator_identity=identity,errors=errors,
                method='Cold boot to inherited menu, wait for fade, replay via native controller B; no RAM writes. Pause after each real VBlank/probe.',
                prior_nonzero_tilemap_words=nonzero,states=states,
                scope='Actual nonzero menu planes clear four rows per frame, exact untouched suffix, all32 rows by F7, empty DMA queue and black CRAM. Separate from host lifetime fixture and continuous cadence measurement.')
    report['artifacts']=[dict(path=str(f.relative_to(out)),sha256=maintenance.sha256(f),size_bytes=f.stat().st_size) for f in sorted(out.rglob('*')) if f.is_file()]
    (out/'replay_clear_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],rom_sha256=sha,errors=errors,prior_nonzero_words=nonzero),indent=2))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
