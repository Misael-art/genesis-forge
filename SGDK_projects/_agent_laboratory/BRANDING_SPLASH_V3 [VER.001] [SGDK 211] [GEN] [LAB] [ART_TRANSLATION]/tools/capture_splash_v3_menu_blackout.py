#!/usr/bin/env python3
"""Observe display/CRAM ownership throughout the real inherited menu loader."""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from capture_splash_v3_handoff import decode_sample, self_check


def colors(raw,order):
    if len(raw)!=128:raise ValueError('palette_size_invalid')
    return [int.from_bytes(raw[i:i+2],order) for i in range(0,128,2)]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rom',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();self_check();assert colors(bytes(128),'little')==[0]*64
    project=Path(__file__).resolve().parents[1];workspace=next(p for p in project.parents if (p/'tools/sgdk_wrapper').is_dir());sys.path.insert(0,str(workspace/'tools/sgdk_wrapper'))
    import blastem_native_diagnostic as native
    import blastem_maintenance as maintenance
    from artifact_paths import project_output
    rom=Path(a.rom).resolve();out=project_output(project,a.out,allowed=('out',))
    if out.exists():raise ValueError('output_must_be_new')
    symbols={f[2]:int(f[0],16)&0xffffff for line in rom.with_name('symbol.txt').read_text().splitlines() if len(f:=line.split())>=3}
    spec,dest,binary=maintenance.package();identity=maintenance.verify(spec,dest,binary);sha=maintenance.sha256(rom);out.mkdir(parents=True);shutil.copyfile(rom,out/'rom.bin')
    script=['help',f'breakpoint 0x{symbols["SCENE_menuEnter"]:x}','continue','delete 0'];labels=[]
    def snap(label):
        labels.append(label);script.extend([f'printf "BLACKOUT {label} %d\\n" frame',f'save/b "ram_{label}.bin" [0xFF0000] 65536',f'save/b "regs_{label}.bin" vdp:reg',f'save/w "cram_{label}.bin" vdp:cram',f'save/b "vram_{label}.bin" vdp:vram'])
    snap('menu_entry')
    script.extend([f'breakpoint 0x{symbols["PAL_setPalette"]:x}',f'condition 1 ([0x{symbols["gApp"]:x}]=0)&([0x{symbols["gApp"]+2:x}]=2)',
                   'command 1','printf "MENU_HARDWARE_PALETTE_WRITE %d\\n" frame','continue','end',
                   f'breakpoint 0x{symbols["VDP_clearPlane"]:x}','continue','delete 2'])
    snap('loader_begin')
    script.extend([f'breakpoint 0x{symbols["PAL_fadeInAll"]:x}','continue','delete 3']);snap('before_fade')
    script.extend([f'breakpoint 0x{symbols["AUDIO_startBrandBgm"]:x}','continue','delete 4']);snap('loader_done')
    script.extend([f'breakpoint 0x{symbols["INPUT_update"]:x}',f'condition 5 [0x{symbols["gApp"]+18:x}]=0','continue','delete 5']);snap('unlocked')
    script.extend(['printf "FORGE_SNAPSHOT_COMPLETE %d\\n" frame','quit']);commands='\n'.join(script)+'\n'
    if len(commands.encode())>8192:raise ValueError('debugger_script_bound_exceeded')
    (out/'commands.txt').write_text(commands);code,expired,display,raw=native.execute(binary,out/'rom.bin',out,commands,timeout=60);text=raw.decode(errors='replace');errors=[];states=[]
    if code or (expired and 'Saved SRAM to ' not in text):errors.append('collector_incomplete')
    if re.search(r'Failed to eval|not a recognized command|Unexpected TOKEN',text):errors.append('debugger_command_error')
    for label in labels:
        markers=re.findall(rf'BLACKOUT {label} (\d+)\r?\n',text)
        if len(markers)!=1:errors.append('marker_missing:'+label);continue
        ram=(out/f'ram_{label}.bin').read_bytes();regs=(out/f'regs_{label}.bin').read_bytes();pal=colors((out/f'cram_{label}.bin').read_bytes(),'little');target=symbols['sMenuFadeTarget']&0xffff
        state=decode_sample(ram,symbols,label,int(markers[0]));state.update(display_enabled=bool(regs[1]&0x40),cram_black=not any(pal),backdrop_color0=pal[0],cram=pal,target_palette=colors(ram[target:target+128],'big'));states.append(state)
    by={s['label']:s for s in states}
    if any(s['scene']!=2 for s in states):errors.append('scene_not_menu')
    if by['loader_begin']['display_enabled'] or by['before_fade']['display_enabled']:errors.append('loader_not_forced_blank')
    if by['loader_begin']['backdrop_color0'] or not by['before_fade']['cram_black'] or not by['loader_done']['cram_black']:errors.append('hardware_palette_not_held_black')
    if not by['loader_done']['display_enabled'] or not by['loader_done']['palette_fade'] or not by['loader_done']['locked']:errors.append('fade_input_handoff_invalid')
    if by['before_fade']['target_palette'][0]!=0 or not any(by['before_fade']['target_palette']):errors.append('target_palette_invalid')
    if by['unlocked']['locked'] or by['unlocked']['palette_fade'] or by['unlocked']['needs_enter'] or not by['unlocked']['display_enabled']:errors.append('destination_not_ready')
    if by['unlocked']['cram']!=by['before_fade']['target_palette']:errors.append('final_palette_not_target')
    writes=len(re.findall(r'MENU_HARDWARE_PALETTE_WRITE \d+\r?\n',text))
    if writes:errors.append(f'intermediate_source_palettes_published:{writes}')
    if maintenance.sha256(rom)!=sha or maintenance.verify(spec,dest,binary)!=identity:errors.append('source_identity_changed')
    report=dict(schema='splash_v3_menu_blackout.v1',status='passed' if not errors else 'needs_review',rom_sha256=sha,emulator_identity=identity,errors=errors,hardware_source_palette_calls=writes,states=states,
                scope='Read-only function-entry pauses and hardware palette call trace. Display held off through synchronous load, black CRAM before re-enable/fade, exact final palette and unlocked input. No host/video/audio-quality approval.')
    report['artifacts']=[dict(path=str(f.relative_to(out)),sha256=maintenance.sha256(f),size_bytes=f.stat().st_size) for f in sorted(out.rglob('*')) if f.is_file()]
    (out/'menu_blackout_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],rom_sha256=sha,errors=errors,intermediate_palette_calls=writes),indent=2))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
