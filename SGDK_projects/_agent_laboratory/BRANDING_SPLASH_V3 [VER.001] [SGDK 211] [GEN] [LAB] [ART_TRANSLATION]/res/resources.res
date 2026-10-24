// Branding intro assets built by tools/image-tools/build_branding_intro_assets.py.
// Every PNG is indexed, 8px aligned, and limited to a single 16-color palette.
IMAGE img_brand_fx_tiles "branding/brand_fx_tiles.png" BEST
IMAGE img_brand_engine_logo "branding/brand_engine_logo.png" BEST
IMAGE img_brand_author_logo "branding/brand_author_logo.png" BEST
IMAGE img_brand_project_logo "branding/brand_project_logo.png" BEST
IMAGE img_brand_presents_text "branding/brand_presents_text.png" BEST

// Branding intro audio uses SGDK 2.11 WAV resources for the XGM2 PCM path.
WAV brand_bell_forge "audio/branding/bell_forge.wav" XGM2 13300
WAV brand_typewriter_click "audio/branding/typewriter_click.wav" XGM2 6650
WAV brand_bell_terminal "audio/branding/bell_terminal.wav" XGM2 13300
WAV brand_stamp_whoosh "audio/branding/stamp_whoosh.wav" XGM2 13300
WAV brand_reverb_tail "audio/branding/reverb_tail.wav" XGM2 13300
WAV brand_hammer_slam "audio/branding/hammer_slam.wav" XGM2 13300
XGM2 mus_forge_brand "music/forge_brand_loop.vgm"

// Sonic-logo candidate V3. V010 remains preserved as a rejected historical take.
// V012 remains the positive reference; V013 and V014 were rejected for continuous, monotonous delivery. V015 uses clipped phrases, faster FM releases, short accents, and crystalline pings.
XGM2 mus_splash_v3 "music/splash_v3_sonic_logo_v4.vgm"
WAV sfx_splash_v3_energy_rise "audio/branding_splash_v3/splash_energy_rise_v3.wav" XGM2 13300
WAV sfx_splash_v3_mark_lock "audio/branding_splash_v3/splash_mark_lock_v3.wav" XGM2 13300
WAV sfx_splash_v3_sweep_pass "audio/branding_splash_v3/splash_sweep_pass_v3.wav" XGM2 13300
WAV sfx_splash_v3_tail "audio/branding_splash_v3/splash_tail_v3.wav" XGM2 13300

// =====================================================================
// branding_sequence_v2 — DECLARACOES PENDENTES DE ARTE
// Autoridade: doc/branding_sequence_contract.json
//
// Os 5 IMAGE brand_* acima sao PLACEHOLDERS desenhados por primitiva em
// tools/image-tools/build_branding_intro_assets.py. Estao declarados como
// source_kind=procedural_primitive / acceptance_status=placeholder em
// doc/asset_provenance_manifest.json e NUNCA podem ser promovidos a final.
//
// O agente de arte que entregar os assets do v2 deve, para cada linha:
//   1. produzir o PNG indexado (index 0 transparente, 15 cores visiveis);
//   2. descomentar a linha correspondente;
//   3. adicionar a entrada em doc/asset_provenance_manifest.json;
//   4. rodar audit_procedural_asset_provenance.py e o build pelo wrapper.
//
// Larguras/alturas de SPRITE sao em TILES e valem POR QUADRO do strip.
//
IMAGE   img_starfield_v2      "branding/starfield_320x224.png"           BEST
IMAGE   img_forge_bg_b        "branding/forge_bg_b_320x224.png"          BEST
IMAGE   img_forge_bg_a_props  "branding/forge_bg_a_props_320x224.png"    BEST
SPRITE  spr_forge_ember       "branding/spr_forge_ember_16x16_strip.png" 2 2 FAST 0
SPRITE  spr_forge_shard       "branding/spr_forge_shard_16x16_strip.png" 2 2 FAST 0
SPRITE  spr_forge_hammer      "branding/spr_forge_hammer_48x48_strip.png" 6 6 FAST 0
IMAGE   img_logo_engine_v2    "branding/logo_engine_224x64.png"          BEST
IMAGE   img_logo_author_v2    "branding/logo_author_192x32.png"          BEST
IMAGE   img_logo_project_v2   "branding/logo_project_224x48.png"         BEST
IMAGE   img_presents_text_v2  "branding/presents_text_96x16.png"         BEST
IMAGE   img_presents_bar_v2   "branding/presents_bar_8x8.png"            NONE
// =====================================================================

// Splash V3 visual development preview. Assets are indexed and remain
// placeholders pending future human review.
// NONE keeps tile bytes available for bounded DMA_QUEUE_COPY streaming.
IMAGE   img_splash_backdrop_v3 "branding_v3/splash_backdrop_v3_320x224.png" NONE
IMAGE   img_splash_backdrop_v3_v005 "branding_v3/splash_backdrop_v3_v005_320x224.png" NONE
IMAGE   img_splash_backdrop_v3_v006 "branding_v3/splash_backdrop_v3_v006_320x224.png" NONE
// V012 is a comparison-only runtime preview; keep V006 as the curatorial baseline.
IMAGE   img_splash_backdrop_v3_v012 "branding_v3/splash_backdrop_v3_v012_320x224.png" NONE
// V014 is a development-only visual preview; V006 remains the runtime baseline.
IMAGE   img_splash_backdrop_v3_v014 "branding_v3/splash_backdrop_v3_v014_320x224.png" NONE
// V015 is an isolated development preview; activate only with SPLASH_V3_BACKDROP_V015.
IMAGE   img_splash_backdrop_v3_v015 "branding_v3/splash_backdrop_v3_v015_320x224.png" NONE
// V016 is a soft-field comparison preview; activate only with SPLASH_V3_BACKDROP_V016.
IMAGE   img_splash_backdrop_v3_v016 "branding_v3/splash_backdrop_v3_v016_320x224.png" NONE
// V018 is a broad-facet WIP preview; activate only with SPLASH_V3_BACKDROP_V018.
IMAGE   img_splash_backdrop_v3_v018 "branding_v3/splash_backdrop_v3_v018_320x224.png" NONE
// V019 is a broken-floor/refined negative-space WIP; activate only with SPLASH_V3_BACKDROP_V019.
IMAGE   img_splash_backdrop_v3_v019 "branding_v3/splash_backdrop_v3_v019_320x224.png" NONE
// Splash V3 lettering B is an isolated WIP placeholder; source-level activation only, with pre-B baselines preserved.
IMAGE   img_splash_sgdk_v3     "branding_v3/splash_sgdk_wordmark_v3_224x48.png" NONE
IMAGE   img_splash_forge_v3    "branding_v3/splash_forge_wordmark_v3_192x32.png" NONE
SPRITE  spr_splash_particle_v3 "sprites/splash_particle_v3_8x8_strip.png" 1 1 NONE 0
