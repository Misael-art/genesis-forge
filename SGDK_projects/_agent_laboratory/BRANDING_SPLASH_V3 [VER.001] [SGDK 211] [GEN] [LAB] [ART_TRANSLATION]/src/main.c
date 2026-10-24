#include <genesis.h>

#include "core/app.h"
#include "system/input.h"
#include "system/runtime_probe.h"

int main(bool hardReset)
{
    APP_boot(hardReset);

    while (TRUE)
    {
        INPUT_update();
        APP_update();
        SPR_update();
        MDRuntimeProbe_sampleDmaQueue();
        SYS_doVBlankProcess();
#if !defined(SPLASH_V3_DIAGNOSTIC_NO_PROBE_TICK)
        MDRuntimeProbe_tick();
#endif
    }

    return 0;
}
