#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint16_t u16;
#define TILE_SIZE               32
#define TILE_INDEX_MASK         (0xFFFF / TILE_SIZE)
#define TILE_ATTR_PRIORITY_SFT      15
#define TILE_ATTR_PALETTE_SFT       13
#define TILE_ATTR_VFLIP_SFT         12
#define TILE_ATTR_HFLIP_SFT         11
#define TILE_ATTR_PRIORITY_MASK     (1 << TILE_ATTR_PRIORITY_SFT)
#define TILE_ATTR_PALETTE_MASK      (3 << TILE_ATTR_PALETTE_SFT)
#define TILE_ATTR_VFLIP_MASK        (1 << TILE_ATTR_VFLIP_SFT)
#define TILE_ATTR_HFLIP_MASK        (1 << TILE_ATTR_HFLIP_SFT)
static void prepareTileMapDataRowEx(u16* dest, u16 width, const u16* data, u16 basetile)
{
    // we can increment both index and palette
    const u16 baseinc = basetile & (TILE_INDEX_MASK | TILE_ATTR_PALETTE_MASK);
    // we can only do logical OR on priority and HV flip
    const u16 baseor = basetile & (TILE_ATTR_PRIORITY_MASK | TILE_ATTR_VFLIP_MASK | TILE_ATTR_HFLIP_MASK);

    const u16* s = data;
    u16* d = dest;
    u16 i;

    i = width >> 2;
    // prepare map data for row update
    while (i--)
    {
        *d++ = baseor | (*s++ + baseinc);
        *d++ = baseor | (*s++ + baseinc);
        *d++ = baseor | (*s++ + baseinc);
        *d++ = baseor | (*s++ + baseinc);
    }

    i = width & 3;
    // prepare map data for row update
    while (i--) *d++ = baseor | (*s++ + baseinc);
}
static void v3PrepareLogoRowData(u16 *dest, const u16 *source, u16 width, u16 basetile)
{
    /* Exact SGDK 2.11 prepareTileMapDataRowEx attribute arithmetic. */
    const u16 baseinc = basetile & (TILE_INDEX_MASK | TILE_ATTR_PALETTE_MASK);
    const u16 baseor = basetile & (TILE_ATTR_PRIORITY_MASK | TILE_ATTR_VFLIP_MASK | TILE_ATTR_HFLIP_MASK);
    u16 column;
    for (column = 0; column < width; column++) {
        dest[column] = baseor | (u16)(source[column] + baseinc);
    }
}
int main(void){
    const u16 bases[]={0,0x2860,0xE7FF,0xF800,0xFFFF};
    u16 src[34],ref[34],fast[34];unsigned cases=0;
    for(unsigned base=0;base<5;base++)for(unsigned word=0;word<65536;word++){
        u16 width=(u16)(word%34);
        for(unsigned i=0;i<34;i++){src[i]=(u16)(word+i*37);ref[i]=fast[i]=0x3C3C;}
        prepareTileMapDataRowEx(ref,width,src,bases[base]);
        v3PrepareLogoRowData(fast,src,width,bases[base]);
        if(memcmp(ref,fast,sizeof(ref))){fprintf(stderr,"case %u mismatch\n",cases);return 1;}
        cases++;
    }
    printf("%u SGDK attribute-row cases passed: all source words, 5 bases, widths0..33 and tail guards\n",cases);return 0;
}
