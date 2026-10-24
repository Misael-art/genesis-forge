
#include <stdint.h>
#include <stdio.h>
typedef uint8_t bool;typedef uint16_t u16;typedef int16_t s16;
#define TRUE 1
#define FALSE 0
#define START_PROFIL
#define END_PROFIL(x)
#define checkSpriteValid(a,b) ((void)0)
#define SPLASH_V3_MANUAL_TILE_FASTPATH 1
typedef struct { u16 maxNumTile; } SpriteDefinition;
typedef struct {u16 status,attribut;SpriteDefinition* definition;} Sprite;
static int vram,allocCalls,freeCalls,apiCalls;static u16 freedIndex;
static bool sParticleUniformGeometry;
static s16 VRAM_alloc(int *region,u16 count){(void)region;(void)count;allocCalls++;return 42;}
static void VRAM_free(int *region,u16 index){(void)region;freedIndex=index;freeCalls++;}
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
#define TILE_ATTR_MASK              (TILE_ATTR_PRIORITY_MASK | TILE_ATTR_PALETTE_MASK | TILE_ATTR_VFLIP_MASK | TILE_ATTR_HFLIP_MASK)
#define SPR_FLAG_AUTO_VRAM_ALLOC                0x0800
#define SPR_FLAG_AUTO_TILE_UPLOAD               0x0400
#define NEED_TILES_UPLOAD                   0x0004
static bool reference_setter(Sprite* sprite, s16 value)
{
    START_PROFIL

    // for debug
    checkSpriteValid(sprite, "reference_setter");

    s16 newInd;
    u16 status = sprite->status;
    u16 oldAttribut = sprite->attribut;

    if (status & SPR_FLAG_AUTO_VRAM_ALLOC)
    {
        // pass to manual allocation
        if (value != -1)
        {
            // remove auto vram alloc flag
            status &= ~SPR_FLAG_AUTO_VRAM_ALLOC;
            // release allocated VRAM first
            VRAM_free(&vram, oldAttribut & TILE_INDEX_MASK);
            // set fixed VRAM index
            newInd = value;

#ifdef SPR_DEBUG
            KLog_U2("reference_setter: #", getSpriteIndex(sprite), " passed to manual allocation, VRAM index =", value);
            KLog_U3("  released ", sprite->definition->maxNumTile, " tiles in VRAM at ", sprite->attribut & TILE_INDEX_MASK, ", remaining VRAM: ", VRAM_getFree(&vram));
#endif // SPR_DEBUG
        }
        // nothing to do --> just return TRUE
        else
        {
            END_PROFIL(PROFIL_SET_VRAM_IND)

            return TRUE;
        }
    }
    else
    {
        // pass to auto allocation
        if (value == -1)
        {
            // set auto vram alloc flag
            status |= SPR_FLAG_AUTO_VRAM_ALLOC;
            // allocate VRAM
            newInd = VRAM_alloc(&vram, sprite->definition->maxNumTile);

#ifdef SPR_DEBUG
            KLog_U1_("reference_setter: #", getSpriteIndex(sprite), " passed to auto allocation");
            KLog_U3("  allocated ", sprite->definition->maxNumTile, " tiles in VRAM at ", newInd, ", remaining VRAM: ", VRAM_getFree(&vram));
#endif // SPR_DEBUG

            // can't allocate ?
            if (newInd < 0)
            {
                // save status and return FALSE
                sprite->status = status;

                END_PROFIL(PROFIL_SET_VRAM_IND)

                return FALSE;
            }
        }
        // just use the new value for index
        else newInd = value;
    }

    // VRAM tile index changed ?
    if ((oldAttribut & TILE_INDEX_MASK) != (u16) newInd)
    {
        sprite->attribut = (oldAttribut & TILE_ATTR_MASK) | newInd;
        // auto tile upload enabled ? --> need to re upload tile to new location
        if (status & SPR_FLAG_AUTO_TILE_UPLOAD)
            status |= NEED_TILES_UPLOAD;
    }

    // save status
    sprite->status = status;

    END_PROFIL(PROFIL_SET_VRAM_IND)

    return TRUE;
}
static bool SPR_setVRAMTileIndex(Sprite *sprite,s16 value){apiCalls++;return reference_setter(sprite,value);}
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
int main(void){
    const u16 indices[]={0,1,96,1740,2047,65535};
    SpriteDefinition definition={1};unsigned cases=0;
    for(int geometry=0;geometry<2;geometry++)for(int flags=0;flags<4;flags++)for(int tags=0;tags<32;tags++)for(int old=0;old<5;old++)for(int next=0;next<6;next++){
        Sprite ref={(u16)(0x8002|(flags&1?SPR_FLAG_AUTO_VRAM_ALLOC:0)|(flags&2?SPR_FLAG_AUTO_TILE_UPLOAD:0)),(u16)((tags<<11)|indices[old]),&definition};
        Sprite fast=ref;int expectedAlloc,expectedFree;u16 expectedFreed;
        allocCalls=freeCalls=apiCalls=0;freedIndex=0;
        reference_setter(&ref,(s16)indices[next]);expectedAlloc=allocCalls;expectedFree=freeCalls;expectedFreed=freedIndex;
        allocCalls=freeCalls=apiCalls=0;freedIndex=0;sParticleUniformGeometry=(bool)geometry;
        v3SetPreloadedParticleTile(&fast,indices[next]);
        int eligible=geometry && flags==0 && indices[next]<=TILE_INDEX_MASK;
        if(ref.status!=fast.status || ref.attribut!=fast.attribut || allocCalls!=expectedAlloc || freeCalls!=expectedFree || freedIndex!=expectedFreed || apiCalls!=(eligible?0:1)){
            fprintf(stderr,"case %u mismatch geometry=%d flags=%d tags=%d old=%u next=%u\n",cases,geometry,flags,tags,indices[old],indices[next]);return 1;
        }
        cases++;
    }
    printf("%u actual-SGDK differential cases passed: attributes, status, allocation/release calls and guarded fallback\n",cases);
    return 0;
}
