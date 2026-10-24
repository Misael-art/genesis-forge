#include <genesis.h>

#include "core/app.h"
#include "scenes/scene_branding_v3_audio_preview.h"
#include "system/audio.h"
#include "system/input.h"

static bool sAudioPreviewComplete;
static u16 sMusicFramesObserved;
static u16 sMusicFramesPlaying;
static u16 sMusicDropouts;

static void audioPreviewLogCue(const char* label, SplashV3AudioCue cue, u16 row)
{
    char line[40];
    bool pcmStarted = AUDIO_playSplashV3Cue(cue);

    sprintf(line, "%s: %s", label, pcmStarted ? "PCM" : "PSG FALLBACK");
    VDP_drawTextFill(line, 4, row, 32);
}

void SCENE_brandingV3AudioPreviewEnter(void)
{
    AUDIO_stopAll();
    sAudioPreviewComplete = FALSE;
    sMusicFramesObserved = 0;
    sMusicFramesPlaying = 0;
    sMusicDropouts = 0;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setBackgroundColor(0);
    VDP_setTextPalette(PAL1);
    PAL_setColor(16, RGB24_TO_VDPCOLOR(0x101522));
    PAL_setColor(17, RGB24_TO_VDPCOLOR(0x87D8FF));
    PAL_setColor(18, RGB24_TO_VDPCOLOR(0xF2C36D));
    PAL_setColor(31, RGB24_TO_VDPCOLOR(0x87D8FF));

    VDP_drawText("SPLASH V3 AUDIO CANDIDATE", 4, 4);
    VDP_drawText("P1 024 ENERGY | 060 MUSIC | 240 STOP", 2, 9);
    VDP_drawText("P2 264 ENERGY | 300 MUSIC | 480 STOP", 2, 11);
    VDP_drawText("LOCK 118/358 | SWEEP 178/418", 4, 13);
    VDP_drawText("TAIL 210/450 | 2 PASSES OF 240F", 4, 15);
    VDP_drawText("MUSIC@61: WAITING", 4, 17);
    VDP_drawText("LISTEN TO THE EXACT ROM", 4, 19);
    VDP_drawText("A: RETURN AFTER TWO PASSES", 4, 21);
}

void SCENE_brandingV3AudioPreviewUpdate(void)
{
    char frameLine[24];
    char musicLine[32];
    const u16 frame = gApp.sceneFrames;

    if (sAudioPreviewComplete) {
        sprintf(frameLine, "DONE @480");
    } else {
        sprintf(frameLine, "FRAME:%03u", (unsigned)frame);
    }
    VDP_drawTextFill(frameLine, 4, 6, 14);

    if ((frame == 24) || (frame == 264)) {
        audioPreviewLogCue((frame == 24) ? "P1 ENERGY" : "P2 ENERGY",
                           SPLASH_V3_CUE_ENERGY_RISE, 23);
    }
    if ((frame == 60) || (frame == 300)) {
        AUDIO_startSplashV3();
        VDP_drawTextFill((frame == 60) ? "PASS1 XGM2 START" : "PASS2 XGM2 START", 4, 24, 24);
    }
    if ((frame == 118) || (frame == 358)) {
        audioPreviewLogCue((frame == 118) ? "P1 MARK LOCK" : "P2 MARK LOCK",
                           SPLASH_V3_CUE_MARK_LOCK, 25);
    }
    if ((frame == 178) || (frame == 418)) {
        audioPreviewLogCue((frame == 178) ? "P1 SWEEP" : "P2 SWEEP",
                           SPLASH_V3_CUE_SWEEP_PASS, 26);
    }
    if ((frame == 210) || (frame == 450)) {
        audioPreviewLogCue((frame == 210) ? "P1 TAIL" : "P2 TAIL",
                           SPLASH_V3_CUE_TAIL, 27);
    }

    if (((frame >= 61) && (frame < 240)) ||
        ((frame >= 301) && (frame < 480))) {
        const bool musicPlaying = XGM2_isPlaying();

        sMusicFramesObserved++;
        if (musicPlaying) {
            sMusicFramesPlaying++;
        } else {
            sMusicDropouts++;
        }

        if ((frame == 61) || (frame == 301)) {
            VDP_drawTextFill(musicPlaying ? "MUSIC: PLAYING" : "MUSIC: MISSING", 4, 17, 24);
        }
    }

    if (frame == 240) {
        AUDIO_stopAll();
        VDP_drawTextFill("PASS1 DONE", 4, 22, 20);
    }

    if (!sAudioPreviewComplete && frame >= 480) {
        AUDIO_stopAll();
        sAudioPreviewComplete = TRUE;
        sprintf(musicLine, "MUSIC %u/%u DROP:%u",
                (unsigned)sMusicFramesPlaying,
                (unsigned)sMusicFramesObserved,
                (unsigned)sMusicDropouts);
        VDP_drawTextFill(musicLine, 4, 18, 30);
        VDP_drawTextFill("TWO PASSES DONE", 4, 22, 20);
    }

    if (sAudioPreviewComplete && INPUT_pressed(BUTTON_A)) {
        APP_changeScene(APP_SCENE_BRANDING);
    }
}
