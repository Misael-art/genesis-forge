#!/usr/bin/env python3
"""Compare the guarded attribute update with the actual SGDK 2.11 setter."""
import hashlib
import json
import re
import subprocess
import argparse
from pathlib import Path
from build_splash_v3_motion_lut import function


def main():
    project=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=project/'rascunho/manual_tile_path_20261016/scene_branding_v3_rejected_r1.c',
                        help='Preserved rejected experiment by default; the active scene uses the ordinary SGDK setter.')
    args=parser.parse_args()
    workspace=next(p for p in project.parents if (p/'sdk/sgdk-2.11').is_dir())
    sdk=workspace/'sdk/sgdk-2.11'
    library=(sdk/'src/sprite_eng.c').read_text()
    source=args.source.read_text()
    definitions=''
    for file,names in [('inc/vdp.h',['TILE_SIZE','TILE_INDEX_MASK']),
                       ('inc/vdp_tile.h',['TILE_ATTR_PRIORITY_SFT','TILE_ATTR_PALETTE_SFT','TILE_ATTR_VFLIP_SFT','TILE_ATTR_HFLIP_SFT','TILE_ATTR_PRIORITY_MASK','TILE_ATTR_PALETTE_MASK','TILE_ATTR_VFLIP_MASK','TILE_ATTR_HFLIP_MASK','TILE_ATTR_MASK']),
                       ('inc/sprite_eng.h',['SPR_FLAG_AUTO_VRAM_ALLOC','SPR_FLAG_AUTO_TILE_UPLOAD']),
                       ('src/sprite_eng.c',['NEED_TILES_UPLOAD'])]:
        text=(sdk/file).read_text()
        for name in names:
            definitions+=re.search(r'^#define '+name+r'\s+[^\n]+',text,re.M)[0]+'\n'
    actual=function(library.replace('bool SPR_setVRAMTileIndex(', 'static bool SPR_setVRAMTileIndex('),'SPR_setVRAMTileIndex')
    actual=actual.replace('SPR_setVRAMTileIndex','reference_setter')
    header=r'''
#include <stdint.h>
#include <stdio.h>
typedef uint8_t bool;typedef uint16_t u16;typedef int16_t s16;
#define TRUE 1
#define FALSE 0
#define START_PROFIL
#define END_PROFIL(x)
#define checkSpriteValid(a,b) ((void)0)
#define SPLASH_V3_MANUAL_TILE_FASTPATH 1
typedef struct { u16 maxNumTile; } SpriteDefinition;
typedef struct {u16 status,attribut;SpriteDefinition* definition;} Sprite;
static int vram,allocCalls,freeCalls,apiCalls;static u16 freedIndex;
static bool sParticleUniformGeometry;
static s16 VRAM_alloc(int *region,u16 count){(void)region;(void)count;allocCalls++;return 42;}
static void VRAM_free(int *region,u16 index){(void)region;freedIndex=index;freeCalls++;}
'''
    code=header+definitions+actual+r'''
static bool SPR_setVRAMTileIndex(Sprite *sprite,s16 value){apiCalls++;return reference_setter(sprite,value);}
'''+function(source,'v3SetPreloadedParticleTile')+r'''
int main(void){
    const u16 indices[]={0,1,96,1740,2047,65535};
    SpriteDefinition definition={1};unsigned cases=0;
    for(int geometry=0;geometry<2;geometry++)for(int flags=0;flags<4;flags++)for(int tags=0;tags<32;tags++)for(int old=0;old<5;old++)for(int next=0;next<6;next++){
        Sprite ref={(u16)(0x8002|(flags&1?SPR_FLAG_AUTO_VRAM_ALLOC:0)|(flags&2?SPR_FLAG_AUTO_TILE_UPLOAD:0)),(u16)((tags<<11)|indices[old]),&definition};
        Sprite fast=ref;int expectedAlloc,expectedFree;u16 expectedFreed;
        allocCalls=freeCalls=apiCalls=0;freedIndex=0;
        reference_setter(&ref,(s16)indices[next]);expectedAlloc=allocCalls;expectedFree=freeCalls;expectedFreed=freedIndex;
        allocCalls=freeCalls=apiCalls=0;freedIndex=0;sParticleUniformGeometry=(bool)geometry;
        v3SetPreloadedParticleTile(&fast,indices[next]);
        int eligible=geometry && flags==0 && indices[next]<=TILE_INDEX_MASK;
        if(ref.status!=fast.status || ref.attribut!=fast.attribut || allocCalls!=expectedAlloc || freeCalls!=expectedFree || freedIndex!=expectedFreed || apiCalls!=(eligible?0:1)){
            fprintf(stderr,"case %u mismatch geometry=%d flags=%d tags=%d old=%u next=%u\n",cases,geometry,flags,tags,indices[old],indices[next]);return 1;
        }
        cases++;
    }
    printf("%u actual-SGDK differential cases passed: attributes, status, allocation/release calls and guarded fallback\n",cases);
    return 0;
}
'''
    out=project/'rascunho/manual_tile_path_20261016';out.mkdir(parents=True,exist_ok=True)
    harness=out/'manual_tile_differential.c';harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(harness),'-o',str(out/'manual_tile_differential')],check=True)
    result=subprocess.check_output([str(out/'manual_tile_differential')],text=True).strip()
    report=dict(schema='splash_v3_manual_tile_differential.v1',status='passed',cases=7680,
        sgdk_setter_sha256=hashlib.sha256(actual.encode()).hexdigest(),harness_sha256=hashlib.sha256(code.encode()).hexdigest(),
        source_sha256=hashlib.sha256(source.encode()).hexdigest(),result=result,
        scope='Actual SGDK setter extracted from workspace 2.11. Host stub allocator checks call equivalence, not hardware allocator correctness. Runtime SAT/pixel and timing proof are separate.')
    (project/'out/logs/splash_v3_manual_tile_differential_20261016.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)


if __name__=='__main__':
    main()
