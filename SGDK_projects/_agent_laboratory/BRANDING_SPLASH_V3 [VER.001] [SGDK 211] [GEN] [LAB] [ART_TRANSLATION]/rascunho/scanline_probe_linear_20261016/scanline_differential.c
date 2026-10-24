
#include <stdint.h>
#include <stdio.h>
typedef uint8_t u8; typedef int8_t s8; typedef uint16_t u16;
typedef int16_t s16; typedef uint32_t u32;
#define PROBE_SCANLINE_COUNT 224
#define PROBE_TOUCHED_WORDS 8
#define HIDDEN 0
typedef struct { u8 size; s16 offsetY; } FrameVDPSprite;
typedef struct { u16 numSprite; FrameVDPSprite* frameVDPSprites; } Frame;
typedef struct Sprite { Frame* frame; u16 visibility; s16 y; struct Sprite* next; } Sprite;
static Sprite* firstSprite;
static s8 old_s_lineCountDelta[225]; static s16 old_s_lineWidthDelta[225]; static u16 old_s_peakWidth;
static u32 old_s_lineTouched[8];
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
static s8 new_s_lineCountDelta[225]; static s16 new_s_lineWidthDelta[225]; static u16 new_s_peakWidth;
static void new_probe_mark_line(s16 line, s8 dc, s16 dw)
{
    new_s_lineCountDelta[line] += dc;
    new_s_lineWidthDelta[line] += dw;
}
static u16 new_measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 peak = 0;
    s16 count = 0;
    s16 width = 0;
    u16 line;

    new_s_peakWidth = 0;

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

                new_probe_mark_line(start, 1, w);
                new_probe_mark_line(end, -1, (s16)-w);
            }
        }
        cursor = cursor->next;
    }

    /* Include the offscreen end sentinel at 224 so no delta survives reuse. */
    for (line = 0; line <= PROBE_SCANLINE_COUNT; line++) {
        count += new_s_lineCountDelta[line];
        width += new_s_lineWidthDelta[line];
        new_s_lineCountDelta[line] = 0;
        new_s_lineWidthDelta[line] = 0;
        if ((u16)count > peak) peak = (u16)count;
        if ((u16)width > new_s_peakWidth) new_s_peakWidth = (u16)width;
    }

    return peak;
}

int main(void) {
    Sprite sprites[80]; Frame frames[80]; FrameVDPSprite cells[80];
    u32 rng=0x513aac17; int test, i, line, rep;
    for (test=0; test<512; test++) {
        u16 expectedCount=0, expectedWidth=0;
        for (i=0; i<80; i++) {
            rng=rng*1664525u+1013904223u;
            cells[i].size=(u8)((rng>>16)&15);
            cells[i].offsetY=(s16)((int)((rng>>8)%17)-8);
            sprites[i].y=(s16)(128+(int)(rng%304)-40);
            sprites[i].visibility=(rng&7)!=0;
            sprites[i].frame=(rng&31)?&frames[i]:0;
            sprites[i].next=i==79?0:&sprites[i+1];
            frames[i].numSprite=1; frames[i].frameVDPSprites=&cells[i];
            if (test<3) {
                cells[i].size=15; cells[i].offsetY=0; sprites[i].visibility=1; sprites[i].frame=&frames[i];
                sprites[i].y=(s16)(128+(test==0?96:test==1?223:-32));
            }
        }
        firstSprite=sprites;
        for (line=0; line<224; line++) {
            u16 count=0,width=0;
            for (i=0; i<80; i++) if(sprites[i].frame && sprites[i].visibility) {
                int start=sprites[i].y-128+cells[i].offsetY;
                int height=((cells[i].size&3)+1)*8;
                if(line>=start && line<start+height) {count++; width+=(u16)(((cells[i].size>>2)+1)*8);}
            }
            if(count>expectedCount) expectedCount=count;
            if(width>expectedWidth) expectedWidth=width;
        }
        for(rep=0;rep<2;rep++) {
            u16 oldCount=old_measure_max_scanline_sprites();
            u16 newCount=new_measure_max_scanline_sprites();
            if(oldCount!=expectedCount || newCount!=expectedCount || old_s_peakWidth!=expectedWidth || new_s_peakWidth!=expectedWidth) {
                fprintf(stderr,"fixture %d repetition %d expected %u/%u old %u/%u new %u/%u\n",test,rep,expectedCount,expectedWidth,oldCount,old_s_peakWidth,newCount,new_s_peakWidth);return 1;
            }
        }
    }
    puts("512 cases x 2 repetitions passed: 224-line count/pixel oracle, both actual C scanners, boundary clipping, 80-link peak and reuse");
    return 0;
}
