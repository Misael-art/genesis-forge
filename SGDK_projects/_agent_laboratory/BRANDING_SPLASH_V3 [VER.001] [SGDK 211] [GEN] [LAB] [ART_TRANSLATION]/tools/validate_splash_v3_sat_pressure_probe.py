#!/usr/bin/env python3
"""Validate actual C SAT pressure scanner against an independent line oracle."""
import hashlib
import json
import subprocess
import argparse
from pathlib import Path
from build_splash_v3_motion_lut import function


def main():
    project=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bounded',action='store_true')
    args=parser.parse_args()
    source=(project/'src/system/runtime_probe.c').read_text()
    out=project/'rascunho/sat_pressure_probe_20261016'
    reference=(out/'runtime_probe_reference.c').read_text()
    if args.bounded:
        out=project/'rascunho/bounded_sat_sweep_20261016'
        out.mkdir(exist_ok=True)
    header=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8; typedef int8_t s8; typedef uint16_t u16;
typedef int16_t s16; typedef uint32_t u32; typedef uint8_t bool;
#define TRUE 1
#define FALSE 0
#define SAT_MAX_SIZE 80
#define PROBE_SCANLINE_COUNT 224
#define PROBE_TOUCHED_WORDS 8
#define HIDDEN 1
typedef struct { u16 y; u8 size,link; u16 attribut,x; } VDPSprite;
static VDPSprite vdpSpriteCache[96];
static u16 sSatPressureDelta[225], s_peakWidth;
static bool sScanlineInvalid;
typedef struct { u8 offsetY,offsetYFlip,size,offsetX,offsetXFlip,numTile; } FrameVDPSprite;
typedef struct { s8 numSprite; FrameVDPSprite* frameVDPSprites; } Frame;
typedef struct Sprite { Frame* frame; u16 visibility; s16 y; struct Sprite* next; } Sprite;
static Sprite* firstSprite;
'''
    if args.bounded:
        header+='#define SPLASH_V3_BOUNDED_SAT_SWEEP 1\n'
    # Resolve the two mutually exclusive opening loop braces before the
    # small C-function extractor counts braces (it is not a preprocessor).
    branch='''#if defined(SPLASH_V3_BOUNDED_SAT_SWEEP)
    for (line = firstEndpoint; line <= lastEndpoint; line++) {
#else
    for (line = 0; line <= PROBE_SCANLINE_COUNT; line++) {
#endif'''
    assert source.count(branch)==1, 'bounded_loop_source_changed'
    loop='    for (line = firstEndpoint; line <= lastEndpoint; line++) {' if args.bounded else '    for (line = 0; line <= PROBE_SCANLINE_COUNT; line++) {'
    scanner_source=source.replace(branch,loop,1)
    code=header+function(scanner_source,'measure_max_scanline_sprites')+'\n'
    fallback=source[source.index('#else\n#define PROBE_TOUCHED_WORDS'):]
    for prefix,text in [('old_',reference),('fixed_',fallback)]:
        funcs='static s8 s_lineCountDelta[225]; static s16 s_lineWidthDelta[225]; static u32 s_lineTouched[8]; static u16 s_peakWidth;\n'
        funcs+=function(text,'probe_mark_line')+'\n'+function(text,'measure_max_scanline_sprites')
        for name in ('s_lineCountDelta','s_lineWidthDelta','s_lineTouched','s_peakWidth','probe_mark_line','measure_max_scanline_sprites'):
            funcs=funcs.replace(name,prefix+name)
        code+=funcs+'\n'
    code+=r'''
int main(void) {
    u32 rng=0x491ab527; int test,i,j,line,rep;
    for(test=0;test<1024;test++) {
        int order[80],n; u16 expectedCount=0,expectedWidth=0;
        rng=rng*1664525u+1013904223u; n=(int)(rng%81);
        if(test==0)n=0;
        if(test==1 || test==2 || test==3)n=80;
        memset(vdpSpriteCache,0,sizeof(vdpSpriteCache));
        for(i=0;i<80;i++)order[i]=i;
        for(i=1;i<n;i++) { int temp; rng=rng*1664525u+1013904223u;j=1+(int)(rng%(unsigned)(n-1));temp=order[i];order[i]=order[j];order[j]=temp; }
        for(i=0;i<n;i++) {
            VDPSprite *s=&vdpSpriteCache[order[i]];
            rng=rng*1664525u+1013904223u;
            s->size=(u8)((rng>>16)&255);s->y=(u16)(rng&511);s->link=i==n-1?0:(u8)order[i+1];
            if(test==1) {s->size=15;s->y=228;}
            if(test==2) {s->size=0;s->y=351;}
            if(test==3) {s->size=15;s->y=0;}
        }
        /* Unlinked garbage must not enter the pressure measurement. */
        for(i=n? n:1;i<96;i++){vdpSpriteCache[i].y=224;vdpSpriteCache[i].size=15;}
        for(line=0;line<224;line++) {
            u16 count=0,width=0;
            for(i=0;i<n;i++) {
                VDPSprite s=vdpSpriteCache[order[i]];
                int top=(int)(s.y&511)-128;
                int height=((s.size&3)+1)*8;
                if(line>=top && line<top+height) {count++;width+=(u16)((((s.size>>2)&3)+1)*8);}
            }
            if(count>expectedCount)expectedCount=count;
            if(width>expectedWidth)expectedWidth=width;
        }
        for(rep=0;rep<3;rep++) {
            u16 count=measure_max_scanline_sprites();
            if(sScanlineInvalid || count!=expectedCount || s_peakWidth!=expectedWidth) {
                fprintf(stderr,"case %d rep %d expected %u/%u got %u/%u\n",test,rep,expectedCount,expectedWidth,count,s_peakWidth);return 1;
            }
        }
    }
    /* Both malformed-link cases must fail closed and clear endpoint state. */
    memset(vdpSpriteCache,0,sizeof(vdpSpriteCache));vdpSpriteCache[0].y=228;vdpSpriteCache[0].link=127;
    if(measure_max_scanline_sprites()!=65535 || !sScanlineInvalid || s_peakWidth!=65535)return 2;
    vdpSpriteCache[0].link=1;vdpSpriteCache[1].y=228;vdpSpriteCache[1].link=1;
    if(measure_max_scanline_sprites()!=65535 || !sScanlineInvalid)return 3;
    memset(vdpSpriteCache,0,sizeof(vdpSpriteCache));
    if(measure_max_scanline_sprites()!=0 || sScanlineInvalid || s_peakWidth)return 4;
    /* Regression: enum HIDDEN=1 is not the hidden mask 0. */
    FrameVDPSprite cell={0,0,0,0,0,1};Frame frame={-127,&cell};Sprite hidden={&frame,0,228,0};firstSprite=&hidden;
    if(old_measure_max_scanline_sprites()!=1 || old_s_peakWidth!=8)return 5;
    if(fixed_measure_max_scanline_sprites()!=0 || fixed_s_peakWidth!=0)return 6;
    puts("1024 SAT cases x 3 repeats + invalid index/cycle + recovery + actual hidden-mask regression passed");
    return 0;
}
'''
    harness=out/'sat_pressure_self_check.c';harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(harness),'-o',str(out/'sat_pressure_self_check')],check=True)
    result=subprocess.check_output([str(out/'sat_pressure_self_check')],text=True).strip()
    report=dict(schema='splash_v3_sat_pressure_self_check.v1',status='passed',cases=1024,repetitions=3,
        method='Actual C scanner + independent exhaustive 224-line oracle; shuffled linked lists, clipping, width units, 80-cell peak, malformed lists and stale-buffer recovery.',
        source_sha256=hashlib.sha256(source.encode()).hexdigest(),harness_sha256=hashlib.sha256(code.encode()).hexdigest(),
        hidden_mask_bug_reproduced=True,corrected_fallback_passed=True,result=result,
        scope='Host correctness and sanitizer coverage only; runtime cost and submitted/VRAM agreement require emulator evidence.')
    report['bounded_sweep']=args.bounded
    name='splash_v3_bounded_sat_self_check_20261016.json' if args.bounded else 'splash_v3_sat_pressure_self_check_20261016.json'
    (project/'out/logs'/name).write_text(json.dumps(report,indent=2)+'\n')
    print(result)


if __name__=='__main__':
    main()
