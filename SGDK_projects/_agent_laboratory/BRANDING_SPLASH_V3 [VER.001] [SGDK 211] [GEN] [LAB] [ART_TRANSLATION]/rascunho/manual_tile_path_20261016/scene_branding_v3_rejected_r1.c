#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "scenes/branding_v3.h"
#include "system/audio.h"
#include "system/input.h"
#include "system/runtime_probe.h"

#if defined(SPLASH_V3_MOTION_LUT)
#include "generated/splash_v3_motion_lut.h"
#endif

#if defined(SPLASH_V3_BACKDROP_V019)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v019
#elif defined(SPLASH_V3_BACKDROP_V018)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v018
#elif defined(SPLASH_V3_BACKDROP_V016)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v016
#elif defined(SPLASH_V3_BACKDROP_V015)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v015
#elif defined(SPLASH_V3_BACKDROP_V014)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v014
#elif defined(SPLASH_V3_BACKDROP_V012)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v012
#elif defined(SPLASH_V3_BACKDROP_V006)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v006
#elif defined(SPLASH_V3_BACKDROP_V005)
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3_v005
#else
#define SPLASH_BACKDROP_IMAGE img_splash_backdrop_v3
#endif

#define SPLASH_PARTICLE_COUNT       64
#define SPLASH_SWEEP_SPARK_COUNT     6
#define SPLASH_SWEEP_TRAIL_BASE      SPLASH_SWEEP_SPARK_COUNT
#define SPLASH_SWEEP_SPRITE_COUNT   (SPLASH_SWEEP_SPARK_COUNT * 2)
#define SPLASH_PARTICLE_FRAME_MAX    8
#define SPLASH_IMAGE_COUNT           3
#define SPLASH_DMA_CHUNK_TILES     180
#define SPLASH_ENERGY_START         24
#define SPLASH_OUTLINE_START        84
#define SPLASH_PARTICLE_LOCK       120
#define SPLASH_FORGE_REVEAL        150
#define SPLASH_SWEEP_START         180
#define SPLASH_FADE_START          210
#define SPLASH_END_FRAME           240
#define SPLASH_SGDK_X               48
#define SPLASH_SGDK_Y               72

static const s16 sCos16[16] = {
    256, 237, 181, 98, 0, -98, -181, -237,
    -256, -237, -181, -98, 0, 98, 181, 237
};

static const s16 sSin16[16] = {
    0, 98, 181, 237, 256, 237, 181, 98,
    0, -98, -181, -237, -256, -237, -181, -98
};

typedef struct {
    u16 startFrame;
    u8 lifetimeFrames;
    s16 x[4];
    s16 y[4];
    u8 noisePhase;
    u8 noisePeriodFrames;
    u8 noiseAmplitudePx;
    u8 flickerPeriodFrames;
    u8 flickerPhase;
    u8 trailLagPx;
} SweepTrajectory;

/* Per-instance speed, path, crosswind and flicker: see the v004 curation contract. */
static const SweepTrajectory sSweepTrajectories[SPLASH_SWEEP_SPARK_COUNT] = {
    {180, 24, { -8,  14, 235, 270}, { 78,  86,  70,  82},  0, 2, 1, 8, 0, 5},
    {181, 28, { 14,  38, 166, 235}, {104, 112,  96, 108},  4, 2, 1, 0, 0, 4},
    {180, 30, { 38,  72, 124, 207}, {130, 137, 119, 131},  8, 3, 2, 9, 3, 5},
    {184, 22, {  4,  48, 258, 306}, {156, 146, 168, 154}, 11, 2, 1, 0, 0, 4},
    {182, 27, { 55,  80, 132, 215}, {184, 191, 174, 181},  3, 3, 2, 7, 5, 5},
    {185, 23, { 22,  58, 195, 300}, {208, 201, 215, 205}, 14, 2, 1, 8, 2, 4}
};

static const s8 sSweepNoisePx[16] = {
    -1, -1, 0, 1, 1, 0, -1, -1,
     0,  1, 1, 0, 0, -1,  0,  1
};

#if defined(SPLASH_V3_PARTICLE_ANCHORS_R1)
/*
 * Diagnostic permutation r1, preserved for the user's F109 review.
 * Its geometry-only report measures 22 sprites / 176 pixels at raster line 99
 * in F109 and 21 sprites in F108. It is a WIP preview variant, not the default.
 * Source contract: out/logs/choreography_inputs_splash_v3_glyph_anchor_v001_20261014_r1/particle_glyph_anchor_contract.json.
 */
static const u8 sParticleTargetTileX[SPLASH_PARTICLE_COUNT] = {
    7, 10, 2, 5, 23, 12, 20, 13, 16, 8, 17, 4, 25, 1, 20, 22,
    15, 2, 11, 5, 7, 0, 2, 21, 10, 18, 11, 14, 6, 15, 2, 18,
    24, 18, 20, 12, 26, 8, 3, 5, 25, 26, 19, 6, 15, 9, 12, 4,
    10, 25, 15, 22, 15, 18, 10, 21, 6, 1, 3, 22, 24, 17, 4, 13
};
static const u8 sParticleTargetTileY[SPLASH_PARTICLE_COUNT] = {
    1, 4, 2, 5, 2, 0, 3, 1, 4, 2, 5, 3, 0, 4, 1, 4,
    2, 0, 3, 1, 4, 2, 5, 2, 0, 3, 1, 4, 2, 5, 3, 0,
    3, 1, 4, 2, 5, 3, 1, 4, 1, 4, 2, 0, 3, 1, 4, 2,
    5, 2, 0, 3, 1, 4, 2, 5, 3, 1, 4, 1, 4, 2, 0, 3
};
#else
/*
 * 64 WIP targets sampled from visible 8x8 cells of the SGDK plate.
 * Source hash and selection policy: out/logs/choreography_inputs_splash_v3_glyph_anchor_v001_20261014_r2/particle_glyph_anchor_contract.json.
 * Regenerate and remeasure if the wordmark source changes.
 */
static const u8 sParticleTargetTileX[SPLASH_PARTICLE_COUNT] = {
    19, 15, 8, 15, 24, 10, 2, 10, 9, 23, 18, 11, 6, 26, 0, 5,
    22, 15, 2, 10, 1, 20, 17, 18, 12, 2, 4, 6, 21, 12, 15, 26,
    2, 16, 5, 6, 4, 15, 25, 22, 3, 10, 1, 20, 18, 25, 24, 7,
    14, 22, 3, 18, 5, 13, 21, 7, 25, 20, 11, 4, 8, 13, 12, 17
};
static const u8 sParticleTargetTileY[SPLASH_PARTICLE_COUNT] = {
    2, 3, 2, 2, 3, 2, 2, 4, 1, 2, 4, 1, 2, 4, 2, 1,
    4, 0, 3, 5, 1, 1, 5, 1, 4, 5, 0, 3, 5, 0, 1, 5,
    0, 4, 5, 0, 3, 5, 0, 1, 4, 0, 4, 4, 0, 2, 4, 1,
    4, 3, 1, 3, 4, 1, 2, 4, 1, 3, 3, 2, 3, 3, 2, 2
};
#endif

static const u16 sBlackPalette[64] = { 0 };
static u16 sLogoOutlinePalette[16];
/* Cool, lower-luminance field palette for the final WIP hold; preserves facets. */
static const u16 sBackdropReviewPalette[16] = {
    RGB24_TO_VDPCOLOR(0x000000), RGB24_TO_VDPCOLOR(0x000020),
    RGB24_TO_VDPCOLOR(0x000040), RGB24_TO_VDPCOLOR(0x000040),
    RGB24_TO_VDPCOLOR(0x000060), RGB24_TO_VDPCOLOR(0x000080),
    RGB24_TO_VDPCOLOR(0x0020A0), RGB24_TO_VDPCOLOR(0x0040A0),
    RGB24_TO_VDPCOLOR(0x0060A0), RGB24_TO_VDPCOLOR(0x0080C0),
    RGB24_TO_VDPCOLOR(0x00A0C0), RGB24_TO_VDPCOLOR(0x20A0C0),
    RGB24_TO_VDPCOLOR(0x20A0C0), RGB24_TO_VDPCOLOR(0x40A0C0),
    RGB24_TO_VDPCOLOR(0x80A0C0), RGB24_TO_VDPCOLOR(0xA0C0C0)
};
static const u16 sReviewTextColor[1] = { RGB24_TO_VDPCOLOR(0xA6E6FC) };
/* Lift only the three shadow/contour colors after the field darkens at frame 210. */
static const u16 sLogoFinalEdgePalette[3] = {
    RGB24_TO_VDPCOLOR(0x000080),
    RGB24_TO_VDPCOLOR(0x0020B0),
    RGB24_TO_VDPCOLOR(0x0040E0)
};

static const TileSet *sImageTiles[SPLASH_IMAGE_COUNT];
static u16 sImageTileBase[SPLASH_IMAGE_COUNT];
static u16 sParticleFrameBase[SPLASH_PARTICLE_FRAME_MAX];
static u8 sParticleFrameCount;
static bool sParticleUniformGeometry;
static Sprite *sParticles[SPLASH_PARTICLE_COUNT];
static u8 sParticleFrameIndex[SPLASH_PARTICLE_COUNT];
/* ceil(smoothstep(step / 36) * 65536), indexed by step 0..35. */
static const u16 sConvergeWeightQ16[36] = {
    0, 149, 585, 1290, 2248, 3442,
    4855, 6470, 8271, 10240, 12362, 14617,
    16991, 19466, 22026, 24652, 27330, 30041,
    32768, 35496, 38207, 40885, 43511, 46071,
    48546, 50920, 53175, 55296, 57266, 59067,
    60682, 62095, 63289, 64247, 64952, 65388
};
static s16 sParticleStartX[SPLASH_PARTICLE_COUNT];
static s16 sParticleStartY[SPLASH_PARTICLE_COUNT];
static u16 sLoadImageIndex;
static u16 sLoadTileOffset;
static u8 sLoadParticleFrame;
static u8 sVisualAssetsLoaded;
static u8 sBackdropMapQueued;
static u8 sSgdkMapQueued;
static u8 sForgeMapQueued;
static u8 sEnergyStarted;
static u8 sReviewWait;
static u8 sLoadFailed;
static u8 sSpriteAllocationFailed;

static void v3PrepareLogoOutlinePalette(void)
{
    u16 i;

    for (i = 0; i < 16; i++) {
        /* Keep the blue contour; hold the pale fill colors at black for beat one. */
        sLogoOutlinePalette[i] = (i >= 10) ? 0 : img_splash_sgdk_v3.palette->data[i];
    }
}

static s16 v3DivTowardZero(s32 numerator, s32 denominator)
{
    return (s16)(numerator / denominator);
}

static u16 v3ParticleBirth(u16 index)
{
    return (u16)(SPLASH_ENERGY_START + (((u32)index * 60u) / SPLASH_PARTICLE_COUNT));
}

static void v3RadialPosition(u16 index, u16 frame, s16 *outX, s16 *outY)
{
    const u16 birth = v3ParticleBirth(index);
    const u16 age = (frame > birth) ? (u16)(frame - birth) : 0;
    const u16 sector = (u16)(((index * 5u) + ((index / 8u) * 3u)) & 15u);
    u16 radius;
    s16 dx;
    s16 dy;

    if (age <= 28) {
        radius = (u16)(8u + ((80u * age) / 28u));
    } else if (age <= 36) {
        radius = 88;
    } else if (age < 59) {
        radius = (u16)(88u - ((74u * (age - 36u)) / 23u));
    } else {
        radius = 14;
    }

    dx = v3DivTowardZero((s32)sCos16[sector] * radius, 256);
    dy = v3DivTowardZero((s32)sSin16[sector] * radius, 256);
    *outX = (s16)(160 + dx);
    *outY = (s16)(112 + dy);
}

static void v3ParticleTarget(u16 index, s16 *outX, s16 *outY)
{
    *outX = (s16)(SPLASH_SGDK_X + (sParticleTargetTileX[index] * 8u) + 4u);
    *outY = (s16)(SPLASH_SGDK_Y + (sParticleTargetTileY[index] * 8u) + 4u);
}

static s16 v3ScaleQ16TowardZero(s16 value, u16 weight)
{
    const s32 product = (s32)value * (s32)weight;

    if (product < 0) return (s16)(-((-product) >> 16));
    return (s16)(product >> 16);
}

static void v3ParticlePosition(u16 index, u16 frame, s16 *outX, s16 *outY)
{
    s16 targetX;
    s16 targetY;
    u16 step;

    if (frame < SPLASH_OUTLINE_START) {
        v3RadialPosition(index, frame, outX, outY);
        return;
    }

    v3ParticleTarget(index, &targetX, &targetY);
    step = (u16)(frame - (SPLASH_OUTLINE_START - 1));
    if (step >= 36) {
        *outX = targetX;
        *outY = targetY;
        return;
    }

    *outX = (s16)(sParticleStartX[index] +
                  v3ScaleQ16TowardZero((s16)(targetX - sParticleStartX[index]), sConvergeWeightQ16[step]));
    *outY = (s16)(sParticleStartY[index] +
                  v3ScaleQ16TowardZero((s16)(targetY - sParticleStartY[index]), sConvergeWeightQ16[step]));
}

static void v3SetPreloadedParticleTile(Sprite *sprite, u16 tileIndex)
{
#if defined(SPLASH_V3_MANUAL_TILE_FASTPATH)
    /* SGDK 2.11 sprite_eng.c: in the already-manual, no-upload branch,
     * the tile setter changes only this public attribute word. This scene
     * owns the allocation and preloads all eight single-cell frames. */
    if (sParticleUniformGeometry && (tileIndex <= TILE_INDEX_MASK) &&
        ((sprite->status & (SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD)) == 0)) {
        sprite->attribut = (sprite->attribut & TILE_ATTR_MASK) | tileIndex;
        return;
    }
#endif
    SPR_setVRAMTileIndex(sprite, (s16)tileIndex);
}

static void v3SetParticleFrame(u16 index, Sprite *sprite, u8 frame)
{
    if (sprite == NULL || sParticleFrameCount == 0) return;
    if (frame >= sParticleFrameCount) frame %= sParticleFrameCount;
    if (sParticleFrameIndex[index] == frame) return;
    v3SetPreloadedParticleTile(sprite, sParticleFrameBase[frame]);
#if defined(SPLASH_V3_STABLE_PARTICLE_GEOMETRY)
    if (!sParticleUniformGeometry ||
        (sprite->status & (SPR_FLAG_AUTO_VRAM_ALLOC | SPR_FLAG_AUTO_TILE_UPLOAD))) {
        SPR_setFrame(sprite, frame);
    }
#else
    SPR_setFrame(sprite, frame);
#endif
    sParticleFrameIndex[index] = frame;
}

static void v3HideParticles(void)
{
    u16 i;

    for (i = 0; i < SPLASH_PARTICLE_COUNT; i++) {
        if (sParticles[i] != NULL) SPR_setVisibility(sParticles[i], HIDDEN);
    }
}

static void v3UpdateEnergyParticles(u16 frame)
{
    u16 i;
    u8 animationFrame;

    if (sParticleFrameCount == 0) return;
    animationFrame = (u8)((frame / 4u) % sParticleFrameCount);

    for (i = 0; i < SPLASH_PARTICLE_COUNT; i++) {
        Sprite *sprite = sParticles[i];
        const u16 birth = v3ParticleBirth(i);
        const u8 particleFrame = animationFrame;
        s16 centerX;
        s16 centerY;

        animationFrame++;
        if (animationFrame >= sParticleFrameCount) animationFrame = 0;

        if (sprite == NULL) continue;
        if (frame < birth) {
            SPR_setVisibility(sprite, HIDDEN);
            continue;
        }

#if defined(SPLASH_V3_MOTION_LUT) && !defined(SPLASH_V3_PARTICLE_ANCHORS_R1)
        centerX = sEnergyMotionLut[frame - SPLASH_ENERGY_START][i][0];
        centerY = sEnergyMotionLut[frame - SPLASH_ENERGY_START][i][1];
#else
        v3ParticlePosition(i, frame, &centerX, &centerY);
#endif
        SPR_setPosition(sprite, (s16)(centerX - 4), (s16)(centerY - 4));
        v3SetParticleFrame(i, sprite, particleFrame);
        SPR_setVisibility(sprite, VISIBLE);
    }
}

static u16 v3SweepEaseQ8(u16 tQ8)
{
    const u32 t = tQ8;
    return (u16)((t * t * (768u - (2u * t))) >> 16);
}

static s16 v3LerpQ8(s16 from, s16 to, u16 tQ8)
{
    return (s16)(from + (((s32)(to - from) * tQ8) / 256));
}

static s16 v3BezierQ8(const s16 points[4], u16 tQ8)
{
    const s16 a = v3LerpQ8(points[0], points[1], tQ8);
    const s16 b = v3LerpQ8(points[1], points[2], tQ8);
    const s16 c = v3LerpQ8(points[2], points[3], tQ8);
    const s16 d = v3LerpQ8(a, b, tQ8);
    const s16 e = v3LerpQ8(b, c, tQ8);

    return v3LerpQ8(d, e, tQ8);
}

static void v3SweepPositionAt(const SweepTrajectory *trajectory, u16 elapsed,
                              s16 *outX, s16 *outY)
{
    const u16 remaining = (u16)(trajectory->lifetimeFrames - elapsed);
    const u16 duration = (u16)(trajectory->lifetimeFrames - 1u);
    const u16 linearTQ8 = (u16)(((u32)elapsed * 256u) / duration);
    const u16 easedTQ8 = v3SweepEaseQ8(linearTQ8);
    s16 x = v3BezierQ8(trajectory->x, easedTQ8);
    s16 y = v3BezierQ8(trajectory->y, easedTQ8);

    if ((elapsed >= 2u) && (remaining > 2u)) {
        const u16 noiseStep = (u16)(elapsed / trajectory->noisePeriodFrames);
        const u16 noiseIndex = (u16)((noiseStep + trajectory->noisePhase) & 15u);

        x = (s16)(x + (sSweepNoisePx[(noiseIndex + 6u) & 15u] *
                       trajectory->noiseAmplitudePx));
        y = (s16)(y + (sSweepNoisePx[noiseIndex] *
                       trajectory->noiseAmplitudePx));
    }

    *outX = x;
    *outY = y;
}

static bool v3SweepCoreFrame(const SweepTrajectory *trajectory, u16 elapsed, u8 *outFrame)
{
    const u16 remaining = (u16)(trajectory->lifetimeFrames - elapsed);
    static const u8 birthFrames[4] = { 0, 5, 6, 4 };

    if (elapsed < 4u) {
        *outFrame = birthFrames[elapsed];
        return TRUE;
    }
    if (remaining == 4u) {
        *outFrame = 6;
        return TRUE;
    }
    if (remaining == 3u) {
        *outFrame = 5;
        return TRUE;
    }
    if (remaining == 2u) {
        *outFrame = 0;
        return TRUE;
    }
    if (remaining <= 1u) return FALSE;

    if ((trajectory->flickerPeriodFrames != 0u) &&
        (((elapsed + trajectory->flickerPhase) % trajectory->flickerPeriodFrames) == 0u)) {
        /* Frame 1 is the authored lower-luma flare: about 84% of the steady core. */
        *outFrame = 1;
        return TRUE;
    }

    *outFrame = 4;
    return TRUE;
}

static void v3SweepPosition(u16 index, u16 elapsed, s16 *outX, s16 *outY)
{
#if defined(SPLASH_V3_MOTION_LUT)
    *outX = sSweepMotionLut[index][elapsed][0];
    *outY = sSweepMotionLut[index][elapsed][1];
#else
    v3SweepPositionAt(&sSweepTrajectories[index], elapsed, outX, outY);
#endif
}

static bool v3SweepTrailFrame(const SweepTrajectory *trajectory, u16 elapsed,
                              s16 deltaY, u8 *outFrame)
{
    const u16 remaining = (u16)(trajectory->lifetimeFrames - elapsed);

    if ((elapsed < 3u) || (remaining <= 2u)) return FALSE;
    if (remaining == 4u) {
        *outFrame = 5;
        return TRUE;
    }
    if (remaining == 3u) {
        *outFrame = 0;
        return TRUE;
    }

    if (deltaY < -1) *outFrame = 3;
    else if (deltaY > 1) *outFrame = 4;
    else *outFrame = 2;
    return TRUE;
}

static void v3UpdateSweep(u16 frame)
{
    u16 sparkIndex;

    if (sParticleFrameCount == 0) return;

    for (sparkIndex = SPLASH_SWEEP_SPRITE_COUNT; sparkIndex < SPLASH_PARTICLE_COUNT; sparkIndex++) {
        if (sParticles[sparkIndex] != NULL) {
            SPR_setVisibility(sParticles[sparkIndex], HIDDEN);
        }
    }

    for (sparkIndex = 0; sparkIndex < SPLASH_SWEEP_SPARK_COUNT; sparkIndex++) {
        const u16 trailIndex = (u16)(SPLASH_SWEEP_TRAIL_BASE + sparkIndex);
        Sprite *core = sParticles[sparkIndex];
        Sprite *trail = sParticles[trailIndex];
        const SweepTrajectory *trajectory = &sSweepTrajectories[sparkIndex];
        u16 elapsed;
        u8 coreFrame;
        u8 trailFrame;
        s16 x;
        s16 y;
        s16 priorX;
        s16 priorY;
        s16 deltaX;
        s16 deltaY;

        if (frame < trajectory->startFrame) {
            if (core != NULL) SPR_setVisibility(core, HIDDEN);
            if (trail != NULL) SPR_setVisibility(trail, HIDDEN);
            continue;
        }

        elapsed = (u16)(frame - trajectory->startFrame);
        if (elapsed >= trajectory->lifetimeFrames) {
            if (core != NULL) SPR_setVisibility(core, HIDDEN);
            if (trail != NULL) SPR_setVisibility(trail, HIDDEN);
            continue;
        }

        v3SweepPosition(sparkIndex, elapsed, &x, &y);
        if ((core != NULL) && v3SweepCoreFrame(trajectory, elapsed, &coreFrame)) {
            SPR_setPosition(core, x, y);
            v3SetParticleFrame(sparkIndex, core, coreFrame);
            SPR_setVisibility(core, VISIBLE);
        } else if (core != NULL) {
            SPR_setVisibility(core, HIDDEN);
        }

        v3SweepPosition(sparkIndex, (elapsed > 2u) ? (u16)(elapsed - 2u) : 0u,
                          &priorX, &priorY);
        deltaX = (s16)(x - priorX);
        deltaY = (s16)(y - priorY);
        if (deltaX < 1) deltaX = 1;

        if ((trail != NULL) && v3SweepTrailFrame(trajectory, elapsed, deltaY, &trailFrame)) {
            s16 trailY = (s16)(y - v3DivTowardZero((s32)deltaY * trajectory->trailLagPx, deltaX));
            if (trailY < (s16)(y - 2)) trailY = (s16)(y - 2);
            else if (trailY > (s16)(y + 2)) trailY = (s16)(y + 2);

            SPR_setPosition(trail, (s16)(x - trajectory->trailLagPx), trailY);
            v3SetParticleFrame(trailIndex, trail, trailFrame);
            SPR_setVisibility(trail, VISIBLE);
        } else if (trail != NULL) {
            SPR_setVisibility(trail, HIDDEN);
        }
    }
}

static void v3SetImagePalette(u16 paletteIndex, const Image *image)
{
    if (image->palette != NULL) {
        PAL_setPalette(paletteIndex, image->palette->data, DMA_QUEUE_COPY);
    }
}

static void v3QueueBackdropMap(void)
{
    if (sBackdropMapQueued || sLoadFailed) return;

    sBackdropMapQueued = VDP_setTileMapEx(
        BG_B,
        SPLASH_BACKDROP_IMAGE.tilemap,
        TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, sImageTileBase[0]),
        0, 0, 0, 0, 40, 28, DMA_QUEUE_COPY
    );
    if (!sBackdropMapQueued) sLoadFailed = TRUE;
}

static void v3QueueLogoMap(const Image *image, u16 palette, u16 base,
                           u16 x, u16 y, u16 width, u16 height, u8 *queued)
{
    if (*queued || sLoadFailed) return;

    *queued = VDP_setTileMapEx(
        BG_A,
        image->tilemap,
        TILE_ATTR_FULL(palette, TRUE, FALSE, FALSE, base),
        x, y, 0, 0, width, height, DMA_QUEUE_COPY
    );
    if (!*queued) sLoadFailed = TRUE;
}

static void v3PrepareAssets(void)
{
    const Animation *animation;
    u32 cursor = TILE_USER_INDEX;
    u16 i;

    sImageTiles[0] = SPLASH_BACKDROP_IMAGE.tileset;
    sImageTiles[1] = img_splash_sgdk_v3.tileset;
    sImageTiles[2] = img_splash_forge_v3.tileset;

    for (i = 0; i < SPLASH_IMAGE_COUNT; i++) {
        const TileSet *tileset = sImageTiles[i];

        if (tileset == NULL || tileset->compression != COMPRESSION_NONE || tileset->tiles == NULL) {
            sLoadFailed = TRUE;
            return;
        }
        sImageTileBase[i] = (u16)cursor;
        cursor += tileset->numTile;
    }

    animation = spr_splash_particle_v3.animations[0];
    if (animation == NULL || animation->numFrame == 0 ||
        animation->numFrame > SPLASH_PARTICLE_FRAME_MAX) {
        sLoadFailed = TRUE;
        return;
    }

    sParticleFrameCount = (u8)animation->numFrame;
    sParticleUniformGeometry = TRUE;
    for (i = 0; i < sParticleFrameCount; i++) {
        const AnimationFrame *frame = animation->frames[i];
        const TileSet *tileset = animation->frames[i]->tileset;
        const FrameVDPSprite *cell = &frame->frameVDPSprites[0];

        if (tileset == NULL || tileset->compression != COMPRESSION_NONE || tileset->tiles == NULL) {
            sLoadFailed = TRUE;
            return;
        }
        sParticleFrameBase[i] = (u16)cursor;
        cursor += tileset->numTile;

        /* The cutscene owns visual frame timing. Only a stationary 8x8
         * descriptor with no automatic animation can share its geometry.
         * Any richer authored frame retains the ordinary SGDK frame path. */
        if ((frame->numSprite != animation->frames[0]->numSprite) ||
            ((frame->numSprite & 0x7F) != 1) || (frame->timer != 0) ||
            (tileset->numTile != 1) || (cell->size != 0) ||
            (cell->offsetX != 0) || (cell->offsetY != 0) ||
            (cell->offsetXFlip != 0) || (cell->offsetYFlip != 0) ||
            (cell->numTile != 1)) {
            sParticleUniformGeometry = FALSE;
        }
    }

    if (cursor > ((u32)TILE_USER_MAX_INDEX + 1u)) {
        sLoadFailed = TRUE;
        return;
    }

    for (i = 0; i < SPLASH_IMAGE_COUNT; i++) {
        MDRuntimeProbe_noteVramLoadRange(sImageTileBase[i], sImageTiles[i]->numTile);
    }
    MDRuntimeProbe_noteVramLoadRange(
        sParticleFrameBase[0], (u16)(cursor - sParticleFrameBase[0]));

    sLoadImageIndex = 0;
    sLoadTileOffset = 0;
    sLoadParticleFrame = 0;
}

static void v3LoadOneChunk(void)
{
    const TileSet *tileset;
    u16 remaining;
    u16 count;

    if (sLoadFailed || sVisualAssetsLoaded) return;

    while (sLoadImageIndex < SPLASH_IMAGE_COUNT &&
           sLoadTileOffset >= sImageTiles[sLoadImageIndex]->numTile) {
        sLoadImageIndex++;
        sLoadTileOffset = 0;
    }

    if (sLoadImageIndex < SPLASH_IMAGE_COUNT) {
        tileset = sImageTiles[sLoadImageIndex];
        remaining = (u16)(tileset->numTile - sLoadTileOffset);
        count = (remaining > SPLASH_DMA_CHUNK_TILES) ? SPLASH_DMA_CHUNK_TILES : remaining;

        if (count != 0) {
            VDP_loadTileData(tileset->tiles + ((u32)sLoadTileOffset * 8u),
                             (u16)(sImageTileBase[sLoadImageIndex] + sLoadTileOffset),
                             count, DMA_QUEUE);
            sLoadTileOffset = (u16)(sLoadTileOffset + count);
        }
        return;
    }

    if (sLoadParticleFrame < sParticleFrameCount) {
        const Animation *animation = spr_splash_particle_v3.animations[0];
        const TileSet *frameTiles = animation->frames[sLoadParticleFrame]->tileset;

        VDP_loadTileSet(frameTiles, sParticleFrameBase[sLoadParticleFrame], DMA_QUEUE);
        sLoadParticleFrame++;
        return;
    }

    sVisualAssetsLoaded = TRUE;
}

static void v3CreateParticles(void)
{
    u16 i;
    u16 spawned = 0;
    u16 failed = 0;

    for (i = 0; i < SPLASH_PARTICLE_COUNT; i++) {
        sParticleFrameIndex[i] = 0xFF;
        v3RadialPosition(i, SPLASH_OUTLINE_START - 1,
                         &sParticleStartX[i], &sParticleStartY[i]);
        Sprite *sprite = SPR_addSpriteEx(
            &spr_splash_particle_v3,
            -32, -32,
            TILE_ATTR(PAL3, TRUE, FALSE, FALSE),
            SPR_FLAG_AUTO_VISIBILITY
        );

        sParticles[i] = sprite;
        if (sprite == NULL) {
            sSpriteAllocationFailed = TRUE;
            failed++;
            continue;
        }

        spawned++;
        SPR_setAutoTileUpload(sprite, FALSE);
        SPR_setVRAMTileIndex(sprite, (s16)sParticleFrameBase[0]);
        SPR_setFrame(sprite, 0);
        SPR_setVisibility(sprite, HIDDEN);
        if (i < SPLASH_SWEEP_SPARK_COUNT) {
            SPR_setDepth(sprite, (s16)(100u + i));
        } else if (i < SPLASH_SWEEP_SPRITE_COUNT) {
            SPR_setDepth(sprite, (s16)(200u + i - SPLASH_SWEEP_TRAIL_BASE));
        }
    }

    MDRuntimeProbe_noteSpriteAlloc(spawned, failed);
}

void SCENE_brandingV3Enter(void)
{
    u16 i;

    gApp.showDebugHud = FALSE;
    AUDIO_stopAll();
    gApp.sceneFrames = 0;
    VDP_setScreenWidth320();
    VDP_setScreenHeight224();
    VDP_setPlaneSize(64, 32, TRUE);
    VDP_setTextPlane(BG_A);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHilightShadow(FALSE);
    VDP_setWindowOff();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setBackgroundColor(0);
    PAL_setColors(0, sBlackPalette, 64, DMA_QUEUE_COPY);

    for (i = 0; i < SPLASH_PARTICLE_COUNT; i++) sParticles[i] = NULL;
    sParticleFrameCount = 0;
    sParticleUniformGeometry = FALSE;
    sVisualAssetsLoaded = FALSE;
    sBackdropMapQueued = FALSE;
    sSgdkMapQueued = FALSE;
    sForgeMapQueued = FALSE;
    sEnergyStarted = FALSE;
    sReviewWait = FALSE;
    sLoadFailed = FALSE;
    sSpriteAllocationFailed = FALSE;
    sLoadImageIndex = 0;
    sLoadTileOffset = 0;
    sLoadParticleFrame = 0;

    MDRuntimeProbe_beginDmaPreload();
    v3PrepareAssets();
    if (!sLoadFailed) v3CreateParticles();
}

void SCENE_brandingV3Exit(void)
{
    AUDIO_stopAll();
    VDP_setHilightShadow(FALSE);
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
    VDP_setWindowOff();
    VDP_setTextPlane(BG_A);
}

void SCENE_brandingV3Update(void)
{
    const u16 frame = gApp.sceneFrames;

#if defined(SPLASH_V3_H40_F109_HOLD)
    /* Diagnostic-only: leave the rendered F109 state intact for inspection. */
    if (frame > 109) return;
#endif

    if (!sVisualAssetsLoaded && !sLoadFailed) v3LoadOneChunk();
    if (sVisualAssetsLoaded && !sBackdropMapQueued) {
        v3QueueBackdropMap();
        if (sBackdropMapQueued && !sLoadFailed) {
            MDRuntimeProbe_finishDmaPreloadAfterCurrentFrame();
        }
    }

    if ((frame == SPLASH_ENERGY_START) && sBackdropMapQueued && !sEnergyStarted) {
        v3SetImagePalette(PAL0, &SPLASH_BACKDROP_IMAGE);
        PAL_setPalette(PAL3, spr_splash_particle_v3.palette->data, DMA_QUEUE_COPY);
        AUDIO_playSplashV3Cue(SPLASH_V3_CUE_ENERGY_RISE);
        sEnergyStarted = TRUE;
    }

    if (frame == 60) AUDIO_startSplashV3();

    if ((frame == SPLASH_OUTLINE_START) && sEnergyStarted) {
        v3QueueLogoMap(&img_splash_sgdk_v3, PAL1, sImageTileBase[1], 6, 9, 28, 6, &sSgdkMapQueued);
        v3PrepareLogoOutlinePalette();
        PAL_fadeIn(16, 31, sLogoOutlinePalette, 36, TRUE);
    }

    if (frame == 118) AUDIO_playSplashV3Cue(SPLASH_V3_CUE_MARK_LOCK);

    if (frame == SPLASH_PARTICLE_LOCK) {
        /* The blue outline is already settled; reveal the pale fill as a second beat. */
        PAL_fadeIn(26, 31, &img_splash_sgdk_v3.palette->data[10], 18, TRUE);
        v3HideParticles();
    }

    if (frame == SPLASH_FORGE_REVEAL) {
        v3QueueLogoMap(&img_splash_forge_v3, PAL2, sImageTileBase[2], 8, 16, 24, 4, &sForgeMapQueued);
        PAL_fadeIn(32, 47, img_splash_forge_v3.palette->data, 12, TRUE);
    }

    if (frame == 178) AUDIO_playSplashV3Cue(SPLASH_V3_CUE_SWEEP_PASS);
    if ((frame >= SPLASH_SWEEP_START) && (frame < SPLASH_FADE_START)) v3UpdateSweep(frame);

    if (frame == SPLASH_FADE_START) {
        AUDIO_playSplashV3Cue(SPLASH_V3_CUE_TAIL);
        v3HideParticles();
        PAL_setColors((PAL1 * 16) + 1, sLogoFinalEdgePalette, 3, DMA_QUEUE_COPY);
#if defined(SPLASH_V3_VISUAL_PREVIEW)
        /* Settle the crystal field without erasing the final branded composition. */
#if defined(SPLASH_V3_BACKDROP_V019)
        PAL_fade(0, 15, img_splash_backdrop_v3_v019.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#elif defined(SPLASH_V3_BACKDROP_V018)
        PAL_fade(0, 15, img_splash_backdrop_v3_v018.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#elif defined(SPLASH_V3_BACKDROP_V016)
        PAL_fade(0, 15, img_splash_backdrop_v3_v016.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#elif defined(SPLASH_V3_BACKDROP_V015)
        PAL_fade(0, 15, img_splash_backdrop_v3_v015.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#elif defined(SPLASH_V3_BACKDROP_V014)
        PAL_fade(0, 15, img_splash_backdrop_v3_v014.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#elif defined(SPLASH_V3_BACKDROP_V012)
        PAL_fade(0, 15, img_splash_backdrop_v3_v012.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#elif defined(SPLASH_V3_BACKDROP_V006)
        PAL_fade(0, 15, img_splash_backdrop_v3_v006.palette->data,
                 sBackdropReviewPalette, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#else
        PAL_fadeOut(0, 15, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#endif
#else
        PAL_fadeOut(0, 63, SPLASH_END_FRAME - SPLASH_FADE_START, TRUE);
#endif
    }

    if ((frame >= SPLASH_ENERGY_START) && (frame < SPLASH_PARTICLE_LOCK) && sEnergyStarted) {
        v3UpdateEnergyParticles(frame);
    }

    if (frame >= SPLASH_END_FRAME) {
#if defined(SPLASH_V3_MENU_HANDOFF)
        /* Finish the palette fade and queued VDP transfers before menu takes ownership. */
        if (PAL_isDoingFade() || (DMA_getQueueSize() != 0)) return;
        SCENE_brandingV3Exit();
        APP_changeSceneLocked(APP_SCENE_MENU);
        return;
#else
        if (!sReviewWait) {
            AUDIO_stopAll();
            v3HideParticles();
            if (!VDP_loadFont(&font_default, DMA_QUEUE_COPY)) sLoadFailed = TRUE;
            PAL_setColors((PAL3 * 16) + 15, sReviewTextColor, 1, DMA_QUEUE_COPY);
            VDP_setTextPlane(BG_A);
            VDP_setTextPalette(PAL3);
            VDP_setTextPriority(TRUE);
            VDP_drawText("A: REVER", 16, 21);
            if (sLoadFailed || sSpriteAllocationFailed) {
                VDP_drawText("DEVELOPMENT PREVIEW WARNING", 5, 1);
            }
            sReviewWait = TRUE;
        }

        if (INPUT_pressed(BUTTON_A)) {
            SCENE_brandingV3Exit();
            APP_changeScene(APP_SCENE_BRANDING);
            return;
        }
#endif
    }

}
