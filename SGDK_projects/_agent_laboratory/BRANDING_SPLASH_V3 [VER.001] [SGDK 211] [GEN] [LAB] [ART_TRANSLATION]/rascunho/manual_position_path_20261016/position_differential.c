
#include <stdint.h>
#include <stdio.h>
typedef uint16_t u16;typedef int16_t s16;
typedef struct {u16 status;s16 x,y;} Sprite;
#define START_PROFIL
#define END_PROFIL(x)
#define checkSpriteValid(a,b) ((void)0)
#define SPLASH_V3_MANUAL_POSITION_FASTPATH 1
static int apiCalls;
#define SPR_FLAG_AUTO_VISIBILITY                0x0200
#define NEED_VISIBILITY_UPDATE              0x0001
static void reference_setter(Sprite* sprite, s16 x, s16 y)
{
    START_PROFIL

    const s16 newx = x + 0x80;
    const s16 newy = y + 0x80;

#ifdef SPR_DEBUG
    KLog_U3("reference_setter: #", getSpriteIndex(sprite), "  X=", newx, " Y=", newy);
#endif // SPR_DEBUG

    // for debug
    checkSpriteValid(sprite, "reference_setter");

    if ((sprite->x != newx) || (sprite->y != newy))
    {
        sprite->x = newx;
        sprite->y = newy;

        // need to recompute visibility if auto visibility is enabled
        if (sprite->status & SPR_FLAG_AUTO_VISIBILITY)
            sprite->status |= NEED_VISIBILITY_UPDATE;
    }

    END_PROFIL(PROFIL_SET_ATTRIBUTE)
}
static void SPR_setPosition(Sprite *sprite,s16 x,s16 y){apiCalls++;reference_setter(sprite,x,y);}
static void v3SetEnergyPosition(Sprite *sprite, s16 x, s16 y)
{
#if defined(SPLASH_V3_MANUAL_POSITION_FASTPATH) && !defined(SPR_DEBUG)
    /* SGDK 2.11 SPR_setPosition only writes biased x/y in manual visibility
     * mode. VISIBLE/HIDDEN owns that mode here; preserve the API otherwise. */
    if ((sprite->status & SPR_FLAG_AUTO_VISIBILITY) == 0) {
        sprite->x = (s16)(x + 0x80);
        sprite->y = (s16)(y + 0x80);
        return;
    }
#endif
    SPR_setPosition(sprite, x, y);
}
int main(void){
    const s16 points[]={-32768,-32767,-129,-128,-32,-4,0,4,72,224,320,32766,32767};
    unsigned cases=0;
    for(int flags=0;flags<4;flags++)for(unsigned a=0;a<13;a++)for(unsigned b=0;b<13;b++)
    for(unsigned c=0;c<13;c++)for(unsigned d=0;d<13;d++){
        Sprite ref={(u16)(0xA00A|(flags&1?SPR_FLAG_AUTO_VISIBILITY:0)|(flags&2?NEED_VISIBILITY_UPDATE:0)),points[a],points[b]};
        Sprite fast=ref;apiCalls=0;
        reference_setter(&ref,points[c],points[d]);
        v3SetEnergyPosition(&fast,points[c],points[d]);
        if(ref.x!=fast.x || ref.y!=fast.y || ref.status!=fast.status || apiCalls!=(flags&1?1:0)){
            fprintf(stderr,"case %u mismatch\n",cases);return 1;
        }
        cases++;
    }
    printf("%u SGDK position cases passed, manual/auto visibility, dirty flags and signed endpoints\n",cases);
    return 0;
}
