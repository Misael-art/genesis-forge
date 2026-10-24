#!/usr/bin/env python3
"""Check actual menu target writers without publishing intermediate colors."""
from pathlib import Path
import hashlib
import json
import subprocess
from build_splash_v3_motion_lut import function


def main():
    project=Path(__file__).resolve().parents[1];source=(project/'src/scenes/scene_menu.c').read_text()
    helpers=function(source,'menuSetPalette')+'\n'+function(source,'menuSetColor')
    code=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint16_t u16;
#define SPLASH_V3_MENU_HANDOFF 1
static struct {u16 before,colors[64],after;} guarded;
#define sMenuFadeTarget guarded.colors
int main(void);
'''+helpers+r'''
int main(void){
    u16 expected[64],colors[16];unsigned cases=0;
    for(unsigned seed=0;seed<4096;seed++){
        guarded.before=guarded.after=0x3C3C;
        for(unsigned i=0;i<64;i++)sMenuFadeTarget[i]=expected[i]=0x5555;
        for(unsigned slot=0;slot<4;slot++){
            for(unsigned i=0;i<16;i++)colors[i]=(u16)(seed*16+i);
            menuSetPalette((u16)slot,colors);memcpy(expected+slot*16,colors,32);
            if(memcmp(sMenuFadeTarget,expected,sizeof(expected)))return 1;
            cases++;
        }
        for(unsigned index=0;index<64;index++){
            menuSetColor((u16)index,(u16)(seed+index));expected[index]=(u16)(seed+index);
            if(memcmp(sMenuFadeTarget,expected,sizeof(expected)))return 2;
            cases++;
        }
        menuSetColor(0,0);menuSetColor(15,0);menuSetColor(63,0xEE);menuSetColor(49,0xEE);
        if(sMenuFadeTarget[0] || sMenuFadeTarget[15] || sMenuFadeTarget[63]!=0xEE || sMenuFadeTarget[49]!=0xEE)return 3;
        if(guarded.before!=0x3C3C || guarded.after!=0x3C3C)return 4;
    }
    printf("%u target writer checks passed; all16-bit source words, four slots, all64 indices and guards\n",cases);return 0;
}
'''
    out=project/'rascunho/menu_blackout_20261016';out.mkdir(exist_ok=True);harness=out/'menu_palette_target.c';harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(harness),'-o',str(out/'menu_palette_target')],check=True)
    result=subprocess.check_output([str(out/'menu_palette_target')],text=True).strip()
    report=dict(schema='splash_v3_menu_palette_target.v1',status='passed',checks=4096*68,
                helper_sha256=hashlib.sha256(helpers.encode()).hexdigest(),source_sha256=hashlib.sha256(source.encode()).hexdigest(),result=result,
                scope='Actual HANDOFF writer branches target only RAM. Loader display/CRAM behavior and final fade/input need ROM evidence.')
    (project/'out/logs/splash_v3_menu_palette_target_20261016.json').write_text(json.dumps(report,indent=2)+'\n');print(result)


if __name__=='__main__':main()
