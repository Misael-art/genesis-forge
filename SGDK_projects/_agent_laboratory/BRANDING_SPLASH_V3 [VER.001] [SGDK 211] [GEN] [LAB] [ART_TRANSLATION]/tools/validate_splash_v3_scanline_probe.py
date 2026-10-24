#!/usr/bin/env python3
"""Compile old/new actual C scanners against an independent per-line oracle."""
import hashlib
import json
import subprocess
from pathlib import Path
from build_splash_v3_motion_lut import function


def main():
    project = Path(__file__).resolve().parents[1]
    out = project/'rascunho/scanline_probe_linear_20261016'
    old = (out/'runtime_probe_before.c').read_text()
    new = (project/'src/system/runtime_probe.c').read_text()
    header = r'''
#include <stdint.h>
#include <stdio.h>
typedef uint8_t u8; typedef int8_t s8; typedef uint16_t u16;
typedef int16_t s16; typedef uint32_t u32;
#define PROBE_SCANLINE_COUNT 224
#define PROBE_TOUCHED_WORDS 8
#define HIDDEN 0
typedef struct { u8 size; s16 offsetY; } FrameVDPSprite;
typedef struct { u16 numSprite; FrameVDPSprite* frameVDPSprites; } Frame;
typedef struct Sprite { Frame* frame; u16 visibility; s16 y; struct Sprite* next; } Sprite;
static Sprite* firstSprite;
'''
    code = header
    for prefix, source in [('old_',old),('new_',new)]:
        declarations = 'static s8 s_lineCountDelta[225]; static s16 s_lineWidthDelta[225]; static u16 s_peakWidth;\n'
        if prefix == 'old_':
            declarations += 'static u32 s_lineTouched[8];\n'
        funcs = declarations + function(source,'probe_mark_line') + '\n' + function(source,'measure_max_scanline_sprites')
        for name in ('s_lineCountDelta','s_lineWidthDelta','s_peakWidth','s_lineTouched','probe_mark_line','measure_max_scanline_sprites'):
            funcs = funcs.replace(name,prefix+name)
        code += funcs+'\n'
    code += r'''
int main(void) {
    Sprite sprites[80]; Frame frames[80]; FrameVDPSprite cells[80];
    u32 rng=0x513aac17; int test, i, line, rep;
    for (test=0; test<512; test++) {
        u16 expectedCount=0, expectedWidth=0;
        for (i=0; i<80; i++) {
            rng=rng*1664525u+1013904223u;
            cells[i].size=(u8)((rng>>16)&15);
            cells[i].offsetY=(s16)((int)((rng>>8)%17)-8);
            sprites[i].y=(s16)(128+(int)(rng%304)-40);
            sprites[i].visibility=(rng&7)!=0;
            sprites[i].frame=(rng&31)?&frames[i]:0;
            sprites[i].next=i==79?0:&sprites[i+1];
            frames[i].numSprite=1; frames[i].frameVDPSprites=&cells[i];
            if (test<3) {
                cells[i].size=15; cells[i].offsetY=0; sprites[i].visibility=1; sprites[i].frame=&frames[i];
                sprites[i].y=(s16)(128+(test==0?96:test==1?223:-32));
            }
        }
        firstSprite=sprites;
        for (line=0; line<224; line++) {
            u16 count=0,width=0;
            for (i=0; i<80; i++) if(sprites[i].frame && sprites[i].visibility) {
                int start=sprites[i].y-128+cells[i].offsetY;
                int height=((cells[i].size&3)+1)*8;
                if(line>=start && line<start+height) {count++; width+=(u16)(((cells[i].size>>2)+1)*8);}
            }
            if(count>expectedCount) expectedCount=count;
            if(width>expectedWidth) expectedWidth=width;
        }
        for(rep=0;rep<2;rep++) {
            u16 oldCount=old_measure_max_scanline_sprites();
            u16 newCount=new_measure_max_scanline_sprites();
            if(oldCount!=expectedCount || newCount!=expectedCount || old_s_peakWidth!=expectedWidth || new_s_peakWidth!=expectedWidth) {
                fprintf(stderr,"fixture %d repetition %d expected %u/%u old %u/%u new %u/%u\n",test,rep,expectedCount,expectedWidth,oldCount,old_s_peakWidth,newCount,new_s_peakWidth);return 1;
            }
        }
    }
    puts("512 cases x 2 repetitions passed: 224-line count/pixel oracle, both actual C scanners, boundary clipping, 80-link peak and reuse");
    return 0;
}
'''
    harness=out/'scanline_differential.c'
    harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(harness),'-o',str(out/'scanline_differential')],check=True)
    result=subprocess.check_output([str(out/'scanline_differential')],text=True).strip()
    report=dict(schema='splash_v3_scanline_probe_equivalence.v1',status='passed',cases=512,repetitions=2,
        method='Actual old/new C functions compiled with address/undefined sanitizers; independent exhaustive 224-line oracle.',
        old_source_sha256=hashlib.sha256(old.encode()).hexdigest(),new_source_sha256=hashlib.sha256(new.encode()).hexdigest(),
        harness_sha256=hashlib.sha256(code.encode()).hexdigest(),result=result,
        scope='Host semantic equivalence of count/width scanner; 68000 cost and runtime require separate ROM evidence.')
    (project/'out/logs/splash_v3_scanline_probe_equivalence_20261016.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)


if __name__=='__main__':
    main()
