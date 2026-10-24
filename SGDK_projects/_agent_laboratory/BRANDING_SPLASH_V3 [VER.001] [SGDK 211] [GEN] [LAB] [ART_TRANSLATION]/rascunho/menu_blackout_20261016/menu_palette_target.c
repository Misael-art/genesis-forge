
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint16_t u16;
#define SPLASH_V3_MENU_HANDOFF 1
static struct {u16 before,colors[64],after;} guarded;
#define sMenuFadeTarget guarded.colors
int main(void);
static void menuSetPalette(u16 slot, const u16 *colors)
{
#if defined(SPLASH_V3_MENU_HANDOFF)
    u16 i;
    for (i = 0; i < 16; i++) sMenuFadeTarget[slot * 16 + i] = colors[i];
#else
    PAL_setPalette(slot, colors, DMA);
#endif
}
static void menuSetColor(u16 index, u16 color)
{
#if defined(SPLASH_V3_MENU_HANDOFF)
    sMenuFadeTarget[index] = color;
#else
    PAL_setColor(index, color);
#endif
}
int main(void){
    u16 expected[64],colors[16];unsigned cases=0;
    for(unsigned seed=0;seed<4096;seed++){
        guarded.before=guarded.after=0x3C3C;
        for(unsigned i=0;i<64;i++)sMenuFadeTarget[i]=expected[i]=0x5555;
        for(unsigned slot=0;slot<4;slot++){
            for(unsigned i=0;i<16;i++)colors[i]=(u16)(seed*16+i);
            menuSetPalette((u16)slot,colors);memcpy(expected+slot*16,colors,32);
            if(memcmp(sMenuFadeTarget,expected,sizeof(expected)))return 1;
            cases++;
        }
        for(unsigned index=0;index<64;index++){
            menuSetColor((u16)index,(u16)(seed+index));expected[index]=(u16)(seed+index);
            if(memcmp(sMenuFadeTarget,expected,sizeof(expected)))return 2;
            cases++;
        }
        menuSetColor(0,0);menuSetColor(15,0);menuSetColor(63,0xEE);menuSetColor(49,0xEE);
        if(sMenuFadeTarget[0] || sMenuFadeTarget[15] || sMenuFadeTarget[63]!=0xEE || sMenuFadeTarget[49]!=0xEE)return 3;
        if(guarded.before!=0x3C3C || guarded.after!=0x3C3C)return 4;
    }
    printf("%u target writer checks passed; all16-bit source words, four slots, all64 indices and guards\n",cases);return 0;
}
