#include "genesis.h"

__attribute__((externally_visible))
const ROMHeader rom_header = {
#if (ENABLE_BANK_SWITCH != 0)
    "SEGA SSF        ",
#elif (MODULE_MEGAWIFI != 0)
    "SEGA MEGAWIFI   ",
#else
    "SEGA MEGA DRIVE ",
#endif
    "(C)SGDK 2024    ",
#if defined(SPLASH_V3_VISUAL_PREVIEW) || defined(SPLASH_V3_MENU_HANDOFF)
    "SGDK FORGE SPLASH V3 DEV PREVIEW               ",
    "SGDK FORGE SPLASH V3 DEV PREVIEW               ",
#elif defined(SPLASH_V3_AUDIO_PREVIEW)
    "SGDK FORGE V3 AUDIO PREVIEW",
    "SGDK FORGE V3 AUDIO PREVIEW",
#else
    "A FORJA V2 LAB BASELINE                       ",
    "A FORJA V2 LAB BASELINE                       ",
#endif
    "GM 00000000-00",
    0x000,
    "JD              ",
    0x00000000,
#if (ENABLE_BANK_SWITCH != 0)
    0x003FFFFF,
#else
    0x000FFFFF,
#endif
    0xE0FF0000,
    0xE0FFFFFF,
    "RA",
    0xF820,
    0x00200000,
    0x0020FFFF,
    "            ",
    "DEMONSTRATION PROGRAM                   ",
    "JUE             "
};
