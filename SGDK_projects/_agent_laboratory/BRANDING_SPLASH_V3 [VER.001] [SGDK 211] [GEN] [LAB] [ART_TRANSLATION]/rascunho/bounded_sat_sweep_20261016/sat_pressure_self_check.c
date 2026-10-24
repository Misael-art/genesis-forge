
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
#define SPLASH_V3_BOUNDED_SAT_SWEEP 1
static u16 measure_max_scanline_sprites(void)
{
    u16 index = 0;
    u16 remaining = SAT_MAX_SIZE;
    u16 line;
    u16 pressure = 0;
    u16 peakCount = 0;
    u16 peakWidthTiles = 0;
#if defined(SPLASH_V3_BOUNDED_SAT_SWEEP)
    u16 firstEndpoint = PROBE_SCANLINE_COUNT;
    u16 lastEndpoint = 0;
#endif

    s_peakWidth = 0;
    sScanlineInvalid = FALSE;
    /* SPR_update owns this cache. It is the submitted SAT, not a VRAM
     * readback; emitted-hardware claims still require the paired VDP dump. */
    do {
        const VDPSprite *sprite = &vdpSpriteCache[index];
        s16 start = (s16)(sprite->y & 0x01FF) - 128;
        s16 end = start + (s16)(((sprite->size & 3u) + 1u) << 3);

        if ((end > 0) && (start < PROBE_SCANLINE_COUNT)) {
            const u16 packed = 512u + (((sprite->size >> 2) & 3u) + 1u);
            if (start < 0) start = 0;
            if (end > PROBE_SCANLINE_COUNT) end = PROBE_SCANLINE_COUNT;
#if defined(SPLASH_V3_BOUNDED_SAT_SWEEP)
            /* Every nonzero endpoint lies in this inclusive interval. The
             * preceding valid/invalid pass clears all endpoints it touched. */
            if ((u16)start < firstEndpoint) firstEndpoint = (u16)start;
            if ((u16)end > lastEndpoint) lastEndpoint = (u16)end;
#endif
            sSatPressureDelta[start] = (u16)(sSatPressureDelta[start] + packed);
            sSatPressureDelta[end] = (u16)(sSatPressureDelta[end] - packed);
        }
        index = sprite->link & 0x7Fu;
        if (index == 0) break;
        if (index >= SAT_MAX_SIZE) goto invalid_sat;
    } while (--remaining != 0);
    if (index != 0) goto invalid_sat;

    for (line = firstEndpoint; line <= lastEndpoint; line++) {
        const u16 delta = sSatPressureDelta[line];
        if (delta != 0) {
            u16 count;
            u16 widthTiles;
            pressure = (u16)(pressure + delta);
            sSatPressureDelta[line] = 0;
            count = pressure >> 9;
            widthTiles = pressure & 511u;
            if (count > peakCount) peakCount = count;
            if (widthTiles > peakWidthTiles) peakWidthTiles = widthTiles;
        }
    }
    s_peakWidth = peakWidthTiles << 3;
    return peakCount;

invalid_sat:
    for (line = 0; line <= PROBE_SCANLINE_COUNT; line++) sSatPressureDelta[line] = 0;
    sScanlineInvalid = TRUE;
    /* Invalid-chain sentinel, never a physical count. Legacy cap checks
     * fail closed, while MDRT word 31 records the distinct invalid event. */
    s_peakWidth = 0xFFFF;
    return 0xFFFF;
}
static s8 old_s_lineCountDelta[225]; static s16 old_s_lineWidthDelta[225]; static u32 old_s_lineTouched[8]; static u16 old_s_peakWidth;
static void old_probe_mark_line(s16 line, s8 dc, s16 dw)
{
    old_s_lineCountDelta[line] += dc;
    old_s_lineWidthDelta[line] += dw;
    old_s_lineTouched[(u16)line >> 5] |= 1UL << (line & 31);
}
static u16 old_measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 peak = 0;
    s16 count = 0;
    s16 width = 0;
    u8 k;

    old_s_peakWidth = 0;

    while (cursor != NULL) {
        if (cursor->frame != NULL && cursor->visibility != HIDDEN) {
            u16 index;
            const u16 n = cursor->frame->numSprite & 0x7F;

            for (index = 0; index < n; index++) {
                const FrameVDPSprite* vdpSprite = &cursor->frame->frameVDPSprites[index];
                s16 start = (cursor->y - 0x80) + (s16)vdpSprite->offsetY;
                s16 end = start + (s16)(((vdpSprite->size & 0x3) + 1) << 3);
                const s16 w = (s16)((((vdpSprite->size >> 2) & 0x3) + 1) << 3);

                /* Sprite estacionado fora da tela pode dar end negativo; sem
                 * este guarda o indice sai do array e corrompe memoria. */
                if (end <= 0 || start >= (s16)PROBE_SCANLINE_COUNT) continue;
                if (start < 0) start = 0;
                if (end > (s16)PROBE_SCANLINE_COUNT) end = (s16)PROBE_SCANLINE_COUNT;

                old_probe_mark_line(start, 1, w);
                old_probe_mark_line(end, -1, (s16)-w);
            }
        }
        cursor = cursor->next;
    }

    /* varre so as linhas marcadas, em ordem crescente, zerando para o proximo quadro */
    for (k = 0; k < PROBE_TOUCHED_WORDS; k++) {
        u32 bits = old_s_lineTouched[k];
        old_s_lineTouched[k] = 0;
        while (bits) {
            u32 t = bits;
            u8 bi = 0;
            u16 line;
            if (!(t & 0xFFFF)) { t >>= 16; bi += 16; }
            if (!(t & 0xFF)) { t >>= 8; bi += 8; }
            if (!(t & 0xF)) { t >>= 4; bi += 4; }
            if (!(t & 0x3)) { t >>= 2; bi += 2; }
            if (!(t & 0x1)) bi += 1;
            bits &= bits - 1;
            line = (u16)k * 32 + bi;
            count += old_s_lineCountDelta[line];
            width += old_s_lineWidthDelta[line];
            old_s_lineCountDelta[line] = 0;
            old_s_lineWidthDelta[line] = 0;
            if ((u16)count > peak) peak = (u16)count;
            if ((u16)width > old_s_peakWidth) old_s_peakWidth = (u16)width;
        }
    }

    return peak;
}
static s8 fixed_s_lineCountDelta[225]; static s16 fixed_s_lineWidthDelta[225]; static u32 fixed_s_lineTouched[8]; static u16 fixed_s_peakWidth;
static void fixed_probe_mark_line(s16 line, s8 dc, s16 dw)
{
    fixed_s_lineCountDelta[line] += dc;
    fixed_s_lineWidthDelta[line] += dw;
    fixed_s_lineTouched[(u16)line >> 5] |= 1UL << (line & 31);
}
static u16 fixed_measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 peak = 0;
    s16 count = 0;
    s16 width = 0;
    u8 k;

    fixed_s_peakWidth = 0;
    sScanlineInvalid = FALSE;

    while (cursor != NULL) {
        /* Sprite.visibility is a bitmask (0 hidden), not SpriteVisibility. */
        if (cursor->frame != NULL && cursor->visibility != 0) {
            u16 index;
            const u16 n = cursor->frame->numSprite & 0x7F;

            for (index = 0; index < n; index++) {
                const FrameVDPSprite* vdpSprite = &cursor->frame->frameVDPSprites[index];
                s16 start = (cursor->y - 0x80) + (s16)vdpSprite->offsetY;
                s16 end = start + (s16)(((vdpSprite->size & 0x3) + 1) << 3);
                const s16 w = (s16)((((vdpSprite->size >> 2) & 0x3) + 1) << 3);

                /* Sprite estacionado fora da tela pode dar end negativo; sem
                 * este guarda o indice sai do array e corrompe memoria. */
                if (end <= 0 || start >= (s16)PROBE_SCANLINE_COUNT) continue;
                if (start < 0) start = 0;
                if (end > (s16)PROBE_SCANLINE_COUNT) end = (s16)PROBE_SCANLINE_COUNT;

                fixed_probe_mark_line(start, 1, w);
                fixed_probe_mark_line(end, -1, (s16)-w);
            }
        }
        cursor = cursor->next;
    }

    /* varre so as linhas marcadas, em ordem crescente, zerando para o proximo quadro */
    for (k = 0; k < PROBE_TOUCHED_WORDS; k++) {
        u32 bits = fixed_s_lineTouched[k];
        fixed_s_lineTouched[k] = 0;
        while (bits) {
            u32 t = bits;
            u8 bi = 0;
            u16 line;
            if (!(t & 0xFFFF)) { t >>= 16; bi += 16; }
            if (!(t & 0xFF)) { t >>= 8; bi += 8; }
            if (!(t & 0xF)) { t >>= 4; bi += 4; }
            if (!(t & 0x3)) { t >>= 2; bi += 2; }
            if (!(t & 0x1)) bi += 1;
            bits &= bits - 1;
            line = (u16)k * 32 + bi;
            count += fixed_s_lineCountDelta[line];
            width += fixed_s_lineWidthDelta[line];
            fixed_s_lineCountDelta[line] = 0;
            fixed_s_lineWidthDelta[line] = 0;
            if ((u16)count > peak) peak = (u16)count;
            if ((u16)width > fixed_s_peakWidth) fixed_s_peakWidth = (u16)width;
        }
    }

    return peak;
}

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
