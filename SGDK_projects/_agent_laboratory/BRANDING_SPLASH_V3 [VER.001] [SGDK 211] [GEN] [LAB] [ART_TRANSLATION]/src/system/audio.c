#include <genesis.h>

#include "resources.h"
#include "system/audio.h"

static u8 sCueFrames = 0;
static u8 sBgmWanted = 0;
static u8 sSplashFallbackKind = 0;
static u8 sSplashFallbackFrames = 0;
static u8 sSplashFallbackStep = 0;

#define AUDIO_BGM_FORGE_V2 1
#define AUDIO_BGM_SPLASH_V3 2

static void audioStopPsg(void)
{
    PSG_setEnvelope(0, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(1, PSG_ENVELOPE_MIN);
    PSG_setEnvelope(2, PSG_ENVELOPE_MIN);
}

static void audioPulsePsg(u8 channel, u16 tone, u8 envelope, u8 frames)
{
    PSG_setFrequency(channel, tone);
    PSG_setEnvelope(channel, envelope);
    sCueFrames = frames;
}

static void audioSplashFallbackSetTone(void)
{
    u16 tone;

    switch (sSplashFallbackKind)
    {
        case (u8)SPLASH_V3_CUE_ENERGY_RISE + 1:
            tone = (sSplashFallbackStep < 12) ?
                   (u16)(180 + ((u16)sSplashFallbackStep * 48)) : 516;
            break;
        case (u8)SPLASH_V3_CUE_MARK_LOCK + 1:
            tone = 988;
            break;
        case (u8)SPLASH_V3_CUE_SWEEP_PASS + 1:
            tone = (sSplashFallbackStep < 10) ?
                   (u16)(300 + ((u16)sSplashFallbackStep * 70)) : 930;
            break;
        case (u8)SPLASH_V3_CUE_TAIL + 1:
            tone = 147;
            break;
        default:
            tone = 0x200;
            break;
    }

    PSG_setFrequency(2, tone);
}

static void audioStartSplashFallback(SplashV3AudioCue cue)
{
    sSplashFallbackKind = (u8)cue + 1;
    sSplashFallbackStep = 0;
    sSplashFallbackFrames = (cue == SPLASH_V3_CUE_MARK_LOCK) ? 4 :
                            (cue == SPLASH_V3_CUE_TAIL) ? 6 : 8;
    PSG_setEnvelope(2, 9);
    audioSplashFallbackSetTone();
}

static void audioUpdateSplashFallback(void)
{
    if (sSplashFallbackFrames == 0) {
        return;
    }

    sSplashFallbackStep++;
    sSplashFallbackFrames--;
    if (sSplashFallbackFrames == 0) {
        PSG_setEnvelope(2, PSG_ENVELOPE_MIN);
        sSplashFallbackKind = 0;
        sSplashFallbackStep = 0;
    } else {
        audioSplashFallbackSetTone();
    }
}

void AUDIO_stopAll(void)
{
    sBgmWanted = 0;
    sCueFrames = 0;
    sSplashFallbackKind = 0;
    sSplashFallbackFrames = 0;
    sSplashFallbackStep = 0;
    audioStopPsg();
    XGM2_stopPCM(SOUND_PCM_CH1);
    XGM2_stopPCM(SOUND_PCM_CH2);
    XGM2_stopPCM(SOUND_PCM_CH3);
    XGM2_stop();
}

void AUDIO_startBrandBgm(void)
{
    sBgmWanted = AUDIO_BGM_FORGE_V2;
    XGM2_play(mus_forge_brand);
}

void AUDIO_startSplashV3(void)
{
    sBgmWanted = AUDIO_BGM_SPLASH_V3;
    XGM2_play(mus_splash_v3);
}

void AUDIO_init(void)
{
    PSG_reset();
    XGM2_loadDriver(TRUE);
    AUDIO_stopAll();
    sCueFrames = 0;
}

void AUDIO_playCue(AudioCue cue)
{
    switch (cue)
    {
        case AUDIO_CUE_MENU:
            AUDIO_stopAll();
            audioPulsePsg(0, 440, 5, 5);
            break;
        case AUDIO_CUE_JUMP:
            AUDIO_stopAll();
            audioPulsePsg(0, 720, 3, 6);
            break;
        case AUDIO_CUE_LAND:
            AUDIO_stopAll();
            PSG_setNoise(PSG_NOISE_TYPE_PERIODIC, PSG_NOISE_FREQ_CLOCK8);
            PSG_setEnvelope(2, 6);
            sCueFrames = 4;
            break;
        case AUDIO_CUE_STRIKE:
            AUDIO_stopAll();
            audioPulsePsg(1, 180, 2, 8);
            break;
        case AUDIO_CUE_PAUSE:
            AUDIO_stopAll();
            audioPulsePsg(0, 320, 4, 4);
            break;
        case AUDIO_CUE_BRAND_ENGINE_HIT:
            XGM2_playPCMEx(brand_bell_forge, sizeof(brand_bell_forge), SOUND_PCM_CH2, 12, FALSE, FALSE);
            audioPulsePsg(0, 260, 2, 14);
            break;
        case AUDIO_CUE_BRAND_AUTHOR_CLICK:
            XGM2_playPCMEx(brand_typewriter_click, sizeof(brand_typewriter_click), SOUND_PCM_CH3, 4, TRUE, FALSE);
            audioPulsePsg(1, 920, 7, 2);
            break;
        case AUDIO_CUE_BRAND_AUTHOR_BELL:
            XGM2_playPCMEx(brand_bell_terminal, sizeof(brand_bell_terminal), SOUND_PCM_CH2, 10, FALSE, FALSE);
            audioPulsePsg(0, 700, 5, 10);
            break;
        case AUDIO_CUE_BRAND_PROJECT_WHOOSH:
            XGM2_playPCMEx(brand_stamp_whoosh, sizeof(brand_stamp_whoosh), SOUND_PCM_CH2, 11, FALSE, FALSE);
            audioPulsePsg(0, 190, 2, 12);
            break;
        case AUDIO_CUE_BRAND_PROJECT_TAIL:
            XGM2_playPCMEx(brand_reverb_tail, sizeof(brand_reverb_tail), SOUND_PCM_CH3, 8, FALSE, FALSE);
            audioPulsePsg(2, 1160, 4, 8);
            break;
        case AUDIO_CUE_BRAND_HAMMER_SLAM:
            /* Nao para a trilha. PCM no CH2 (musica nao usa sample) + ruido
             * branco e um tom grave: o console "treme" com o flash visual. */
            XGM2_playPCMEx(brand_hammer_slam, sizeof(brand_hammer_slam),
                           SOUND_PCM_CH2, 15, FALSE, FALSE);
            PSG_setNoise(PSG_NOISE_TYPE_WHITE, PSG_NOISE_FREQ_CLOCK4);
            PSG_setEnvelope(2, 1);
            PSG_setFrequency(0, 72);
            PSG_setEnvelope(0, 1);
            sCueFrames = 18;
            break;
        default:
            sCueFrames = 0;
            break;
    }
}

bool AUDIO_playSplashV3Cue(SplashV3AudioCue cue)
{
    const u8* sample;
    u32 length;
    SoundPCMChannel channel;
    u8 priority;
    bool started;

    switch (cue)
    {
        case SPLASH_V3_CUE_ENERGY_RISE:
            sample = sfx_splash_v3_energy_rise;
            length = sizeof(sfx_splash_v3_energy_rise);
            channel = SOUND_PCM_CH2;
            priority = 9;
            break;
        case SPLASH_V3_CUE_MARK_LOCK:
            sample = sfx_splash_v3_mark_lock;
            length = sizeof(sfx_splash_v3_mark_lock);
            channel = SOUND_PCM_CH3;
            priority = 13;
            break;
        case SPLASH_V3_CUE_SWEEP_PASS:
            sample = sfx_splash_v3_sweep_pass;
            length = sizeof(sfx_splash_v3_sweep_pass);
            channel = SOUND_PCM_CH2;
            priority = 11;
            break;
        case SPLASH_V3_CUE_TAIL:
            sample = sfx_splash_v3_tail;
            length = sizeof(sfx_splash_v3_tail);
            channel = SOUND_PCM_CH3;
            priority = 8;
            break;
        default:
            return FALSE;
    }

    started = XGM2_playPCMEx(sample, length, channel, priority, FALSE, FALSE);
    if (!started) {
        audioStartSplashFallback(cue);
    }
    return started;
}

void AUDIO_update(void)
{
    if (sBgmWanted && !XGM2_isPlaying()) {
        if (sBgmWanted == AUDIO_BGM_SPLASH_V3) {
            XGM2_play(mus_splash_v3);
        } else {
            XGM2_play(mus_forge_brand);
        }
    }

    if (sCueFrames == 0) {
        audioUpdateSplashFallback();
        return;
    }

    sCueFrames--;
    if (sCueFrames == 0) {
        audioStopPsg();
    }

    audioUpdateSplashFallback();
}
