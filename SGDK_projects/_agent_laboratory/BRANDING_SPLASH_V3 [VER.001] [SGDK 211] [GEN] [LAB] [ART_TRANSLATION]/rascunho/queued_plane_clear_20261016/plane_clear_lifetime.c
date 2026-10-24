
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint8_t bool;
#define DMA_VRAM 0
static const u16 sPlaneClearWords[256]={0};
static u16 sPlaneClearARows,sPlaneClearBRows;
static uint8_t vram[65536];
static struct {const u16* src;u16 to,len,step;} jobs[8];
static unsigned count,capacity,calls,failures,partials;static uint32_t rng;
static u16 VDP_getBGAAddress(void){return 0xC000;}
static u16 VDP_getBGBAddress(void){return 0xE000;}
static bool DMA_queueDma(u8 location,void* src,u16 to,u16 len,u16 step){
    if(location!=DMA_VRAM || src!=sPlaneClearWords || len!=256 || step!=2 ||
       !((to>=0xC000 && to<=0xCE00)||(to>=0xE000 && to<=0xEE00)) || (to&511))return 0;
    calls++;rng=rng*1664525u+1013904223u;
    if(count>=capacity || (rng&7)==0){failures++;return 0;}
    jobs[count].src=src;jobs[count].to=to;jobs[count].step=step;
    /* A split across a source bank may admit a prefix then reject. A
     * complete retry is safe because the submitted words remain zero. */
    if(calls%31==0){jobs[count++].len=128;partials++;return 0;}
    jobs[count++].len=len;return 1;
}
static void drain(unsigned n){
    while(n-- && count){
        for(unsigned word=0;word<jobs[0].len;word++){
            unsigned a=jobs[0].to+word*jobs[0].step;
            u16 value=jobs[0].src[word];vram[a]=(u8)(value>>8);vram[a+1]=(u8)value;
        }
        memmove(jobs,jobs+1,(--count)*sizeof(jobs[0]));
    }
}
static void v3QueuePlaneClears(void)
{
    if (sPlaneClearARows < 32 && DMA_queueDma(DMA_VRAM, (void *)sPlaneClearWords,
            VDP_getBGAAddress() + sPlaneClearARows * 128u, 256, 2)) {
        sPlaneClearARows += 4;
    }
    if (sPlaneClearBRows < 32 && DMA_queueDma(DMA_VRAM, (void *)sPlaneClearWords,
            VDP_getBGBAddress() + sPlaneClearBRows * 128u, 256, 2)) {
        sPlaneClearBRows += 4;
    }
}
int main(void){
    unsigned cases=0,allFailures=0,allPartials=0;
    for(unsigned cap=1;cap<=8;cap*=2)for(unsigned seed=1;seed<=64;seed++){
        for(unsigned replay=0;replay<2;replay++){
            memset(vram,0x6A,sizeof(vram));count=0;capacity=cap;calls=failures=partials=0;
            rng=seed;sPlaneClearARows=sPlaneClearBRows=0;
            /* Build backpressure before draining; rows represent accepted
             * work, so rejection cannot advance beyond accepted blocks. */
            for(unsigned tick=0;tick<12;tick++)v3QueuePlaneClears();
            for(unsigned tick=0;tick<512 && (sPlaneClearARows<32 || sPlaneClearBRows<32 || count);tick++){
                v3QueuePlaneClears();drain(1+(tick%3));
                if(sPlaneClearARows>32 || sPlaneClearBRows>32 || sPlaneClearARows%4 || sPlaneClearBRows%4)return 1;
            }
            if(sPlaneClearARows!=32 || sPlaneClearBRows!=32 || count)return 2;
            for(unsigned a=0;a<sizeof(vram);a++){
                u8 expected=((a>=0xC000 && a<0xD000)||(a>=0xE000 && a<0xF000))?0:0x6A;
                if(vram[a]!=expected){fprintf(stderr,"outcome mismatch cap%u seed%u addr%u\n",cap,seed,a);return 3;}
            }
            for(unsigned i=0;i<256;i++)if(sPlaneClearWords[i])return 4;
            allFailures+=failures;allPartials+=partials;
        }
        cases++;
    }
    capacity=0;count=0;sPlaneClearARows=sPlaneClearBRows=0;
    for(unsigned tick=0;tick<24;tick++)v3QueuePlaneClears();
    if(sPlaneClearARows || sPlaneClearBRows || count || !allFailures || !allPartials)return 5;
    printf("%u schedules x2 reentries passed; queue rejection, partial admission, drain, immutable source and exact plane bounds\n",cases);return 0;
}
