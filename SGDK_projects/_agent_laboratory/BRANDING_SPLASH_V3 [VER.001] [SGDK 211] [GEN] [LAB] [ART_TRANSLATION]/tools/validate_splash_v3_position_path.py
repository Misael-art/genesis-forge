#!/usr/bin/env python3
"""Compare the guarded manual position path to the workspace SGDK setter."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from build_splash_v3_motion_lut import function


def main():
    project=Path(__file__).resolve().parents[1]
    workspace=next(p for p in project.parents if (p/'sdk/sgdk-2.11').is_dir())
    sdk=workspace/'sdk/sgdk-2.11'
    library=(sdk/'src/sprite_eng.c').read_text()
    source=(project/'src/scenes/scene_branding_v3.c').read_text()
    actual=function(library.replace('void SPR_setPosition(', 'static void SPR_setPosition('),'SPR_setPosition')
    actual=actual.replace('SPR_setPosition','reference_setter')
    # The extractor expects plain static void; FORCE_INLINE remains in the
    # ROM source and is unnecessary to the semantic host comparison.
    helper=function(source.replace('static FORCE_INLINE void v3SetEnergyPosition(',
                                   'static void v3SetEnergyPosition('),'v3SetEnergyPosition')
    definitions=''
    for file,name in [('inc/sprite_eng.h','SPR_FLAG_AUTO_VISIBILITY'),
                      ('src/sprite_eng.c','NEED_VISIBILITY_UPDATE')]:
        text=(sdk/file).read_text()
        definitions+=re.search(r'^#define '+name+r'\s+[^\n]+',text,re.M)[0]+'\n'
    code=r'''
#include <stdint.h>
#include <stdio.h>
typedef uint16_t u16;typedef int16_t s16;
typedef struct {u16 status;s16 x,y;} Sprite;
#define START_PROFIL
#define END_PROFIL(x)
#define checkSpriteValid(a,b) ((void)0)
#define SPLASH_V3_MANUAL_POSITION_FASTPATH 1
static int apiCalls;
'''+definitions+actual+r'''
static void SPR_setPosition(Sprite *sprite,s16 x,s16 y){apiCalls++;reference_setter(sprite,x,y);}
'''+helper+r'''
int main(void){
    const s16 points[]={-32768,-32767,-129,-128,-32,-4,0,4,72,224,320,32766,32767};
    unsigned cases=0;
    for(int flags=0;flags<4;flags++)for(unsigned a=0;a<13;a++)for(unsigned b=0;b<13;b++)
    for(unsigned c=0;c<13;c++)for(unsigned d=0;d<13;d++){
        Sprite ref={(u16)(0xA00A|(flags&1?SPR_FLAG_AUTO_VISIBILITY:0)|(flags&2?NEED_VISIBILITY_UPDATE:0)),points[a],points[b]};
        Sprite fast=ref;apiCalls=0;
        reference_setter(&ref,points[c],points[d]);
        v3SetEnergyPosition(&fast,points[c],points[d]);
        if(ref.x!=fast.x || ref.y!=fast.y || ref.status!=fast.status || apiCalls!=(flags&1?1:0)){
            fprintf(stderr,"case %u mismatch\n",cases);return 1;
        }
        cases++;
    }
    printf("%u SGDK position cases passed, manual/auto visibility, dirty flags and signed endpoints\n",cases);
    return 0;
}
'''
    out=project/'rascunho/manual_position_path_20261016';out.mkdir(exist_ok=True)
    harness=out/'position_differential.c';harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror',
                    '-fsanitize=address,undefined',str(harness),'-o',str(out/'position_differential')],check=True)
    result=subprocess.check_output([str(out/'position_differential')],text=True).strip()
    report=dict(schema='splash_v3_position_differential.v1',status='passed',cases=4*13**4,
                sgdk_setter_sha256=hashlib.sha256(actual.encode()).hexdigest(),
                source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                harness_sha256=hashlib.sha256(code.encode()).hexdigest(),result=result,
                scope='Actual SGDK 2.11 setter compared on host; signed conversion follows GCC as in target. Auto visibility always calls original API. Runtime cadence/SAT proof separate.')
    (project/'out/logs/splash_v3_position_differential_20261016.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)


if __name__=='__main__':
    main()
