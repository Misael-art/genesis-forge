# 15 - Technical Design Document - BRANDING_SPLASH_V3

## Rework da coreografia após rejeição humana — 2026-10-15

- O usuário rejeitou a passagem anterior, ROM SHA-256 `9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006`: apesar de sete trajetórias distintas, o resultado foi percebido como “som contínuo monótono” visualmente e sem a energia combinada. O código alternava os oito quadros por índice global e não tinha nascimento, fase ativa, dissipação, pares núcleo/rastro ou flicker individual. Não reutilizar essa avaliação como evidência positiva.
- Feedback também registra deficiência na direção de cena: o handoff traduziu deslocamento, mas não decompôs o pedido em trajetórias, vida visual por instância, timing, rastro, brilho discreto e critérios de aceitação. A proposta local para aprimorar `cutscene-cinematic-direction` está em `doc/agent_learning/skill_promotion_candidates.md`; nenhuma skill compartilhada foi alterada.
- O rework em `v3UpdateSweep` usa seis curvas Bézier em Q8 com smoothstep, partidas F180-F185, ruído determinístico de até 1px, ausência de termo de gravidade, quatro quadros de nascimento, base luminosa com flicker de 84% em algumas instâncias e redução de cobertura nos quadros finais. Até seis links de rastro acompanham a tangente, com profundidade atrás do núcleo. Tudo reutiliza os quadros previamente carregados.
- A simulação H40 mediu os 30 quadros F180-F209, incluindo as caixas 8x8 de núcleos e rastros: pico local de 10 sprites/80 pixels por linha em F202-F204, máximo de 12 links visíveis no quadro e zero excedentes. Report: `out/logs/splash_v3_wind_lifecycle_scanline_v002_20261015.json`. É geometria do beat isolado, não budget total ou qualidade visual.
- Revisão formal do código: `out/reviews/splash_v3_wind_lifecycle_v003_20261015/code_review_report.json`, decisão `review_passed_with_risk`; sem defeito novo encontrado, com aceitação visual, performance/áudio e budget VDP integral ainda abertos.
- O compiler de contrato agora reconhece `branding_sequence_v3` na especificação e compila uma cena; o lint em modo lab não tem erros ou warnings. O finding `SC090` é informativo: `boot_mode=unsupported` faz verificações determinísticas de boot serem ignoradas nesta configuração de laboratório.
- ROM candidata isolada v003 foi buildada e executada no BlastEm: 524288 bytes, SHA-256 `558fee0aabbee64ea98582a47fd9284866c649f02f2add179b6d0085a9e151ae`; build report `out/logs/splash_v3_wind_lifecycle_build_v003_20261015/linux_wine_build_report.json`. Vídeo direto da janela, 5,53 s: `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/wind_lifecycle_runtime_review_v003.mp4`; contato: `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/runtime_contact_sheet.png`. A passagem fica observável, mas sem marcadores ROM-side; isso confirma execução e movimento, não FPS sustentado, áudio, budget total ou qualidade aprovada. A aprovação humana permanece pendente. Baseline `out/rom.bin` V017 permanece SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`.

## Rodada Q16/cache e reconciliacao do pico H40 — 2026-10-15

- Técnica aplicada sob a seleção existente fixed_point_trig_lookup: tabela Q16 de pesos de convergência para evitar recomputar smoothstep inteiro em cada coordenada e cache dos pontos iniciais das partículas. O owner continua scene_branding_v3; fallback: retornar à interpolação inteira anterior se surgir divergência de coordenadas ou legibilidade.
- v3ScaleQ16TowardZero preserva truncamento em direção a zero; a tabela cobre os passos 0–35. Comparação offline de todos os passos visíveis 1–35 confirmou coordenadas idênticas às da curva anterior nos anchors r1 e r2. O cache de animação só chama SPR_setVRAMTileIndex e SPR_setFrame quando o frame muda; cada criação do pool reinicia os índices para 0xFF. SGDK 2.11 declara SPR_addSpriteEx no header consultado.
- ROM isolada de 524288 bytes, SHA-256 0bfcb0e1d896d51fdb273a3d033b3d6f8235939beaeed011df6d076985029caa; build report out/work_runs/splash_v3_convergence_q16_frame_cache_20261015/reports/linux_wine_build_report.json. Em F109 local, a probe observa 13/20 sprites e 104/320 pixels. Screenshot, VRAM, CRAM e VSRAM são idênticos ao build Q16 de comparação naquele estado.
- A análise SAT r1 foi separada entre solicitação da lista SGDK e saída observada. Natural r1 registrou 22/20 em 2/1200 quadros e 176/320 px. O build diagnóstico com hold congelou a pose F109 para inspeção; SAT em 0xF400 mostrou 22 células cruzando a linha 99, mas o limite retém só vinte. As duas últimas contribuem um texel opaco ausente e uma célula transparente; o usuário considera a pose perfeita. Isso permite tolerância visual WIP, sem exceção ao limite de hardware.
- Evidência de performance r2 é só snapshot suplementar parcial, sem áudio: 318 amostras após warm-up, 34 sobre o limiar de CPU, pico 189. Não prova desempenho sustentado. DMA/VBlank, 60 fps com áudio, ciclo frame-marked completo e captura canônica permanecem pendentes. Revisões: `out/reviews/splash_v3_frame_cache_h40_review_20261015/code_review_report.json` e `out/reviews/splash_v3_frame_cache_h40_review_20261015/vdp_budget_report.json`.

## Rodada V018 — fundo de facetas amplas em preview experimental

- V018 foi adicionado como recurso opt-in (`SPLASH_V3_BACKDROP_V018`) e não substitui V006 como default nem V017 em `out/rom.bin`. O build usa `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V018`; ROM isolada de 524288 bytes, SHA-256 `a94700a7a79b5fb6ffb074402909e2f7c2f0ddc89a790b05ac143e89edfeb493`.
- Captura direta no BlastEm Flatpak 1.0.0 foi selada para o hash exato. VLAB/MDRT registrou 1200/1200 frames, H40 máximo 14 sprites/112 pixels, zero quadros excedentes, 37/1200 quadros acima do budget de CPU e carga máxima 396. A sessão usou SDL dummy; não prova áudio audível ou desempenho sustentado.
- O desenho usa 901 tiles H/V únicos no fundo e estima 1141/1740 tiles para backdrop + lockup + partículas. Este total é offline; VLAB não registrou ranges de VRAM e `res_graph_report.json` está stale. Ocupação total de VRAM, uploads VBlank/DMA, CPU e budget DAC permanecem sem validação.
- `validate_resources.ps1` reportou 3 erros e 19 avisos no projeto. Os erros incluem `code_loaded_tiles_unmeasured` e reconciliação de claims canônicos que ainda aponta para ROM/reportes anteriores. O preview V018 não foi promovido aos caminhos canônicos de evidência.
- Revisão do código desta mudança: `out/reviews/splash_v3_v018_visual_preview_20261015/code_review_report.json`; escopo isolado, sem defeito de API observado. Decisão `review_passed_with_risk` porque os limites de entrega acima permanecem abertos.
- Estado visual: WIP placeholder; revisar em 320x224/CRT, safe area, bordas, partículas, sweep e leitura do prompt. V017 permanece controle com faixa horizontal rejeitada. Sem aprovação humana, promoção do template ou arquivamento da FORJA V2.

## Rodada V014 — preview visual diagnostico

- Build isolado SGDK 2.11: 393216 bytes, ROM SHA-256 `cd3946fcd7de61709b590f77fec16f0066e3e30b3fe283fd5dad0f20a72cba5c`; flags `SPLASH_V3_VISUAL_PREVIEW` + `SPLASH_V3_BACKDROP_V014`. Build report e run em `out/logs/splash_v3_v014_headless_retry_20261014/linux_wine_build_report.json` e `out/work_runs/splash_v3_v014_headless_retry_20261014/run.json`.
- O hold final foi observado em BlastEm native 1.0.0 por captura diagnostica privada no frame 700; SGDK/FORGE e `A: REVER` aparecem legiveis. Ainda nao houve ciclo completo frame-marked, selo canonico, avaliacao CRT, escuta musical ou medicao de FPS sustentado.
- A auditoria ativa de tiles mede 1096/1740 (63%) para V014 + lockup/particulas WIP; warning de baixa deduplicacao da V014. Proveniencia: 24 simbolos visuais, sem findings. Reports em `out/logs/splash_v3_v014_headless_retry_20261014/`.
- Esta rodada nao substitui a baseline V017/V006 nem fecha runtime, VRAM, VBlank/DMA ou promocao. Status permanece `em_desenvolvimento`.

## 1. Contexto tecnico

- classe: technical_demo de uma splash de marca Mega Drive
- teto de claim: technical_demo
- plataforma: Mega Drive, SGDK 2.11
- cena ativa: APP_SCENE_BRANDING, id 0
- timing inicial: NTSC, 240 quadros; PAL permanece futuro arquitetural
- fonte de verdade: doc/13-spec-cenas.md e doc/branding_v3_cinematic_storyboard.json
- baseline do projeto: runtime visual WIP V017 buildado e observado em amostras diagnosticas diretas do BlastEm local 1.0.0; V014 tambem foi buildada em ROM isolada e capturada num hold diagnostico no frame 700. Ambas as rotas permanecem sem selo canonico; revisao humana, input ROM-side, audio, budgets e desempenho sustentado seguem pendentes

## 2. Arquitetura e ownership

- fluxo do preview: boot -> APP_SCENE_BRANDING V3 -> prompt de replay; sem handoff ao menu
- FSM: sete estados de duracao fixa, 240 quadros NTSC; BUTTON_A reinicia somente depois do fade final
- owner da FSM: scene_branding_v3
- owner de CRAM: branding_v3_palette_controller
- owner de BG_A/B: scene_branding_v3
- owner de sprites: scene_branding_v3_particle_pool; o sweep reutiliza seis núcleos e até seis links de rastro no mesmo owner
- owner de VBlank e DMA: dispatcher global da aplicacao; a cena apenas agenda transferencias
- H-Int e WINDOW: explicitamente fora de uso
- input: sem skip durante a sequencia; BUTTON_A reentra na mesma cena apos o prompt
- teardown do preview: parar audio, limpar BG_A para o prompt; APP_changeScene faz SPR_reset antes da reentrada
- transicao formal: doc/branding_v3_transition_contract.json, status needs_review

## 3. Memoria e VDP

- arrays estaticos: 64 ponteiros de Sprite e LUT inteira de 16 setores; sem heap
- SPR_initEx(16) recebe reserva de tiles de VRAM, nao limite de instancias. O
  SGDK 2.11 cria spritesPool com MAX_SPRITE=80; confirmar depois a reserva de
  tiles separadamente para os assets v3
- geometria WIP selecionada: 64 particulas 8x8; anchors amostrados da mascara SGDK medem 13 sprites/104 pixels na pior linha (F106), 64 links totais. Isso cobre scanline local, nao VDP total nem gate global.
- sweep histórico rejeitado: sete instâncias 8x8 e pico local antigo de 4 sprites/32 pixels não provaram qualidade. Sweep WIP v003 tem seis núcleos e até seis rastros; mede pico de 10 sprites/80 pixels por linha em F202-F204 (`out/logs/splash_v3_wind_lifecycle_scanline_v002_20261015.json`).
- um SPRITE do ResComp tem largura e altura por quadro constantes; nao misturar
  8x8 e 16x16 numa mesma definicao. Alternativas futuras: um sprite 16x16 com
  margem transparente ou duas definicoes que compartilhem tiles por contrato manual
- sem float, malloc/free, pixels desenhados por codigo ou API SGDK presumida
- limites H40 simultaneos: 20 links e 320 pixels por scanline; limite SAT: 80 links
- scanline: geometria local de 990 entradas passou no perfil escolhido; 80x8x8 e perfis de 16x16 a partir de 48 estouram H40
- Tiles WIP V006/B: 823 residentes H/V (26.336 bytes), de teto de payload de arte 1.740 (47,3%; margem 52,7%): fundo 583, SGDK 141, FORGE 91 e particulas 8. O fundo poupa 161 tiles contra V005; o controle de 40 tiles segue rejeitado por checkerboard e 20-40 tiles permanece alvo de curadoria sujeito a fidelidade. Isso nao fecha VRAM total, tiles code-loaded, mapas/fontes, SAT ou envelope completo de VBlank. Report: `out/logs/splash_v3_tile_residency_v006_lettering_b_20261014.json`.
- nenhum teto total de VRAM, DMA, CPU, DAC ou FPS foi fechado
- a matriz mede geometry e nao substitui ancora final, budget ou leitura visual
- sem flicker como fallback

## 4. Tecnicas selecionadas e aplicacao

IDs, tags, owners e fallback continuam em doc/tdd_contract.json e
doc/technique_usage_manifest.json. O estado e WIP implementado; budgets completos
e claims de entrega permanecem pendentes.

- fixed_point_trig_lookup: LUT inteira de 16 setores implementada; scanline medida, custo CPU pendente; fallback para direcoes precomputadas.
- dma_transfer_safety: protege preload e atualizacao de recursos; envelope e
  worst-frame fit pendentes; fallback e adiar carga, nunca transferir fora de VBlank.
- palette_state_transitions: fade-in do contorno azul SGDK (F84-119), preenchimento claro (F120-137), entrada de FORGE e fade de preview implementados; a ROM de laboratorio leva PAL0 a uma paleta fria de repouso e preserva PAL1/PAL2. O build sem preview ainda usa fade global; ownership unico, custo e legibilidade final continuam pendentes.
- shadow_highlight_slot_rule e palette_remastering_slot_audit: reservar e
  auditar papeis de slots; nao usar S/H nem vender como alpha.
- tile_flipping e tile_dedup_hvflip_hashing: testar reuse H/V de tiles no fundo;
  economia so sera declarada depois do report.
- xgm2_pcm_multiplexing e xgm2_audio_architecture: V016/VGM4 e quatro cues estao integrados no preview V017. Uma previa isolada de duas passagens foi buildada e executada em BlastEm; a captura direta do ROM `35af30bb5b0cfe52fb527858b9cd164ed496ee46f144e2396fd151841fb16e71` registrou 358/358 quadros com XGM2 ativo e zero quedas. Stereo/mono WAV para escuta estao em `out/audio/reviews/v009_v016_two_cycle_rom_capture_20261015/`. A rota ficou sem selo canonico e a ROM nao e `out/rom.bin`; aprovacao auditiva humana, budget DAC e performance sustentada permanecem pendentes.

Tecnicas adiadas: sprite_temporal_multiplexing e sprite_band_slot_allocator,
pois nao ha plano de exceder limites legais nem reservar slots por sobrecarga;
reconsiderar somente se a medicao mostrar necessidade. H-Int e contextual scene
transition system estao adiados porque a direcao nao usa raster/H-Int. A tecnica
source_baked_pixel_art_standard aguarda a decisao humana sobre o master.

## 5. Audio

> Os detalhes seguintes descrevem V015 como baseline musical; V016/VGM4 e a candidata corrente, registrada na Rodada V017.

- Driver e ownership: XGM2; card ativo em doc/branding_v3_audio_architecture_card.json.
- Composicao candidata V015: C maior, motivo C5-G5-E5-F5 | D5-G5-B5-C6, 120 BPM, 6/8, duas barras de 90 quadros (180 quadros / 3 s). Gates curtos, releases FM rapidos, stabs de baixo/harmonia e pings aditivos E6/G6/C7; notas acabam antes do sweep.
- Brilho: tres pings FM aditivos curtos; PSG musical fica em silencio. A camada ainda requer escuta humana na cena integrada.
- Entrada no quadro de cena 60, apos o rise de 24-59; mark lock 118, sweep 178, acorde final 195, tail 210, teardown 240. WAVs PCM usam CH2/CH3 com ate dois simultaneos.
- Historico: V012 recebeu retorno positivo; V013 e V014 foram rejeitadas pelo usuario por soarem continuas e monotonas, sem a energia combinada. V015 foi aceita para desenvolvimento. O bundle da ROM V006/B inclui audio.raw, mas nenhuma escuta subjetiva foi registrada; o WAV fisico anterior continua ligado apenas a V005.
- Relatorios: doc/branding_v3_frequency_masking_plan.json, doc/branding_v3_audio_event_matrix.json e doc/branding_v3_composition_scope_contract.json.
- Historico V005: 262144 bytes, SHA-256 `d4d7e5c842d31e88652d7e06856d9eeb3b4b182bb918c11f5aa20eefe6532319`, sem os wordmarks B. Estado atual V006/B: ROM 393216 bytes, SHA-256 `22c6e3962c253b2588cd07d0b9d4fa2d890d4366b8e4de71a87b59e1b755baf4`, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V006`; build report `out/logs/linux_wine_build_report.json`.
- Capturas selecionadas do preview V005 anterior a B foram vistas em BlastEm local 1.0.0: `out/blastem_splash_v3_visual_preview_20261014_v005/`; report `out/logs/splash_v3_visual_audio_review_report_20261014_v005.json` permanece `preview_observed_unsealed`. Ha energia, reveal e lockup luminoso; cycle2_mid/late mostra preto do fade. Nao e evidencia da arte B, nem ha ciclo completo frame-accurate ou prompt/replay rastreados para esse hash.
- V012 continua a referencia sonora positiva; V013/V014 foram rejeitadas por continuidade monotona; V015 e somente integracao WIP. Um WAV de 10,24 s foi capturado por monitor fisico e ligado ao hash V005; sinal presente nao substitui escuta humana, avaliacao de timbre ou julgamento da emenda do loop.
- Audio de producao, budget DAC/performance e promocao ao template continuam pendentes.

## 6. Riscos e mitigacoes

| Risco | Impacto | Mitigacao | Evidencia |
|---|---|---|---|
| Espelhos globais de runtime_probe desatualizados | Instrumentos nao autorizados para medir | Corrigir somente pela curadoria do workspace; manter o laboratorio sem medidas | measurement gate report |
| SpriteDefinition exige dimensao fixa | Proposta de frames 8x8/16x16 nao cabe numa definicao | Comparar perfis separados; fechar uma definicao depois da prova | ResComp local e contrato de asset futuro |
| Placa tipografica sem master aprovado | Pixels atuais sao placeholders derivados de referencia AI | Manter source gate em needs_review; exigir model sheet e fonte autoral | `doc/contracts/visual_source_of_truth_branding_splash_v3.json` |
| Contorno confundido com preenchimento | Marca ilegivel ou contraste fraco | Travar indices por papel e testar piso de luma depois da arte | auditorias visuais futuras |
| Pico de scanline excedido | Flicker ou sprites omitidos | 64x8x8 passa com 13/104; 80x8x8 passa com 16/128 mas usa os 80 links; 48x16x16 chega a 19/304; 64x16x16 e 80x16x16 excedem | `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json` |
| PCM compete com BGM ou DMA | Audio cortado ou desempenho instavel | Ownership e fallback antes de compor/integrar | reports de audio e BlastEm futuros |
| Estado anterior deixa callback ou fila ativos | Falha na reentrada ou menu | Contrato simetrico de transicao e reset | teste de reentrada em BlastEm |

## 7. Validacao e status

> Os bullets abaixo registram a validacao historica V006/B. O estado corrente esta na Rodada V017 ao final deste documento.

- measurement tools gate: bloqueado por 20 espelhos ativos fora do laboratorio
- gate global de ferramentas: bloqueado (7/30 self-checks passaram na varredura global, com falha de espaco temporario e espelhos ativos desatualizados); self-checks individuais relevantes de residency e provenance passaram com TMPDIR=/tmp
- storyboard, TDD e transicao: sincronizados com runtime WIP; transicao final para menu ainda nao existe neste preview
- Assets: V006 e fundo WIP; B esta ativa em `/res` e observada na ROM de laboratorio, mas sem selecao humana. Fundo 1120 raw/585 sem flips/583 H/V; SGDK 168 raw/141 H/V; FORGE 96/91; particula 8. Pico do plano 823 tiles (26.336 bytes, 47,3%). V004/V005 permanecem comparacao; reautoria do vocabulario segue aberta.
- BlastEm: bundle selado para V006/B, cena 0, screenshot semantico aprovado e 1200/1200 quadros de medicao. O snapshot de titulo e 57.7 FPS e nao prova estabilidade; VLAB registra 37/1200 acima do budget, CPU max 459, 64 sprites e pico de 17/linha. Sustained 60fps, replay trace, ciclo frame-accurate, VRAM/DMA/CPU/DAC completos e julgamento humano seguem pendentes. Prompt `A: REVER` usa `font_default`, PAL3 indice 15, coluna 16/linha 21.
- duplicidade de `SPR_update` removida da cena; o loop principal mantem a chamada unica. Medicao de performance sustentada ainda pendente
- `validate_resources.ps1` atualizado: 3 erros/20 avisos em 21 verificacoes; `technical_incomplete`, `technical_ready=false`. Erros: ownership da arvore aninhada, tiles carregados por codigo sem budget e `claim_sources_missing`; closeout segue bloqueado.
- Proveniencia passou para 21/21 simbolos; residency self-check passou e reporta 984 tiles nos sete estados; o aviso remanescente referencia o recurso V004 de comparacao. A validacao geral reportada e anterior a B e continua incompleta.
- nenhuma alegacao de pronta, validada em budget, qualidade visual/sonora final ou `testado_em_emulador`

Mudancas posteriores atualizam este arquivo, doc/13-spec-cenas.md,
doc/10-memory-bank.md, doc/changelog/changelog.md e o manifesto de tecnicas.

## Rodada V006/B — estado atual do preview

> Registro historico da rodada V006/B. O estado corrente e a Rodada V017 abaixo.

- Registro do usuario: manter `em_desenvolvimento` e exigir revisao futura para aprimoramento; aprovacao final visual/sonora, model sheet, template e arquivamento FORJA V2 permanecem falsos.
- Build SGDK 2.11: 393216 bytes, SHA-256 `22c6e3962c253b2588cd07d0b9d4fa2d890d4366b8e4de71a87b59e1b755baf4`, flags `SPLASH_V3_VISUAL_PREVIEW -DSPLASH_V3_BACKDROP_V006`.
- Evidencia BlastEm: `blastem-linux-20261014T133648Z-289753`, screenshot SHA-256 `a5a189903c49e7f6e58a32c5e89365870650669207c8e9da5c99bef5f18a2b5a`, semantic gate `passed`, freshness `ok`, scene 0 e 1200/1200 quadros. O VDP dump e bloco VLAB de 204 bytes, nao VRAM integral.
- VLAB: 37/1200 over-budget frames, CPU max 459, max sprites/scanline 17; `window_fps_snapshot=57.7` e performance sustained permanecem unproven.
- Replay BUTTON_A, ciclo visual frame-marked completo, feedback auditivo humano sobre os dois passes, qualidade visual humana, budget total e promocao seguem abertos.

## Rodada V017 — ancora visual para convergencia das particulas

- Alteracao WIP de runtime: os alvos das 64 particulas 8x8 foram alinhados a centros de celulas visiveis da placa SGDK atual. O contrato deriva anchors do PNG WIP com pelo menos 24 pixels opacos por celula; os anchors precisam ser refeitos quando a arte mudar e nao equivalem a model sheet aprovado.
- Fonte de mascara da geracao inicial r2: placa WIP em `/res`, SHA-256 `f43440eb16fd5f3560fda61a9ce8109674113d5cf07439d432627e59400b4be9`. A linhagem foi corrigida: a mascara agora e recriada em memoria do recorte B da folha autorizada (`source_lettering_model_sheet_ai_v003_20261014.png`, SHA `d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8`, crop `[401,362,1276,518]`), sem ler `/res`. Os 64 anchors v002 sao identicos aos r2 anteriores; contrato e matriz em `out/logs/choreography_inputs_splash_v3_glyph_anchor_v002_source_b_final_20261014/`.
- A atribuicao r1 mediu 21 sprites/linha em F108 e 22 em F109, com 176 pixels/linha, abaixo do limite horizontal. A ROM natural confirmou 22 em 2/1200 quadros. O usuario relata que F109 pareceu perfeito; essa opiniao permite tolerancia visual do efeito, nao aprovacao de budget. A probe percorre a lista SGDK de sprites visiveis e calcula caixas por scanline; nao prova quais objetos entraram na SAT nem quais pixels o VDP mostrou acima do teto. O limite H40 continua 20 sprites/linha. Relatorio de reconciliacao `out/logs/splash_v3_h40_peak_review_20261014.json`.
- A ordenacao r2 por Y/X passa localmente em 13 sprites/104 pixels, pior quadro 106, com 64 links. O stress 80x8x8 mede 16 sprites/128 pixels em F104 e usa 80 links; e apenas candidato WIP. A matriz de 990 entradas esta em `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json`; gate compartilhado segue bloqueado por espelhos stale.
- ROM V017: 393216 bytes, SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V006`.
- BlastEm local 1.0.0: 16 amostras diagnosticas do contato visual mostram energia, revelacao SGDK, entrada FORGE, sweep e lockup. Hold final mostra `A: REVER`; amostras sao por relogio de parede, sem quadro exato, trace independente de input ou selo canonico. Report `out/logs/splash_v3_v017_visual_review_report_20261014.json`.
- Audio atual da ROM: V016/VGM4, score `data/source_audio/splash_v3_sonic_logo_score_v4.json`, VGM `res/music/splash_v3_sonic_logo_v4.vgm`; centro C maior, 6/8 a 120 BPM, 180 quadros, motivo/articulacao revisados e paneamento stereo separado. A ROM isolada do preview completou duas passagens e gerou WAV direto para escuta; nenhuma aprovacao humana foi registrada e a qualidade musical permanece aberta.
- Pendencias para curadoria: leitura nativa/CRT e safe area; lettering/model sheet por glifo; piso numerico de contraste/luma; transicoes de paleta e legibilidade dos counters; centro negativo, facetas/cristais e flare contra FORGE; vocabulario de tiles sem checkerboard; anchors e sobreposicao; sweep/timing; prompt/replay com input ROM-side; captura frame-marked canonica; revisao auditiva humana dos dois passes; VRAM, tiles code-loaded, DMA/VBlank, CPU, DAC e 60fps sustentados.
- Sem aprovacao final visual/sonora, model sheet, ROM de producao, template ou FORJA V2; `ready_for_aaa=false`.

## Preview visual WIP V015/V016 — 2026-10-15

- Macros `SPLASH_V3_BACKDROP_V015` e `SPLASH_V3_BACKDROP_V016` permitem comparação opt-in; builds sem essas flags preservam V006. V016 deriva da fonte conceitual V015 e usa uma máscara oval feathered; mede 652 tiles H/V únicos contra 708 em V015. É tradução WIP, sem reautoria manual aprovada. Report e board: `out/logs/splash_v3_backdrop_v016_translation_report_20261015.json` e `out/logs/splash_v3_backdrop_v016_comparison_wip_v001_20261015.png`.
- Preview V016 isolado: ROM SHA `64d333bf4ec246bbf67c4d947ebae25f33fa5e7eed99e942c9c174d57f98a532`, 393216 bytes; screenshot SHA `a6b31554cf2e9d723f657efbd1aa5ec86d76516d39b3731f972a2e7f9fb13596`. Captura ligada ao hash exato e a 1200 quadros, selada na rota experimental BlastEm 1.0.0. Medições: 14 sprites/linha, 112/320 px, 37/1200 quadros de CPU acima do budget, pico 396; snapshot de título 61,1 fps não prova 60 fps sustentados. Áudio foi dummy.
- V006 segue default; não houve mudança da ROM de produção V017, aprovação visual/sonora, promoção do template ou arquivamento da FORJA V2. Revisão humana de composição nativa/CRT, lettering, safe area, densidade de borda e leitura do campo central continua obrigatória.
- F109 r1: aceitação visual do quadro sem defeito aparente pode permitir essa composição continuar como WIP; não flexibiliza o limite H40 de 20. O probe mede células SGDK cruzando a linha por Y, sem decodificar a SAT final. As 22 entradas observadas em 2/1200 quadros e 176/320 px são sobre-limite medido, não budget aprovado; r2 (13/20) permanece default.


## Delta de runtime 2026-10-14 — handoff candidato

- Perfil SPLASH_V3_MENU_HANDOFF isolado por macro; builds sem a macro preservam a base anterior. rom_head.c identifica este perfil como Splash V3 DEV PREVIEW.
- No frame nominal 240, a cena espera o fade assincrono e a fila DMA esvaziar; nao chama flush manual. SCENE_brandingV3Exit para audio, restaura scroll, Shadow/Highlight, WINDOW e plano de texto. O app manager limpa SAT/sprites e troca a cena.
- O manager bloqueia input, update e transicoes aninhadas por 12 quadros; SCENE_menuEnter desenha o menu herdado, captura as 64 cores via CRAM e executa PAL_fadeInAll por 12 quadros. So depois o menu volta a receber input.
- APIs SGDK 2.11 conferidas em pal.h, pal.c e dma.h: PAL_getColors(u16,u16*,u16), PAL_fadeInAll(const u16*,u16,bool), PAL_isDoingFade(void), DMA_getQueueSize(void). Uma variante de handoff com V012 foi buildada e observada na sessao experimental abaixo; frame markers, input ROM-side e gate canonico continuam pendentes.
- Contratos: doc/branding_v3_transition_contract.json, doc/branding_v3_scene_reset_plan.json, doc/branding_v3_resource_loading_model.json, doc/branding_v3_cutscene_runtime_contract.json, doc/branding_v3_runtime_decision_log.json; revisao estatica out/logs/sgdk_code_review_splash_v3_handoff_20261014.json.
- Tecnica registrada: padrao fade_transition (catalogo runtime) usando palette_state_transitions e dma_transfer_safety; owner application_scene_manager; orcamento visual 12 quadros de fade-in; fallback hard cut ainda nao implementado.

## Revisao visual diagnostica V012 — 2026-10-14

- O menu herdado duplicava cada texto por desenhar uma segunda copia em coordenadas `(x+1,y+1)`. Como `VDP_drawText` usa tiles, isso deslocava oito pixels, nao um. `menuDrawText` agora faz somente uma chamada PAL3 por rotulo; a captura de handoff confirma a linha unica.
- ROM de hold separada: V012, SGDK 2.11, 393216 bytes, SHA-256 `e37f5409e19eb1c626e7554875e2ae8fd2006917d451446b7cb03e4ebe916456`. Screenshot de 640x448 pixels no lockup final mostra SGDK/FORGE legiveis e `A: REVER`; captura anterior com baixo contraste nao tinha frame marker e nao prova falha de paleta. `PAL_initFade` copia a faixa de cores pela contagem; o ponteiro `palette[10]` corresponde a seis indices para CRAM 26-31.
- Evidencia ligada ao hash em `out/evidence/splash_v3_visual_v012_lockup_hold_retry_20261014/`; BlastEm Flatpak 1.0.0, preflight bridge+SDL e fechamento gracioso. O comando de seal antecedeu o shutdown; hashes dos logs mudaram e arquivos transitorios faltaram no pacote, entao o registro foi corrigido para preview sem selo efetivo. A ROM nao tem frame marker, titulo FPS e instantaneo e audio foi dummy. Isso e preview de laboratorio, nao `testado_em_emulador` canonico, budget aprovado ou criterio de release.
- Revisao formal do helper de texto: `out/logs/sgdk_code_review_report_splash_v3_menu_text_fix_20261014.json`, decisao `review_passed_with_risk`; nao aprova a entrega do projeto.
- A ROM baseline V017 e `out/rom.bin` permanecem inalteradas. Arte/lettering placeholder, audio, model sheet, CRT/overscan, sequencia frame-marked, input ROM-side, budgets VDP/DMA/CPU/DAC e revisao humana continuam pendentes.
