# 13 - Especificacao Tecnica por Cena - BRANDING_SPLASH_V3

Escopo: preview WIP isolado da abertura no laboratorio. Este documento nao autoriza promocao, release ou alteracao do template/consumidores.

## Estado atual

| Eixo | Estado | Evidencia |
|---|---|---|
| Direcao | Splash V3 em desenvolvimento; revisao futura autorizada | `doc/curation/splash_v3_user_development_decision_20261014.md` |
| Runtime | Sete beats WIP em `SPLASH_V3_VISUAL_PREVIEW`; o handoff de menu tambem foi buildado e observado em ROM separada | `src/scenes/scene_branding_v3.c`, `src/scenes/scene_menu.c`, `src/core/app.c` |
| Recursos | V006 continua default. V019 é um fundo placeholder opt-in; lettering B continua WIP; VGM V4 e quatro cues seguem sem aprovação auditiva | `res/resources.res`, `doc/asset_provenance_manifest.json`, `doc/17-audio-design.md` |
| Sweep v003 | Histórico de execução; usuário reportou fagulhas aglutinadas e contorno pouco definido durante o escurecimento | ROM SHA `558fee0aabbee64ea98582a47fd9284866c649f02f2add179b6d0085a9e151ae`; vídeo BlastEm em `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/` |
| Sweep v004 | Candidato disperso com três bandas de velocidade e duas trajetórias de vento não uniforme; aceitação visual pendente | ROM SHA `c06e20c46c7eb211f5300ed1919f38192cc9d76425605987d31b22f699f8cc1f`; contrato v004, medição 30 quadros e bundle BlastEm v004 |
| Build | V017 permanece baseline em `out/rom.bin`; V019 opt-in tem bundle próprio; candidato r2 Q16/cache isolado: 524.288 bytes, SHA-256 `0bfcb0e1d896d51fdb273a3d033b3d6f8235939beaeed011df6d076985029caa` | `out/work_runs/splash_v3_convergence_q16_frame_cache_20261015/reports/linux_wine_build_report.json` |
| Emulador | A ROM v004 foi executada no BlastEm. Captura suplementar sem marcador ROM-side, trilha de áudio ou telemetria sustentada; revisão humana pendente | `out/evidence/splash_v3_wind_dispersal_preview_v004_20261015/local_blastem_x11/` |
| Pico r1 | Execução natural mediu 22 células/176 px em F109, em 2/1200 quadros. SAT decodificada na pose congelada: duas entradas além do teto, com só um texel opaco perdido nessa linha; usuário relata quadro perfeito. Tolerância visual WIP, não budget aprovado | `out/evidence/splash_v3_r1_f109_sat_frame_search_20261015/frame_300/`, `out/blastem_splash_v3_h40_r1_natural_20261014/evidence_record.json` |
| Candidato r2 | 13 células/104 px no estado local F109; composição com Q16/cache. Snapshot parcial em 540 externo tem 318 amostras pós-aquecimento, 34 sobre o limiar de CPU e máximo 189; sem claim de 60 fps sustentados | `out/evidence/splash_v3_frame_cache_scene_frame_search_20261015/frame_220/`, `out/evidence/splash_v3_frame_cache_exact_frames_20261015/frame_540/` |
| Scanline | Matriz source-B local: 64x8x8 mede 13/104 em F106; 80x8x8 mede 16/128 em F104 com todos os 80 links; 48x16x16 chega a 19/304. Apenas geometria; gate global bloqueado por espelhos stale | `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json` |
| Auditorias WIP | Contexto, metodologia, higiene e layout passaram; resource validation atual tem 3 erros/20 avisos; freshness alerta artefatos stale, sem obrigatórios ausentes; budget total, áudio e closeout seguem pendentes | `out/logs/freshness_audit_report.json`, `out/logs/validation_report.json`, `out/logs/splash_v3_v017_visual_review_report_20261014.json` |
| Budget total | V019 declara 792 tiles em faixas do loader, 14/20 sprites e 112/320 pixels; VRAM completa, DMA físico, CPU sustentável, DAC e 60fps sustentados seguem pendentes | `out/logs/splash_v3_v019_runtime_tile_ranges_20261015.json`, `out/evidence/splash_v3_v019_preview_20261015/blastem-linux-manual-v019-preview-20261015/runtime_metrics.json` |
| Aprovacao | Visual e audio finais pendentes; FORJA V2 e template intactos | development contract e registros de curadoria |

ROM WIP V017: `out/rom.bin`, SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`; flags `-DSPLASH_V3_VISUAL_PREVIEW -DSPLASH_V3_BACKDROP_V006`. A composicao continua WIP; V017 muda a coreografia de convergencia, nao os PNGs de `/res`.

V019 é somente uma preview de composição do fundo com flags opt-in `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V019`; V006 e V017 seguem como defaults. A telemetria V019 registra máximo 14 sprites/112 pixels por linha (H40), 37/1200 quadros acima do budget de CPU e áudio dummy. Nenhum desses dados aprova a qualidade final nem o orçamento completo.

O candidato r2 Q16/cache é outra ROM WIP, baseada no runtime visual atual e buildada isoladamente. Em uma comparação da pose local F109, mediu 13/20 células e 104/320 pixels. A variante r1 permanece útil como referência de energia visual; seu pico de 22/20 não deve ser vetado esteticamente só pelo contador, mas segue tecnicamente acima do teto. A inspeção SAT exata concluiu que, naquela pose, o excedente perde apenas um texel opaco e uma célula transparente na linha raster observada. Não generalizar esse resultado a outras poses ou linhas.

O snapshot parcial r2 e o alerta de DMA não fecham performance. 5832 bytes é soma de solicitações da fila e 5760 bytes é a maior solicitação individual; comparar os dois como capacidade é uma incompatibilidade semântica do diagnóstico compartilhado. SGDK 2.11 configura capacidade NTSC de 7200 bytes, mas conclusão física de DMA durante VBlank ainda requer medição. Report de budget: `out/reviews/splash_v3_frame_cache_h40_review_20261015/vdp_budget_report.json`.

### Cena 0 - branding_sequence_v3

- Runtime id: `APP_SCENE_BRANDING` / `APP_SCENE_BRANDING` enum 0.
- Papel: assinatura visual/sonora antes do menu. Perfil de preview termina em tela de replay; o candidato separado `SPLASH_V3_MENU_HANDOFF` foi buildado e observado, mas ainda nao tem frame markers, input ROM-side ou gate canonico.
- Formato: NTSC H40, 320x224, 240 quadros; PAL continua futuro arquitetural.
- Fonte de timing/composicao: `doc/branding_v3_cinematic_storyboard.json`.
- Concepcao e curadoria: `doc/branding_v3_scene_conception.md` e `doc/curation/splash_v3_visual_curation_record_20261014.md`.
- Claim ceiling: `technical_demo`, WIP de laboratorio; `ready_for_aaa=false`.

### Planta baixa e recursos visuais WIP

| Recurso | Plano | Posicao/dimensao | Paleta | Tile/cor |
|---|---|---|---|---|
| `img_splash_backdrop_v3_v006` | BG_B | 320x224 | PAL0 | 1120 raw / 583 H-V tiles, 15 cores |
| `img_splash_sgdk_v3` | BG_A | x=48,y=72, 224x48 | PAL1 | 143 raw / 141 H-V tiles, 15 cores |
| `img_splash_forge_v3` | BG_A | x=64,y=128, 192x32 | PAL2 | 92 raw / 91 H-V tiles, 14 cores |
| `spr_splash_particle_v3` | SPRITES | 8 quadros 8x8 | PAL3 | 8 tiles unicos, 9 cores |

O plano selecionado V006/B soma 823 tiles H/V residentes: fundo 583 + SGDK 141 + FORGE 91 + particulas 8 (26.336 bytes, 47,3% de 1.740 tiles de arte). O fundo ainda excede o vocabulario curatorial alvo de 20-40 tiles; reducao so e aceitavel com reautoria que preserve facetas, sem checkerboard. V004/V005 sao comparacoes historicas. Isso mede payload de arte apenas: tiles carregados por codigo, VRAM total, mapas, fontes, SAT e envelope VBlank continuam sem fechamento. Index 0, grid 8x8, cores VDP 9-bit e maximo de 15 cores visiveis por paleta passaram no builder. Report: `out/logs/splash_v3_tile_residency_v006_lettering_b_20261014.json`.

### Timeline implementada

| Beat | Quadros | Runtime |
|---|---:|---|
| `black_silence` | [0,24) | Limpa as duas planes; preload incremental ate 180 tiles por chamada; nenhuma imagem visivel. |
| `energy` | [24,84) | BG_B e PAL0; 64 particulas 8x8 escalonadas; expande ate raio 88 e comeca a contrair. Cue energia F24; musica XGM2 F60. |
| `outline` | [84,120) | Mapa SGDK entra em BG_A; fade de 36 quadros revela primeiro contorno 1-9, mantendo fill 10-15 escuro; particulas convergem para centros de celulas 8x8 visiveis na placa SGDK WIP. Cue lock F118. |
| `fill` | [120,150) | Preenchimento claro do SGDK revela em 18 quadros a partir de F120; contorno se mantem e particulas ficam ocultas. |
| `forge` | [150,180) | Placa FORGE aparece em PAL2 com fade-in de 12 quadros; SGDK fica em PAL1. |
| `sweep` | [180,210) | Seis fagulhas 8x8 com origens, durações e endpoints separados; três bandas horizontais de velocidade (5,83–6,15 / 8,19 / 12,09–14,38 px/quadro); duas trajetórias recebem vento cruzado irregular de amplitude 2px. Curvas Bézier Q8/smoothstep, nascimento/flicker/dissipação e rastros direcionais continuam por instância. Contorno PAL1 índices 1–3 é realçado em F210. Medição v004: 2 sprites/16px por linha, mínimo 23,54px entre centros, nenhum par abaixo de 16px e até 12 links. Cue em F178. |
| `hold_fade` | [210,240) | Cue tail F210; fade apenas de PAL0, preserva o lockup, desenha `A: REVER` e aguarda BUTTON_A no preview isolado. |

Replay chama `APP_changeScene(APP_SCENE_BRANDING)`; o app reseta a SAT com `SPR_reset()` e reinicia a cena. Nao ha handoff ao menu nesta build de laboratorio.

### Medicao de scanline

Self-check do simulador canonico v1.2.0 e do runner local passaram. A matriz percorreu 990 inputs: cinco populacoes (24/32/48/64/80) em 8x8 e 16x16, mais 30 quadros do sweep.

| Perfil | Estado | Pico sprites/linha | Pico pixels/linha | Links | Resultado |
|---|---|---:|---:|---:|---|
| 64 x 8x8 | Selecionado WIP | 13 em F106 | 104 | 64 | Passa geometria local; 65% do limite de contagem H40 |
| 64 x 8x8, permutacao r1 | Tolerancia visual em preview | 22 em F109 | 176 | 64 | ROM natural mediu excedente em 2/1200 quadros; usuario considera o quadro visualmente perfeito; nao passa budget H40 |
| 80 x 8x8 | Stress de densidade | 16 em F104 | 128 | 80 | Passa limites por linha, mas consome todos os links SAT; sem preview visual |
| 6 núcleos + até 6 rastros 8x8 | v003 histórico; usuário reportou aglutinação | 10 em F202-F204 | 80 | máximo 12 visíveis | Medição v002 antiga; não comprova a qualidade pedida |
| 6 núcleos + até 6 rastros 8x8 | v004 candidato de dispersão | 2 em F180-F209 | 16 | máximo 12 visíveis | 30 quadros medidos; distância mínima 23,54px; nenhum par abaixo de 16px; sem violação local H40 |
| 48 x 16x16 | Stress | 19 em F111 | 304 | 48 | Passa por margem minima; warnings de pressao perto do teto |
| 64/80 x 16x16 | Stress | 25/31 | 400/496 | 64/80 | Bloqueado por contagem e largura H40 |

O usuário rejeitou a coreografia anterior (`9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006`) como monótona; o v003 também recebeu feedback de aglutinação e perda de contorno durante o fade. Ambos ficam como histórico de WIP rejeitado. O contrato vigente do beat é `doc/curation/splash_v3_wind_dispersal_contract_v004_20261015.json`. Medição dos 30 quadros F180-F209 em `out/logs/splash_v3_wind_dispersal_scanline_v004_20261015.json`: pico 2 sprites/16 pixels por linha, separação mínima 23,54px e nenhum par abaixo de 16px. Isso valida apenas geometria, não qualidade percebida, runtime integral ou budget global.

Relatorio e inputs: `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json` e `out/logs/choreography_inputs_splash_v3_glyph_anchor_v002_source_b_final_20261014/`. Os 64 anchors sao derivados do recorte B autorizado (`source_lettering_model_sheet_ai_v003_20261014.png`, SHA `d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8`) e reproduzem os centros r2. Esta medicao cobre somente geometria de sprites; a probe da ROM conta a lista SGDK, nao a SAT final. O gate de ferramentas do workspace permanece bloqueado por `project_source_mirror_stale`. Nenhuma ROM, evidencia ou asset foi promovido.

### Budget por eixo

| Eixo | Medido | Pendente |
|---|---|---|
| Tile asset payload | V006/B: 823 tiles H/V / 26.336 bytes; 47,3% de 1.740 tiles de arte disponiveis (payload calculado) | VRAM completa, planos, fonte SGDK, SAT, buffers e residency de runtime |
| Preload | Codigo usa fila e lotes de ate 180 tiles (5.760 bytes por chamada de tile payload) | Total de bytes concorrentes por VBlank, pior quadro e margem em hardware |
| Atualizacao | 64 sprites atualizados por frame ate F120; até 12 links no sweep | CPU real e estabilidade sustentada |
| Scanline | Perfis acima, com self-check | Re-medicao apos model sheet e anchors finais |
| Audio | V016/VGM4 e quatro cues integrados na ROM V017; a revisao nova ainda nao foi ouvida | Dois ciclos de escuta humana, emenda audivel, ownership DAC, quedas e budget final |
| CRAM/paleta | PAL0 fundo, PAL1 SGDK, PAL2 FORGE, PAL3 particulas | Auditoria final de cor/luma e custo de update |
| FPS | Sem medicao sustentada da ROM V017; dados V006 sao historicos e nao fecham este build | Janela sustentada de 60fps com audio e cena pesada |

A chamada duplicada de `SPR_update` foi removida da cena; o loop principal continua owner da atualizacao por frame. A performance sustentada ainda precisa de medicao em ROM com audio.

### Tecnicas registradas no registry

| Registry ID | Aplicacao no WIP | Estado/ponto de curadoria |
|---|---|---|
| `fixed_point_trig_lookup` | LUT inteira de 16 setores para expandir/convergir as particulas | Implementada; scanline medida, custo de CPU ainda pendente. |
| `dma_transfer_safety` | Preload em fila DMA/VBlank, chunks de ate 180 tiles por imagem | Implementada; envelope total por VBlank e pior quadro ainda pendentes. |
| `palette_state_transitions` | Revelacao contorno F84-119, fill F120-137, FORGE e fade | Implementada; legibilidade, luma e custo CRAM precisam de revisao final. |
| `shadow_highlight_slot_rule` | Reserva de slots especiais e declaracao de S/H desligado | Regra aplicada ao plano; sem uso de S/H ou alpha. |
| `palette_remastering_slot_audit` | Papeis PAL0-PAL3 e maximo de 15 cores visiveis | Slots WIP declarados; piso de luma e dead-color audit pendentes. |
| `tile_flipping` | Reuso H/V como opcao de composicao para tiles BG_B | Em avaliacao; nao assumir economia visual ou flags runtime sem report especifico. |
| `tile_dedup_hvflip_hashing` | Medicao de tiles unicos por hash H/V | Audit local V006/B: 823/1.740 tiles selecionados; flags de tilemap e VRAM runtime continuam pendentes. |
| `xgm2_pcm_multiplexing` | Quatro cues PCM junto da candidata BGM V016/VGM4 | Integrados no WIP; escuta, ownership DAC e budget ainda pendentes. |
| `xgm2_audio_architecture` | Ownership XGM2, timeline de cues e handoff de audio | Integrada no WIP; audio.raw foi capturado para V017, mas sem escuta/aprovacao humana. |

Os mesmos nove IDs estao sincronizados em `doc/15-tdd.md`, `doc/10-memory-bank.md` e `doc/changelog/changelog.md`. A presenca no registry nao significa aprovacao nem fechamento de budget.

### Evidencia atual e limite

O report da baseline continua `out/logs/splash_v3_v017_visual_review_report_20261014.json`, ligado a ROM V017 SHA `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`. Alem dela, o handoff V012 (SHA `df699c1aa002b1758921833ae5ec7ae70bd900db7a5cbcd8e2d436307569c852`) e o hold V012 (SHA `e37f5409e19eb1c626e7554875e2ae8fd2006917d451446b7cb03e4ebe916456`) foram observados em BlastEm 1.0.0 isolado. O comando de seal do hold antecedeu o shutdown; o bundle pos-shutdown nao confere e foi rebaixado a preview diagnostico sem selo efetivo. A versao nao fecha o gate canonico 0.6.2; a captura nao traz frame marker e o preflight so confirma bridge+SDL. O audio destas capturas nao foi avaliado. Ainda faltam ciclo frame-marked, input ROM-side, captura canonica da V017, review humana, budget integral e escuta de dois ciclos. Nao declarar `testado_em_emulador`, `validado_budget`, qualidade final ou pronto.

## Ownership

- BG_A/B, CRAM e pool de particulas: `scene_branding_v3` no preview.
- Audio: `branding_v3_audio_director`; XGM2 com cues de energia, lock, sweep e tail.
- DMA/VBlank: a cena agenda `DMA_QUEUE`/`DMA_QUEUE_COPY`; dispatcher global realiza a janela. Envelope real nao medido.
- WINDOW e H-Int: fora de uso.
- Input: sem skip durante 240 quadros; A reinicia somente na espera final.
- A transicao ao menu existe somente no candidato `SPLASH_V3_MENU_HANDOFF`: 240 updates nominais, dreno de fade/DMA e cleanup. Desde 2026-10-16, o mutex so libera depois da entrada do destino, fade inativo e fila DMA vazia; o contador de 12 quadros serve ao HUD e nao libera input. Oito casos funcionais foram observados com input ROM-side em `out/evidence/splash_v3_motion_lut_v002_20261016/native_handoff_01/handoff_observation.json`. Cadencia sustentada, audio aprovado e gate canonico continuam abertos. Perfil `SPLASH_V3_VISUAL_PREVIEW` permanece com replay A: REVER.

### Reconciliacao de coreografia e custo — 2026-10-16

- Selecionada para revisao a variante de geometria fixa `7407e48ee36f0f060c41761cd84aa6f1e0742069abef38f6fcaf462adfaf335f`: oito frames 8x8 com descriptor/timer iguais permitem trocar apenas o tile; guarda e fallback preservam frames mais ricos. Nove cadeias SAT fisicas conferidas por quadro logico; repete 278 VBlanks/241 intervalos (expansao 60/60; sweep 30/30; convergencia 66/36). Sonda completa ativa; 60fps nao aprovados. Matriz e evidencia em `out/reviews/splash_v3_handoff_motion_20261016/cpu_frame_budget_report.json`.

- O contrato offline v004 tinha dois handles Y diferentes do C capturado na ROM. O valor 23,54 px descrevia aquele contrato e foi retirado como medida exata de runtime. O contrato reconciliado e `doc/curation/splash_v3_wind_dispersal_contract_v005_20261016.json`: 154 posicoes ativas conferidas contra as funcoes C; separacao minima real 22,09 px e pico local de 2 sprites/16 px por linha. Nenhum par abaixo de 20 px. Report `out/logs/splash_v3_wind_dispersal_scanline_v005_20261016.json`.
- `SPLASH_V3_MOTION_LUT` e uma candidata opt-in com os mesmos 6.324 pares de coordenadas da referencia C, conferidos nos bytes da ROM; custo de dados 25.296 bytes. Sem mudanca nos PNGs, densidade, trajetorias, ciclo de vida ou frames de sprite.
- Cadencia emulada, mesmo breakpoint e sonda: candidata sem LUT usou 345 VBlanks para 241 intervalos de update; com LUT, 282. Sweep F180-F209 passou de 58 para 30 VBlanks. Isso nao fecha 60 fps sustentados; a convergencia e o custo do observador ainda exigem medicao. Reports em `out/evidence/splash_v3_handoff_readiness_v001_20261016/native_cadence_01/` e `out/evidence/splash_v3_motion_lut_v002_20261016/native_cadence_01/`.

## Gatilhos para futura revisao e promocao

1. Aprovacao humana de rota de lettering, model sheet e fonte autoral.
2. Revisao nativa 320x224 em pelo menos dois ciclos, incluindo sweep e tela final.
3. Reescuta de pelo menos dois ciclos do audio integrado, registrando feedback do usuario.
4. Fechamento de asset provenance, residency/VRAM, DMA/VBlank, CPU, DAC, scanline final e 60fps sustentados.
5. Evidencia BlastEm canonica ligada ao hash final e validacoes limpas.
6. Aprovacao humana especifica para arquivar FORJA V2 e substituir o template; ate la, ambos permanecem inalterados.


## Atualizacao 2026-10-14 — estado corrente de desenvolvimento

- V017 (SHA `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`) continua a ROM baseline em `out/rom.bin`. Uma build isolada com `SPLASH_V3_MENU_HANDOFF` e `SPLASH_V3_BACKDROP_V012` gerou ROM de 393216 bytes, SHA `df699c1aa002b1758921833ae5ec7ae70bd900db7a5cbcd8e2d436307569c852`; BlastEm 1.0 privado mostrou menu, demo e retorno visual. Evidencia `out/evidence/splash_v3_visual_v012_menu_fix_20261014/`.
- A transicao aguarda `PAL_isDoingFade()==false` e `DMA_getQueueSize()==0`, chama `SCENE_brandingV3Exit`, troca para MENU com mutex de 12 quadros, inicia fade-in de paleta e destrava input/update depois do lock. Build/observacao experimental concluida; input ROM-side e frame markers seguem abertos. Contrato `doc/branding_v3_transition_contract.json`; status `preview_observed_experimental`.
- Fundo V006 segue ativo. V007 rejeitado; V008 e V009 foram comparados a 320x224, ambos 438 tiles H/V; V008 e mais limpo mas simetrico; V009 e direcional mas requer safe-area review. Nenhum esta em res. Reports out/logs/splash_v3_backdrop_v008_translation_report_v002_20261014.json e out/logs/splash_v3_backdrop_v009_translation_report_v002_20261014.json.
- Higiene/contexto/metodologia local passaram apos recuperacao hash-bound da arvore; a validacao geral de recursos permanece stale e o budget completo continua aberto.
- Audio permanece sem aprovacao: feedback anterior (abafado/monofonico, baixa qualidade musical, tentativa continua/monotona sem energia) e o pedido de cristalino continuam vinculantes; V016/VGM4 nao foi ouvido em dois ciclos.

## Medicao complementar 2026-10-16 — submitted SAT

Candidata `8aed3920593594b56b9bf4acc62699ff21c9082baeead6e1a13d2642764cd9d7`: observador completo sobre cadeia SAT submetida, 255 VBlanks/241 updates em duas execucoes identicas. Convergencia 36/45, expansao 60/60, sweep 30/30. Quinze cadeias fisicas iguais a versao anterior; doze amostras pos-aquecimento conferem largura e zero invalidas. Corrige contagem de sprites ocultos da sonda anterior; nao infere que dados de estados ativos eram invalidos. Laudo `out/reviews/splash_v3_convergence_cost_20261016/review_summary.json`. Deadline integral, DMA/DAC, gate canonico e qualidade continuam abertos.

## Medicao 2026-10-16 — candidata O

ROM `04f24e1cd52f227c5e01547f2d30b9b915b45fde84a197873687243d5ef35c90`:242/241 intervalos incluindo preto; F24-F239216/216. Convergencia36/36 e fade30/30. Cobertura de todos216 estados visiveis em lotes de boots privados: H40 pico13 sprites e104px, zero excedentes. SRAM pos-aquecimento150 medicoes CPUmax91, zero invalidas. Quatro linhas BG_B por update no preload; logo cache528B; fade source96B. Source do fade inclui contorno17-19, PAL3 omitida somente quando oculta em todos30 estados. `out/reviews/splash_v3_visible_deadline_20261016/resource_loading_model.json` e laudo vinculado. F0/gate canonico/budget integral/qualidade humana continuam abertos.
