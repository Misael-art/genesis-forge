#!/usr/bin/env python3
"""Exercise the actual quiet-beat export predicate, including wrap/reentry."""
from pathlib import Path
import hashlib
import json
import subprocess
from build_splash_v3_motion_lut import function


def main():
    project=Path(__file__).resolve().parents[1]
    source=(project/'src/system/runtime_probe.c').read_text()
    predicate=function(source.replace('static bool probe_snapshot_due(',
                                     'static void probe_snapshot_due('),'probe_snapshot_due')
    predicate=predicate.replace('static void probe_snapshot_due(','static bool probe_snapshot_due(')
    code=r'''
#include <stdint.h>
#include <stdio.h>
typedef uint16_t u16;typedef uint32_t u32;typedef uint8_t bool;
#define TRUE 1
#define FALSE 0
#define APP_SCENE_BRANDING 0
#define SPLASH_V3_QUIET_BEAT_EXPORT 1
static struct {u32 currentScene,totalFrames;u16 sceneFrames;} gApp;
static u32 s_lastExportFrame;static bool sBrandingFinalExported;
'''+predicate+r'''
int main(void){
    unsigned checks=0;
    const u32 origins[]={0,1234,0xFFFFFF00u};
    for(unsigned origin=0;origin<3;origin++)for(unsigned replay=0;replay<3;replay++){
        s_lastExportFrame=0;sBrandingFinalExported=FALSE;gApp.currentScene=0;
        for(unsigned frame=1;frame<=400;frame++){
            gApp.sceneFrames=(u16)frame;gApp.totalFrames=origins[origin]+frame;
            u16 samples=frame>90?(u16)(frame-90):0;
            bool due=probe_snapshot_due(samples);
            bool expected=frame==121||frame==181||frame==240||frame==300||frame==360;
            if(due!=expected){fprintf(stderr,"branding origin%u frame%u mismatch\n",origin,frame);return 1;}
            if(due){s_lastExportFrame=gApp.totalFrames;if(frame>=240)sBrandingFinalExported=TRUE;}
            checks++;
        }
    }
    for(unsigned scene=1;scene<5;scene++)for(unsigned elapsed=0;elapsed<500;elapsed++)for(unsigned samples=0;samples<2;samples++){
        gApp.currentScene=scene;gApp.totalFrames=1000+elapsed;gApp.sceneFrames=240;
        s_lastExportFrame=1000;sBrandingFinalExported=FALSE;
        if(probe_snapshot_due((u16)samples)!=(samples>0&&elapsed>=60))return 2;
        checks++;
    }
    printf("%u export schedule checks passed: initial121, periodic181, final240, reentry, wrap and other scenes\n",checks);return 0;
}
'''
    out=project/'rascunho/quiet_beat_export_20261016';out.mkdir(exist_ok=True)
    harness=out/'export_schedule.c';harness.write_text(code)
    subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(harness),'-o',str(out/'export_schedule')],check=True)
    result=subprocess.check_output([str(out/'export_schedule')],text=True).strip()
    report=dict(schema='splash_v3_export_schedule_self_check.v1',status='passed',checks=7600,
                predicate_sha256=hashlib.sha256(predicate.encode()).hexdigest(),source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                result=result,scope='Actual due predicate checked. Runtime sample accumulation, physical export cost, SRAM data and handoff still require ROM proof.')
    (project/'out/logs/splash_v3_export_schedule_self_check_20261016.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)


if __name__=='__main__':main()
