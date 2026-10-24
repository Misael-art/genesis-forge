#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "scenes/scene_branding.h"
#include "scenes/branding_v2.h"
#include "scenes/scene_boot.h"
#include "scenes/scene_demo.h"
#include "scenes/scene_menu.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"
#if defined(SPLASH_V3_VISUAL_PREVIEW) || defined(SPLASH_V3_MENU_HANDOFF)
#include "scenes/branding_v3.h"
#elif defined(SPLASH_V3_AUDIO_PREVIEW)
#include "scenes/scene_branding_v3_audio_preview.h"
#endif

static void APP_drawDebugHud(void)
{
    char line[40];
    const char* regionName = (gApp.region == APP_REGION_PAL) ? "PAL" : "NTSC";

    /* Canonical single-row HUD at row 26. Row 27 is reserved for scene hints. */
    sprintf(line, "SCN:%-8s FRM:%05lu %s", APP_sceneName(gApp.currentScene), gApp.totalFrames, regionName);
    VDP_drawTextFill(line, HUD_TEXT_X, HUD_ROW_HUD_GLOBAL, HUD_TEXT_LEN);
}

static void APP_drawTransitionHud(void)
{
    char line[40];

    if (gApp.transitionFrames == 0) {
        VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 1);
        return;
    }

    sprintf(line, ">> %s", APP_sceneName(gApp.transitionTarget));
    VDP_drawTextFill(line, 1, 0, 38);
}

void APP_boot(bool hardReset)
{
    (void) hardReset;

    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setBackgroundColor(0);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x121224));

    JOY_init();
    INPUT_init();
    AUDIO_init();
    SPR_initEx(16);   /* reserva 16 tiles para alocacao automatica de sprites; o pool de objetos e fixo no SGDK */

    gApp.currentScene = APP_SCENE_BRANDING;
    gApp.previousScene = APP_SCENE_BRANDING;
    gApp.transitionTarget = APP_SCENE_BRANDING;
    gApp.totalFrames = 0;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 0;
    gApp.transitionLocked = FALSE;
    gApp.region = SYS_isPAL() ? APP_REGION_PAL : APP_REGION_NTSC;
    gApp.targetFps = (gApp.region == APP_REGION_PAL) ? 50 : 60;
    gApp.sceneNeedsEnter = TRUE;
    gApp.showDebugHud = FALSE;
    gApp.paused = FALSE;

    MDRuntimeProbe_init();
}

void SCENE_cleanupLineScroll(VDPPlane plane)
{
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(plane, 0);
    VDP_setVerticalScroll(plane, 0);
}

static void APP_changeSceneInternal(AppScene nextScene, bool lockTransition)
{
    /* One scene-manager owner arbitrates every transition and its optional mutex. */
    if (gApp.transitionLocked) return;

    /*
     * Canonical SAT scrub on every scene transition: SPR_reset invalidates the
     * internal sprite list, SPR_update commits an empty list to VRAM SAT so no
     * stale hardware sprites from the previous scene bleed into the next one.
     */
    SPR_reset();
    SPR_update();

    if (gApp.currentScene == nextScene) {
        gApp.sceneFrames = 0;
        gApp.transitionFrames = 0;
        gApp.transitionLocked = FALSE;
        gApp.sceneNeedsEnter = TRUE;
        return;
    }

    gApp.previousScene = gApp.currentScene;
    gApp.currentScene = nextScene;
    gApp.transitionTarget = nextScene;
    gApp.sceneFrames = 0;
    gApp.transitionFrames = 12;
    gApp.transitionLocked = lockTransition;
    gApp.sceneNeedsEnter = TRUE;
    gApp.paused = FALSE;
}

void APP_changeScene(AppScene nextScene)
{
    APP_changeSceneInternal(nextScene, FALSE);
}

void APP_changeSceneLocked(AppScene nextScene)
{
    APP_changeSceneInternal(nextScene, TRUE);
}

const char* APP_sceneName(AppScene scene)
{
    switch (scene)
    {
        case APP_SCENE_BRANDING: return "BRAND";
        case APP_SCENE_BOOT: return "BOOT";
        case APP_SCENE_MENU: return "MENU";
        case APP_SCENE_DEMO: return "DEMO";
        default: return "UNKNOWN";
    }
}

void APP_update(void)
{
    const u8 transitionAtStart = gApp.transitionFrames;
    const bool transitionLocked = gApp.transitionLocked;
    const AppScene sceneAtStart = gApp.currentScene;
    bool brandingInputLocked = FALSE;

#if defined(SPLASH_V3_MENU_HANDOFF)
    brandingInputLocked = (gApp.currentScene == APP_SCENE_BRANDING);
#endif

    if (!transitionLocked && !brandingInputLocked && INPUT_pressed(BUTTON_C)) {
        gApp.showDebugHud = !gApp.showDebugHud;
        if (!gApp.showDebugHud) {
            /* Clear only the canonical HUD row; row 27 is owned by scene hints. */
            VDP_clearTextArea(0, HUD_ROW_HUD_GLOBAL, VDP_TEXT_COLS, HUD_ROWS);
        }
    }

    if (gApp.sceneNeedsEnter)
    {
        MDRuntimeProbe_onSceneEnter((u16)gApp.currentScene);
        switch (gApp.currentScene)
        {
            case APP_SCENE_BRANDING:
#if defined(SPLASH_V3_VISUAL_PREVIEW) || defined(SPLASH_V3_MENU_HANDOFF)
                SCENE_brandingV3Enter();
#elif defined(SPLASH_V3_AUDIO_PREVIEW)
                SCENE_brandingV3AudioPreviewEnter();
#else
                SCENE_brandingV2Enter();
#endif
                break;
            case APP_SCENE_BOOT: SCENE_bootEnter(); break;
            case APP_SCENE_MENU: SCENE_menuEnter(); break;
            case APP_SCENE_DEMO: SCENE_demoEnter(); break;
            default: SCENE_bootEnter(); break;
        }
        gApp.sceneNeedsEnter = FALSE;
    }

    /* A request may switch currentScene inside the previous scene's update.
     * Let the new scene enter on the next frame before it can process input. */
    if (!transitionLocked && (gApp.currentScene == sceneAtStart)) {
        switch (gApp.currentScene) {
            case APP_SCENE_BRANDING:
#if defined(SPLASH_V3_VISUAL_PREVIEW) || defined(SPLASH_V3_MENU_HANDOFF)
                SCENE_brandingV3Update();
#elif defined(SPLASH_V3_AUDIO_PREVIEW)
                SCENE_brandingV3AudioPreviewUpdate();
#else
                SCENE_brandingV2Update();
#endif
                break;
            case APP_SCENE_BOOT: SCENE_bootUpdate(); break;
            case APP_SCENE_MENU: SCENE_menuUpdate(); break;
            case APP_SCENE_DEMO: SCENE_demoUpdate(); break;
            default: SCENE_bootUpdate(); break;
        }
    }

    if (gApp.showDebugHud) {
        APP_drawDebugHud();
    }

    if (gApp.showDebugHud && (gApp.transitionFrames > 0)) {
        APP_drawTransitionHud();
    }

    if (transitionAtStart > 0) {
        gApp.transitionFrames = (u8)(transitionAtStart - 1);
        if ((gApp.transitionFrames == 0) && !gApp.transitionLocked) {
            VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 1);
        }
    }

    /* The fade/transfer state owns readiness. The HUD countdown must never
     * release input while the destination still owns unfinished work. */
    if (gApp.transitionLocked && !gApp.sceneNeedsEnter &&
        !PAL_isDoingFade() && (DMA_getQueueSize() == 0)) {
        gApp.transitionLocked = FALSE;
        gApp.transitionFrames = 0;
        VDP_clearTextArea(0, 0, VDP_TEXT_COLS, 1);
    }

    AUDIO_update();

    gApp.totalFrames++;
    if (!transitionLocked && (gApp.currentScene == sceneAtStart)) gApp.sceneFrames++;
}
