#include <genesis.h>
#include <sprite_eng.h>
#include <dma.h>

#include "game_vars.h"
#include "system/runtime_probe.h"

/*
 * Canonical ROM-side readiness probe. See system/runtime_probe.h for contract.
 * This module is deliberately small; projects copy it as-is, then tune the
 * warmup and period constants only if budget analysis justifies it.
 */

#define PROBE_MAGIC_HI 0x4D44 /* "MD" */
#define PROBE_MAGIC_LO 0x5254 /* "RT" */
#define PROBE_SCHEMA_VERSION 1
#define PROBE_SRAM_SCHEMA_VERSION 1
#define PROBE_TARGET_FPS_NTSC 60
#define PROBE_TARGET_FPS_PAL 50
#define PROBE_CPU_BUDGET_THRESHOLD 100
#define PROBE_SAMPLE_OFFSET 32
#define PROBE_SCENE_WARMUP_FRAMES 90
/* Janela fixa de medicao: para de acumular apos N quadros pos-warmup (0 = sem limite).
 * Sem ela a janela depende do tempo de parede da captura, e como a luta e deterministica
 * ROMs diferentes eram medidas sobre trechos diferentes da luta (A/B invalido). */
#ifndef PROBE_MEASURE_FRAMES
#define PROBE_MEASURE_FRAMES 1200
#endif
/* A primeira janela que fecha fica travada: exporta uma vez e ignora re-entradas de cena.
 * Sem isso uma captura longa caia na luta SEGUINTE (o fim da luta volta ao attract e
 * zera a sonda), e o quociente vinha de outro trecho de jogo. */
static u8 s_windowLatched;
#define PROBE_SCANLINE_COUNT 224
#define PROBE_SCANLINE_SAMPLE_GROUPS 4
#define PROBE_SCANLINE_GROUP_LENGTH (PROBE_SCANLINE_COUNT / PROBE_SCANLINE_SAMPLE_GROUPS)
#define PROBE_VLAB_OFFSET 0x200
#define PROBE_VLAB_SCHEMA_VERSION 2
#define PROBE_VLAB_RANGE_CAPACITY 4
/* 26 metricas + 3 pares hi/lo com o quadro de cada pico.
 *
 * PORQUE: uma captura do GOTHAM mediu max_scanline_sprites=21 contra o teto de
 * 20 e nao houve como atribuir o pico a nada — o maximo era anonimo. Maximo sem
 * quadro diz que o teto foi violado e nao diz por quem, o que nao fecha
 * diagnostico nenhum.
 *
 * Os pares vao no FIM do bloco para nao deslocar words[0..25], que
 * seal_fresh_evidence_bundle.py ja consome por indice fixo. */
#define PROBE_VLAB_METRIC_WORDS 52
#define PROBE_VLAB_PALETTE_WORDS 64
#define PROBE_VLAB_MEASUREMENT_TRAILER_WORDS 2
#define PROBE_VLAB_TOTAL_BYTES (8 + ((PROBE_VLAB_METRIC_WORDS + PROBE_VLAB_PALETTE_WORDS + PROBE_VLAB_MEASUREMENT_TRAILER_WORDS) * 2))

volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

static u16 s_prevCpuLoad;
static bool s_hasPrevSample;
static u16 s_prevScene;
static u16 s_lastExportSamples;
static u32 s_lastExportFrame;
static u16 s_sceneWarmupFrames;
static u32 s_heartbeatCounter;
static u16 s_scanlineCursor;
static u16 s_vlabPalette[PROBE_VLAB_PALETTE_WORDS];
static u16 s_vlabRanges[PROBE_VLAB_RANGE_CAPACITY][2];
static u16 s_vlabRangeCount;
static u16 s_runtimeDmaMaxBytes;
static u16 s_runtimeDmaMaxEntries;
static u16 s_runtimeDmaMaxTransferBytes;
static u16 s_runtimeDmaPeakFrameHi;
static u16 s_runtimeDmaPeakFrameLo;
static u16 s_preloadMaxBytes;
static u16 s_preloadMaxEntries;
static u16 s_preloadMaxTransferBytes;
static u32 s_preloadPeakFrame;
static u16 s_preloadObservationCount;
static bool s_dmaPreloadActive;
static bool s_dmaPreloadFinishPending;

/* Diferencas por linha: +1/+largura na primeira linha do sprite e -1/-largura
 * na linha seguinte a ultima. Um bitmap marca as linhas tocadas e a varredura
 * visita so elas: entre duas fronteiras a contagem nao muda, entao o pico nas
 * fronteiras e o pico exato das 224 linhas.
 *
 * PORQUE (medido no BlastEm com amostragem de PC):
 *  - a versao original incrementava cada linha coberta por cada sprite; ao
 *    somar a largura no mesmo laco a propria sonda levou a luta de 28% para 78%
 *    de quadros acima do orcamento, com o jogo identico;
 *  - a versao com soma prefixa das 224 linhas ainda custava 12,2% do quadro
 *    (~13k ciclos), dentro do quadro que ela mede.
 *
 * Pixels por linha sao o segundo limite do VDP (H40 = 320 px/linha): poucos
 * sprites largos tambem causam dropout. [20] pico de px, [21] quadros com linha
 * acima da largura da tela, [22] quadros com linha > 20 sprites, [30] quadros
 * medidos apos o warmup (denominador honesto do over_budget em [10]). */
static u16 s_peakWidth;
static bool sScanlineInvalid;

/* Store the frame at the same instant a measured peak changes. */
static void probe_note_peak_frame(u16 slot)
{
    const u32 frame = gApp.totalFrames;
    g_mdRuntimeProbe[slot] = (u16)((frame >> 16) & 0xFFFF);
    g_mdRuntimeProbe[slot + 1] = (u16)(frame & 0xFFFF);
}

#if defined(SPLASH_V3_SAT_PRESSURE_PROBE)
/* Low 9 bits hold width in tiles (<=80*4=320), high bits hold count
 * (<=80). The largest prefix is 80*512+320=41280, below 65536.
 * Unsigned endpoint subtraction and accumulation wrap modulo 65536. */
static u16 sSatPressureDelta[PROBE_SCANLINE_COUNT + 1];

static u16 measure_max_scanline_sprites(void)
{
    u16 index = 0;
    u16 remaining = SAT_MAX_SIZE;
    u16 line;
    u16 pressure = 0;
    u16 peakCount = 0;
    u16 peakWidthTiles = 0;

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
            sSatPressureDelta[start] = (u16)(sSatPressureDelta[start] + packed);
            sSatPressureDelta[end] = (u16)(sSatPressureDelta[end] - packed);
        }
        index = sprite->link & 0x7Fu;
        if (index == 0) break;
        if (index >= SAT_MAX_SIZE) goto invalid_sat;
    } while (--remaining != 0);
    if (index != 0) goto invalid_sat;

    for (line = 0; line <= PROBE_SCANLINE_COUNT; line++) {
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
#else
#define PROBE_TOUCHED_WORDS ((PROBE_SCANLINE_COUNT + 1 + 31) / 32)
static s8 s_lineCountDelta[PROBE_SCANLINE_COUNT + 1];
static s16 s_lineWidthDelta[PROBE_SCANLINE_COUNT + 1];
static u32 s_lineTouched[PROBE_TOUCHED_WORDS];

/*
 * Conta TODAS as 224 linhas por quadro, em vez de amostrar 4 com cursor
 * rotativo.
 *
 * PORQUE: a versao por amostragem olhava 4 linhas de 224 e girava o cursor um
 * passo por quadro. Um pico transitorio numa linha especifica tinha chance
 * baixissima de coincidir com a amostra, e a probe reportou 6 numa cena em que a
 * varredura do simulador media 23 — falso verde para uma configuracao que
 * violaria o limite de sprite por linha e causaria dropout no console.
 *
 * O custo deste caminho legado deve ser medido na ROM; contagem de operacoes
 * C nao demonstra que ele cabe no deadline observado.
 */
static void probe_mark_line(s16 line, s8 dc, s16 dw)
{
    s_lineCountDelta[line] += dc;
    s_lineWidthDelta[line] += dw;
    s_lineTouched[(u16)line >> 5] |= 1UL << (line & 31);
}

static u16 measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 peak = 0;
    s16 count = 0;
    s16 width = 0;
    u8 k;

    s_peakWidth = 0;
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

                probe_mark_line(start, 1, w);
                probe_mark_line(end, -1, (s16)-w);
            }
        }
        cursor = cursor->next;
    }

    /* varre so as linhas marcadas, em ordem crescente, zerando para o proximo quadro */
    for (k = 0; k < PROBE_TOUCHED_WORDS; k++) {
        u32 bits = s_lineTouched[k];
        s_lineTouched[k] = 0;
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
            count += s_lineCountDelta[line];
            width += s_lineWidthDelta[line];
            s_lineCountDelta[line] = 0;
            s_lineWidthDelta[line] = 0;
            if ((u16)count > peak) peak = (u16)count;
            if ((u16)width > s_peakWidth) s_peakWidth = (u16)width;
        }
    }

    return peak;
}
#endif

static void sram_write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void sram_write_visual_word(u32 *offset, u16 value)
{
    sram_write_u16be(*offset, value);
    *offset += 2;
}

static void export_visual_probe_to_sram(void)
{
    u32 offset = PROBE_VLAB_OFFSET;
    u32 frame = gApp.totalFrames;
    u16 i;

    PAL_getColors(0, s_vlabPalette, PROBE_VLAB_PALETTE_WORDS);

    SRAM_enable();
    SRAM_writeByte(offset + 0, 'V');
    SRAM_writeByte(offset + 1, 'L');
    SRAM_writeByte(offset + 2, 'A');
    SRAM_writeByte(offset + 3, 'B');
    sram_write_u16be(offset + 4, PROBE_VLAB_SCHEMA_VERSION);
    sram_write_u16be(offset + 6, PROBE_VLAB_TOTAL_BYTES);

    offset += 8;
    sram_write_visual_word(&offset, g_mdRuntimeProbe[5]);
    sram_write_visual_word(&offset, (u16)((frame >> 16) & 0xFFFF));
    sram_write_visual_word(&offset, (u16)(frame & 0xFFFF));
    sram_write_visual_word(&offset, VDP_getScreenWidth());
    sram_write_visual_word(&offset, VDP_getScreenHeight());
    sram_write_visual_word(&offset, VDP_getPlaneWidth());
    sram_write_visual_word(&offset, VDP_getPlaneHeight());
    sram_write_visual_word(&offset, VDP_getHorizontalScrollingMode());
    sram_write_visual_word(&offset, VDP_getVerticalScrollingMode());
    sram_write_visual_word(&offset, VDP_getBGAAddress());
    sram_write_visual_word(&offset, VDP_getBGBAddress());
    sram_write_visual_word(&offset, VDP_getWindowAddress());
    sram_write_visual_word(&offset, VDP_getSpriteListAddress());
    sram_write_visual_word(&offset, VDP_getHScrollTableAddress());
    sram_write_visual_word(&offset, VDP_getBackgroundColor());
    sram_write_visual_word(&offset, g_mdRuntimeProbe[8]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[9]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[10]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[11]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[13]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[14]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[16]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[17]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[4]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[18]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[19]);
    /* words[26..31]: quadro de cada pico, hi/lo. Anexados no fim do bloco. */
    sram_write_visual_word(&offset, g_mdRuntimeProbe[24]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[25]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[26]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[27]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[28]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[29]);

    sram_write_visual_word(&offset, s_runtimeDmaMaxBytes);
    sram_write_visual_word(&offset, s_runtimeDmaMaxEntries);
    sram_write_visual_word(&offset, s_runtimeDmaMaxTransferBytes);
    sram_write_visual_word(&offset, s_runtimeDmaPeakFrameHi);
    sram_write_visual_word(&offset, s_runtimeDmaPeakFrameLo);
    sram_write_visual_word(&offset, s_preloadMaxBytes);
    sram_write_visual_word(&offset, s_preloadMaxEntries);
    sram_write_visual_word(&offset, s_preloadMaxTransferBytes);
    sram_write_visual_word(&offset, (u16)((s_preloadPeakFrame >> 16) & 0xFFFF));
    sram_write_visual_word(&offset, (u16)(s_preloadPeakFrame & 0xFFFF));
    sram_write_visual_word(&offset, s_preloadObservationCount);
    sram_write_visual_word(&offset, (u16)(s_vlabRangeCount & 0xFFFF));

    for (i = 0; i < PROBE_VLAB_RANGE_CAPACITY; i++) {
        sram_write_visual_word(&offset, s_vlabRanges[i][0]);
        sram_write_visual_word(&offset, s_vlabRanges[i][1]);
    }

    for (i = 0; i < PROBE_VLAB_PALETTE_WORDS; i++) {
        sram_write_visual_word(&offset, s_vlabPalette[i]);
    }
    /* Preserve the legacy metric and CRAM offsets. Schema 2 appends the
     * measured denominator and compiled target after the 64 palette words. */
    sram_write_visual_word(&offset, g_mdRuntimeProbe[30]);
    sram_write_visual_word(&offset, (u16)PROBE_MEASURE_FRAMES);
    SRAM_disable();
}

/* Keep the legacy readiness block and the visual evidence block on the same
 * sampling boundary; a VLAB-only periodic checkpoint may be up to 59 frames old. */
static void export_probe_snapshot(void)
{
    MDRuntimeProbe_exportToSRAM();
    export_visual_probe_to_sram();
}

static void reset_scene_metrics(u16 sceneId, u16 cpuLoad)
{
    u16 i;

    if (s_windowLatched) {
        return;
    }
    g_mdRuntimeProbe[5] = sceneId;
    g_mdRuntimeProbe[8] = 0;
    g_mdRuntimeProbe[9] = 0;
    g_mdRuntimeProbe[10] = 0;
    g_mdRuntimeProbe[11] = 0;
    g_mdRuntimeProbe[13] = 0;
    g_mdRuntimeProbe[14] = 0;
    g_mdRuntimeProbe[15] = 0;
    g_mdRuntimeProbe[16] = 0;
    g_mdRuntimeProbe[17] = 0;
    g_mdRuntimeProbe[18] = 0;
    g_mdRuntimeProbe[19] = 0;
    g_mdRuntimeProbe[20] = 0;
    g_mdRuntimeProbe[21] = 0;
    g_mdRuntimeProbe[22] = 0;
    g_mdRuntimeProbe[30] = 0;
    g_mdRuntimeProbe[MD_RUNTIME_PROBE_INVALID_SAT_WORD] = 0;
    for (i = 24; i <= 29; i++) {
        g_mdRuntimeProbe[i] = 0;   /* quadros de pico zeram junto com os picos */
    }

    for (i = 0; i < MD_RUNTIME_PROBE_MAX_SAMPLES; i++) {
        g_mdRuntimeProbe[PROBE_SAMPLE_OFFSET + i] = 0;
    }

    s_prevCpuLoad = cpuLoad;
    s_hasPrevSample = FALSE;
    s_lastExportSamples = 0;
    s_lastExportFrame = 0;
    s_sceneWarmupFrames = PROBE_SCENE_WARMUP_FRAMES;
    s_scanlineCursor = 0;
    s_vlabRangeCount = 0;
    for (i = 0; i < PROBE_VLAB_RANGE_CAPACITY; i++) {
        s_vlabRanges[i][0] = 0;
        s_vlabRanges[i][1] = 0;
    }
    s_runtimeDmaMaxBytes = 0;
    s_runtimeDmaMaxEntries = 0;
    s_runtimeDmaMaxTransferBytes = 0;
    s_runtimeDmaPeakFrameHi = 0;
    s_runtimeDmaPeakFrameLo = 0;
    s_preloadMaxBytes = 0;
    s_preloadMaxEntries = 0;
    s_preloadMaxTransferBytes = 0;
    s_preloadPeakFrame = 0;
    s_preloadObservationCount = 0;
    s_dmaPreloadActive = FALSE;
    s_dmaPreloadFinishPending = FALSE;
}

static u16 clamp_u16(s32 value)
{
    if (value < 0) return 0;
    if (value > 0xFFFF) return 0xFFFF;
    return (u16) value;
}

void MDRuntimeProbe_writeHeartbeat(void)
{
    /*
     * Rolling READY heartbeat at SRAM[HEARTBEAT_OFFSET]:
     *   [0..4] 'R','E','A','D','Y'
     *   [5..7] 3-byte big-endian rolling counter (advances once per write)
     *
     * The wrapper only checks bytes 0..4 via Test-MDReadyHeartbeat; the
     * rolling counter exists so analytic tooling can confirm the heartbeat
     * is being re-asserted and distinguish live runs from a single stale
     * write that happened to survive a sandbox reset.
     */
    u32 offset = MD_RUNTIME_PROBE_HEARTBEAT_OFFSET;

    SRAM_enable();
    SRAM_writeByte(offset + 0, (u8) 'R');
    SRAM_writeByte(offset + 1, (u8) 'E');
    SRAM_writeByte(offset + 2, (u8) 'A');
    SRAM_writeByte(offset + 3, (u8) 'D');
    SRAM_writeByte(offset + 4, (u8) 'Y');
    SRAM_writeByte(offset + 5, (u8) ((s_heartbeatCounter >> 16) & 0xFF));
    SRAM_writeByte(offset + 6, (u8) ((s_heartbeatCounter >> 8) & 0xFF));
    SRAM_writeByte(offset + 7, (u8) (s_heartbeatCounter & 0xFF));
    SRAM_disable();

    s_heartbeatCounter++;
}

void MDRuntimeProbe_noteSpriteAlloc(u16 spawned, u16 failed)
{
    g_mdRuntimeProbe[18] = spawned;
    g_mdRuntimeProbe[19] = failed;
}

void MDRuntimeProbe_onSceneEnter(u16 sceneId)
{
    s_prevScene = sceneId;
    reset_scene_metrics(sceneId, SYS_getCPULoad());
}

void MDRuntimeProbe_noteVramLoadRange(u16 startTile, u16 tileCount)
{
    const u16 overflow = (u16)(s_vlabRangeCount & 0x8000u);
    const u16 count = (u16)(s_vlabRangeCount & 0x7FFFu);

    if (tileCount == 0) return;
    if (count >= PROBE_VLAB_RANGE_CAPACITY) {
        s_vlabRangeCount = (u16)(overflow | 0x8000u | count);
        return;
    }

    s_vlabRanges[count][0] = startTile;
    s_vlabRanges[count][1] = tileCount;
    s_vlabRangeCount = (u16)(overflow | (count + 1u));
}

void MDRuntimeProbe_beginDmaPreload(void)
{
    s_preloadMaxBytes = 0;
    s_preloadMaxEntries = 0;
    s_preloadMaxTransferBytes = 0;
    s_preloadPeakFrame = 0;
    s_preloadObservationCount = 0;
    s_dmaPreloadActive = TRUE;
    s_dmaPreloadFinishPending = FALSE;
}

void MDRuntimeProbe_finishDmaPreloadAfterCurrentFrame(void)
{
    if (s_dmaPreloadActive) s_dmaPreloadFinishPending = TRUE;
}

void MDRuntimeProbe_sampleDmaQueue(void)
{
    const u16 queueEntries = DMA_getQueueSize();
    const u16 queueBytes = DMA_getQueueTransferSize();
    u16 maxTransferBytes = 0;
    u16 index;

    for (index = 0; index < queueEntries; index++) {
        const DMAOpInfo *op = &dmaQueues[index];
        const u16 transferWords = (u16)(((op->regLenH & 0x00FFu) << 8) |
                                         (op->regLenL & 0x00FFu));
        const u32 transferBytes32 = (u32)transferWords * 2u;
        const u16 transferBytes = (transferBytes32 > 0xFFFFu)
            ? 0xFFFFu : (u16)transferBytes32;

        if (transferBytes > maxTransferBytes) maxTransferBytes = transferBytes;
    }

    if (queueBytes > s_runtimeDmaMaxBytes) {
        s_runtimeDmaMaxBytes = queueBytes;
        s_runtimeDmaPeakFrameHi = (u16)((gApp.totalFrames >> 16) & 0xFFFFu);
        s_runtimeDmaPeakFrameLo = (u16)(gApp.totalFrames & 0xFFFFu);
    }
    if (queueEntries > s_runtimeDmaMaxEntries) s_runtimeDmaMaxEntries = queueEntries;
    if (maxTransferBytes > s_runtimeDmaMaxTransferBytes) {
        s_runtimeDmaMaxTransferBytes = maxTransferBytes;
    }

    if (s_dmaPreloadActive) {
        s_preloadObservationCount++;
        if (queueBytes > s_preloadMaxBytes) {
            s_preloadMaxBytes = queueBytes;
            s_preloadPeakFrame = gApp.totalFrames;
        }
        if (queueEntries > s_preloadMaxEntries) s_preloadMaxEntries = queueEntries;
        if (maxTransferBytes > s_preloadMaxTransferBytes) {
            s_preloadMaxTransferBytes = maxTransferBytes;
        }
        if (s_dmaPreloadFinishPending) {
            s_dmaPreloadActive = FALSE;
            s_dmaPreloadFinishPending = FALSE;
        }
    }
}

void MDRuntimeProbe_init(void)
{
    u16 i;

    for (i = 0; i < MD_RUNTIME_PROBE_WORD_COUNT; i++) {
        g_mdRuntimeProbe[i] = 0;
    }

    g_mdRuntimeProbe[0] = PROBE_MAGIC_HI;
    g_mdRuntimeProbe[1] = PROBE_MAGIC_LO;
    g_mdRuntimeProbe[2] = PROBE_SCHEMA_VERSION;
    g_mdRuntimeProbe[4] = SYS_isPAL() ? PROBE_TARGET_FPS_PAL : PROBE_TARGET_FPS_NTSC;
    g_mdRuntimeProbe[23] = PROBE_CPU_BUDGET_THRESHOLD;
    s_prevScene = (u16) gApp.currentScene;
    s_heartbeatCounter = 0;
    reset_scene_metrics(s_prevScene, SYS_getCPULoad());
}

void MDRuntimeProbe_exportToSRAM(void)
{
    const u16 wordCount = (u16) MD_RUNTIME_PROBE_WORD_COUNT;
    const u16 totalBytes = (u16)(8u + 2u + (wordCount * 2u));
    u32 offset = MD_RUNTIME_PROBE_SRAM_OFFSET;
    u16 i;

    SRAM_enable();

    SRAM_writeByte(offset + 0, 'M');
    SRAM_writeByte(offset + 1, 'D');
    SRAM_writeByte(offset + 2, 'R');
    SRAM_writeByte(offset + 3, 'T');
    sram_write_u16be(offset + 4, PROBE_SRAM_SCHEMA_VERSION);
    sram_write_u16be(offset + 6, totalBytes);
    sram_write_u16be(offset + 8, wordCount);

    offset += 10;
    for (i = 0; i < wordCount; i++) {
        sram_write_u16be(offset, g_mdRuntimeProbe[i]);
        offset += 2;
    }

    SRAM_disable();
}

void MDRuntimeProbe_tick(void)
{
    u16 cpuLoad = SYS_getCPULoad();
    u16 sceneId = (u16) gApp.currentScene;
    u16 samplesRecorded = g_mdRuntimeProbe[9];
    u16 maxScanlineSprites;
    s32 jitterDelta = (s32) cpuLoad - (s32) s_prevCpuLoad;
    u16 jitter = (u16) ((jitterDelta < 0) ? -jitterDelta : jitterDelta);

    if (sceneId != s_prevScene) {
        s_prevScene = sceneId;
        reset_scene_metrics(sceneId, cpuLoad);
        samplesRecorded = g_mdRuntimeProbe[9];
        jitter = 0;
    }

    g_mdRuntimeProbe[5] = sceneId;
    g_mdRuntimeProbe[8]++;

    if (s_sceneWarmupFrames > 0) {
        s_sceneWarmupFrames--;
        s_prevCpuLoad = cpuLoad;
        s_hasPrevSample = FALSE;
        return;
    }

    /*
     * Rolling heartbeat: re-assert READY in SRAM at HEARTBEAT_OFFSET every
     * MD_RUNTIME_PROBE_HEARTBEAT_PERIOD frames post-warmup. A single missed
     * flush on the emulator side cannot starve the wrapper's detection loop
     * because the tag will be rewritten on the next period.
     */
    if ((g_mdRuntimeProbe[8] % MD_RUNTIME_PROBE_HEARTBEAT_PERIOD) == 0u) {
        MDRuntimeProbe_writeHeartbeat();
    }

    if (PROBE_MEASURE_FRAMES && g_mdRuntimeProbe[30] >= PROBE_MEASURE_FRAMES) {
        if (!s_windowLatched) {                     /* janela fechada: exporta 1x e congela */
            s_windowLatched = 1;
            export_probe_snapshot();
        }
        return;
    }
    g_mdRuntimeProbe[30]++;
    if (cpuLoad > PROBE_CPU_BUDGET_THRESHOLD) {
        g_mdRuntimeProbe[10]++;
    }
    if (cpuLoad > g_mdRuntimeProbe[11]) {
        g_mdRuntimeProbe[11] = cpuLoad;
        probe_note_peak_frame(26);
    }
    if (s_hasPrevSample && jitter > g_mdRuntimeProbe[13]) {
        g_mdRuntimeProbe[13] = jitter;
    }

    maxScanlineSprites = measure_max_scanline_sprites();
    if (sScanlineInvalid) g_mdRuntimeProbe[MD_RUNTIME_PROBE_INVALID_SAT_WORD]++;
    if (maxScanlineSprites > g_mdRuntimeProbe[14]) {
        g_mdRuntimeProbe[14] = maxScanlineSprites;
        probe_note_peak_frame(24);
    }
    if (maxScanlineSprites > 20) g_mdRuntimeProbe[22]++;
    if (s_peakWidth > g_mdRuntimeProbe[20]) g_mdRuntimeProbe[20] = s_peakWidth;
    if (s_peakWidth > VDP_getScreenWidth()) g_mdRuntimeProbe[21]++;

    if (g_mdRuntimeProbe[15] < 1) g_mdRuntimeProbe[15] = 1;
    /*
     * [16] instantaneo, [17] MAXIMO acumulado na cena.
     *
     * A versao anterior gravava [17] = 1, uma constante, e exportava isso como
     * `active_sprite_count`. O campo nunca mediu nada. E [16] guardava o valor
     * do quadro do export, que no ato 3 e zero — entao os dois campos que
     * existiam para responder "quantos sprites estao vivos" nao respondiam.
     */
    g_mdRuntimeProbe[16] = clamp_u16(SPR_getNumActiveSprite());
    if (g_mdRuntimeProbe[16] > g_mdRuntimeProbe[17]) {
        g_mdRuntimeProbe[17] = g_mdRuntimeProbe[16];
        probe_note_peak_frame(28);
    }

    if (samplesRecorded < MD_RUNTIME_PROBE_MAX_SAMPLES) {
        g_mdRuntimeProbe[PROBE_SAMPLE_OFFSET + samplesRecorded] = cpuLoad;
        g_mdRuntimeProbe[9] = samplesRecorded + 1;
    }

    s_prevCpuLoad = cpuLoad;
    s_hasPrevSample = TRUE;

    samplesRecorded = g_mdRuntimeProbe[9];
    /*
     * Re-exporta a cada 60 quadros ENQUANTO a cena roda, nao apenas quando a
     * contagem de amostras muda.
     *
     * PORQUE: o buffer de amostras satura em 32 e a condicao antiga
     * (`samplesRecorded != s_lastExportSamples`) parava de disparar. A probe
     * exportava uma unica vez, no quadro 151, e o maximo acumulado cobria so
     * F90-F151. Qualquer pico posterior — no caso desta cena, a convergencia
     * dos estilhacos a partir de F152 — nunca chegava a SRAM, e a captura
     * reportava um numero baixo com aparencia de aprovado.
     *
     * Agora a ultima exportacao carrega o maximo de toda a cena ate ali.
     */
    if (samplesRecorded > 0 && ((gApp.totalFrames - s_lastExportFrame) >= 60u)) {
        export_probe_snapshot();
        s_lastExportSamples = samplesRecorded;
        s_lastExportFrame = gApp.totalFrames;
    }
}
