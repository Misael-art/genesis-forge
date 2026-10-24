
#include <stdint.h>
#include <stdio.h>
typedef uint16_t u16;typedef uint32_t u32;typedef uint8_t bool;
#define TRUE 1
#define FALSE 0
#define APP_SCENE_BRANDING 0
#define SPLASH_V3_QUIET_BEAT_EXPORT 1
static struct {u32 currentScene,totalFrames;u16 sceneFrames;} gApp;
static u32 s_lastExportFrame;static bool sBrandingFinalExported;
static bool probe_snapshot_due(u16 samplesRecorded)
{
    if (samplesRecorded == 0) return FALSE;
#if defined(SPLASH_V3_QUIET_BEAT_EXPORT)
    if (gApp.currentScene == APP_SCENE_BRANDING) {
        /* All samples still run after warmup. Move the first SRAM copy out
         * of convergence into fill (rendered F120, logical counter121).
         * Flush F239 before the following update hands the scene away. */
        if (gApp.sceneFrames < 121) return FALSE;
        if (gApp.sceneFrames >= 240 && !sBrandingFinalExported) return TRUE;
    }
#endif
    return (gApp.totalFrames - s_lastExportFrame) >= 60u;
}
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
