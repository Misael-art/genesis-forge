#include <stdint.h>
#include <stdio.h>
typedef int8_t s8; typedef uint8_t u8; typedef int16_t s16; typedef uint16_t u16; typedef int32_t s32; typedef uint32_t u32;

#define SPLASH_PARTICLE_COUNT       64

#define SPLASH_SWEEP_SPARK_COUNT     6

#define SPLASH_ENERGY_START         24

#define SPLASH_OUTLINE_START        84

#define SPLASH_SGDK_X               48

#define SPLASH_SGDK_Y               72

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

static const s16 sCos16[16] = {
    256, 237, 181, 98, 0, -98, -181, -237,
    -256, -237, -181, -98, 0, 98, 181, 237
};

static const s16 sSin16[16] = {
    0, 98, 181, 237, 256, 237, 181, 98,
    0, -98, -181, -237, -256, -237, -181, -98
};

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

static const u16 sConvergeWeightQ16[36] = {
    0, 149, 585, 1290, 2248, 3442,
    4855, 6470, 8271, 10240, 12362, 14617,
    16991, 19466, 22026, 24652, 27330, 30041,
    32768, 35496, 38207, 40885, 43511, 46071,
    48546, 50920, 53175, 55296, 57266, 59067,
    60682, 62095, 63289, 64247, 64952, 65388
};

static s16 sParticleStartX[64], sParticleStartY[64];

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
int main(void) {
    u16 i, f; s16 x, y;
    for (i=0; i<64; i++) v3RadialPosition(i,83,&sParticleStartX[i],&sParticleStartY[i]);
    for (f=24; f<120; f++) for (i=0; i<64; i++) {
        v3ParticlePosition(i,f,&x,&y); printf("%d %d\n",x,y);
    }
    for (i=0; i<6; i++) for (f=0; f<30; f++) {
        if (f<sSweepTrajectories[i].lifetimeFrames) v3SweepPositionAt(&sSweepTrajectories[i],f,&x,&y);
        else x=y=0;
        printf("%d %d\n",x,y);
    }
    return 0;
}
