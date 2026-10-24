# Changelog Canonico - BRANDING_SPLASH_V3 [VER.001] [SGDK 211] [GEN] [LAB] [ART_TRANSLATION]

## 2026-10-24 - pausa solicitada e checkpoint de branding

- Registrada `BRANDING-001` em `doc/pending/branding_v3_resume_20261024.md`:
  confusoes entre laboratorio/template/V2, baseline/candidatas, medicao/aceite,
  instrumentos divergentes e aprovacao musical pendente. Roteiro de retomada
  inclui todas as rejeicoes e limites sem transformar tentativa em sucesso.
- Preservadas fontes atuais Q/R, assets, fontes autorais, ferramentas locais e
  historico util. README do laboratorio deixa de se apresentar como template.
  Espelhos temporarios, executaveis host e evidencias locais ficam fora do Git.
- Checkpoint JSON identifica baseline, O, Q e R e inventaria fontes/evidencias.
  Nenhuma alteracao C, build, execucao de ROM ou teste de implementacao nesta
  rodada; resultados de 2026-10-16 continuam historicos do respectivo hash.
- PR de rascunho isola este laboratorio dos outros trabalhos do workspace.
  Visual/sonoro nao aprovados; V2 sem arquivo, template sem promocao.

## 2026-10-16 — prontidao do menu e reducao do custo de coreografia

- Fechamento desta rodada: contexto `technical_demo/implementation`, metodologia e higiene passaram; proveniencia 28/28, zero blockers/avisos; self-checks selecionados do simulador e coletor nativo 2/2 passaram. Learning Capture/Audit registrou 6 licoes locais e nenhuma promocao canonica. Freshness do projeto permanece `warning`: 7 reports stale, 0 obrigatorios ausentes e 0 erros; o laudo geral continua aberto, sem green de entrega. Mapa de claims/evidencias e sete eixos WIP em `out/logs/evidence_closeout_report.json`.

- Candidata tecnica selecionada nesta rodada: `out/profiling/splash_v3_stable_geometry_v005_20261016/rom.bin`, SHA `7407e48ee36f0f060c41761cd84aa6f1e0742069abef38f6fcaf462adfaf335f`, 524288 bytes. Guarda runtime confirmou que os oito frames compartilham geometria 8x8 estacionaria, um tile e timer zero; o caminho comum SGDK continua como fallback. Nove cadeias SAT fisicas sao identicas byte a byte a candidata sem esta especializacao. Cadencia repetida duas vezes: 278 VBlanks/241 intervalos; expansao 60/60 e sweep 30/30. Convergencia permanece 66/36, impedindo claim de 60 fps sustentados.
- O cache de visibilidade posterior manteve os mesmos 278 VBlanks/histogramas e foi rejeitado. Fonte da cena restaurada e conferida contra o SHA do input do build selecionado. Diagnostico sem tick da sonda usou 258 VBlanks, mas nao e candidato de entrega nem evidencia de budget aprovado. Detalhes e matriz em `out/reviews/splash_v3_handoff_motion_20261016/cpu_frame_budget_report.json`.
- A candidata selecionada passou pelos oito casos de handoff e teve AV capturado no Flatpak isolado: `out/evidence/splash_v3_stable_geometry_v005_20261016/flatpak_sessions/sess-20261016T175910-58afe69b/`. Video 14 s, audio em disco 37,76 s e SRAM no shutdown gracioso. Escuta humana e sincronismo AV continuam abertos.

- O mutex de transicao agora consulta entrada do destino, fade e fila DMA; o contador visual de 12 quadros nao libera mais input. A captura de RAM confirmou contador zero com fade ativo, seguido de desbloqueio real. Oito casos passaram: bloqueio, B recebido durante fade sem sair do menu, desbloqueio, B posterior reiniciando a splash, retorno ao menu e START entrando na demo. Candidata inicial SHA `80521392fe7736dd867195e68aa184b6934075dde6d8a6f21153fac6764885ae`; evidencia `out/evidence/splash_v3_handoff_readiness_v001_20261016/native_cycle_02/handoff_observation.json`.
- Captura Flatpak isolada dessa candidata registrou menu/splash/menu/demo, video de 14 s e audio em disco de 37,184 s, com SRAM salvo no shutdown. Perfil de captura usa renderer SDL e nearest; o primeiro ensaio OpenGL ficou preso em dialogos Zenity e foi preservado como falha de captura. Evidencia positiva `out/evidence/splash_v3_handoff_readiness_v001_20261016/flatpak_sessions/sess-20261016T172035-299904fe/`. Video/audio possuem inicios distintos e nao fecham sincronismo ou escuta humana.
- `SPLASH_V3_MOTION_LUT` usa 25.296 bytes de coordenadas geradas pelas funcoes C originais. Os 6.324 pares foram conferidos diretamente nos bytes da ROM `4096089a3c868ac8342ccfa8029769e30266af1e496d5391e2818ef269031396`. Nenhum PNG, densidade ou ponto da trajetoria foi alterado. As funcoes de referencia continuam como fallback.
- Mesmo observador externo no APP_update: 241 intervalos usaram 345 VBlanks antes e 282 com LUT; sweep F180-F209 passou de 58 para 30 VBlanks. A candidata LUT tambem passou nos oito casos de handoff. Convergencia e eventos ainda perdem deadlines; isso nao comprova 60 fps sustentados.
- Tentativa de trocar a sonda de linhas marcadas por varredura linear: 512 casos x 2 repeticoes passaram contra oracle independente, mas a ROM `4da8a33c2155a2d6dc64c930e531febc15169cae1ea7775db34ca9198fcd62df` manteve os mesmos 282 VBlanks e histogramas. Hipotese rejeitada; `runtime_probe.c` foi restaurado byte a byte. Evidencias e criterio de reabertura em `out/logs/splash_v3_linear_probe_rejection_20261016.json`.
- Reconciliacao do contrato: dois handles Y do v004 offline divergiam do C capturado. A medida 23,54 px foi retirada como exata de runtime. V005 confere 154 posicoes ativas contra a referencia C e mede 22,09 px, zero pares abaixo de 20 px, pico local 2 sprites/16 pixels por linha. A coreografia C permaneceu identica. Contrato e report em `doc/curation/splash_v3_wind_dispersal_contract_v005_20261016.json` e `out/logs/splash_v3_wind_dispersal_scanline_v005_20261016.json`.
- Estado continua em desenvolvimento. Menu ainda depende de arte/BGM V2; promocao exige resolver essa dependencia, gates tecnicos completos e revisao humana visual/sonora. Baseline `out/rom.bin`, template e FORJA V2 permanecem preservados.

## 2026-10-15 — dispersão do sweep e contorno no fade

- O usuário relatou que o sweep v003 ainda ficava aglutinado e que o contorno do SGDK perdia definição quando o azul escurecia. A deficiência de direção agora inclui falta de critério de dispersão e de contraste pós-fade; registrada em `doc/curation/splash_v3_scene_direction_feedback_20261015.md` e no ledger local, sem editar skills compartilhados.
- O código v004 separa seis trajetórias em três bandas de velocidade horizontal: lenta (5,83 e 6,15 px/quadro), média (8,19) e rápida (12,09, 12,64 e 14,38); `spark_2` e `spark_4` recebem desvios de vento de amplitude 2 px com fases e cadências diferentes. As origens, durações, alturas e endpoints são individuais.
- No início do fade, F210, PAL1 índices 1–3 recebem três azuis mais claros para manter a leitura do contorno no campo escuro. Os PNGs e a proveniência dos assets não mudaram.
- Medição local de F180–F209: separação mínima de 23,54 px em F192 (`spark_2`/`spark_3`), zero pares abaixo de 16/20 px, pico de 2 sprites/16 pixels por scanline e máximo de 12 links. Isto mede somente a geometria dos seis núcleos e rastros; não fecha o budget total.
- Build isolado v004: 524288 bytes, SHA-256 `c06e20c46c7eb211f5300ed1919f38192cc9d76425605987d31b22f699f8cc1f`; report `out/logs/splash_v3_wind_dispersal_build_v004_20261015/linux_wine_build_report.json`. BlastEm capturou 8 s em `out/evidence/splash_v3_wind_dispersal_preview_v004_20261015/local_blastem_x11/`; captura suplementar, sem marcadores ROM-side ou faixa de áudio, e a aceitação humana continua pendente.
- A rota padrão de captura tentou resolver a versão fixada e recebeu HTTP 404; usei o BlastEm Flatpak 1.0 já instalado e ROM com nome único para isolar o SRAM. Uma execução inicial pelo binário Linux com `rom.bin` tocou o SRAM genérico em `/home/misael/.local/share/blastem/rom/save.sram`; não havia hash anterior para comparar. As execuções seguintes usaram caminhos por ROM e salvaram a cópia de SRAM no bundle v004.
- A baseline `out/rom.bin` continua SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`. Splash V3 permanece em desenvolvimento; sem promoção do template, arquivamento FORJA V2 ou aprovação final.

## 2026-10-15 — ciclo de vida das fagulhas e revisão de direção de cena

- O usuário rejeitou a passagem anterior de sete trajetórias como monótona e sem a energia/animação combinadas. A nota anterior de “promissor” foi retirada; contrato, medição e ROM antiga permanecem apenas como histórico de falha. A deficiência do handoff do skill de direção de cena ficou registrada em `doc/curation/splash_v3_scene_direction_feedback_20261015.md` e como candidata local em `doc/agent_learning/skill_promotion_candidates.md`.
- Rework implementado: seis núcleos 8x8 com início assíncrono, curvas Bézier Q8/smoothstep, ruído discreto até 1px, sem termo de gravidade, nascimento de quatro quadros, fase brilhante, flicker individual em parte das instâncias, até seis rastros orientados e redução discreta de cobertura ao dissipar. Contrato: `doc/curation/splash_v3_wind_lifecycle_motion_contract_v002_20261015.json`.
- A medição dos 30 quadros F180-F209 registra até 12 links visíveis, pico de 10 sprites/80 pixels por linha em F202-F204 e zero violações H40. É geometria local, não budget global nem aprovação estética.
- ROM isolada v003: 524288 bytes, SHA-256 `558fee0aabbee64ea98582a47fd9284866c649f02f2add179b6d0085a9e151ae`; build report em `out/logs/splash_v3_wind_lifecycle_build_v003_20261015/linux_wine_build_report.json`. Vídeo direto da janela BlastEm, 5,53 s, e contato visual em `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/`.
- Revisão SGDK 2.11 registrada em `out/reviews/splash_v3_wind_lifecycle_v003_20261015/code_review_report.json`: `review_passed_with_risk`, sem defeito novo no escopo; revisão humana, performance/áudio e budget total continuam abertos.
- O heading da cena foi alinhado ao parser do contrato; `scene_contract_compiler` agora extrai uma cena e o lint lab reporta zero erros/warnings. `SC090` permanece informativo porque o `boot_mode` de laboratório é `unsupported`.
- A validação geral foi atualizada: 3 erros e 20 avisos; os erros são code-loaded tiles sem evidência de VDP integral, reports que não correspondem à ROM baseline e conflito no status agregado. Contexto/metodologia/higiene passaram. O candidato visual segue WIP, sem claim de budget ou entrega. Report: `out/logs/validation_report.json`.
- A captura mostra a cena e a passagem em execução, mas não contém marcadores de frame ROM-side e não prova FPS sustentado, áudio aprovado, budget VDP total ou qualidade visual aceita. Splash V3 segue em desenvolvimento; sem promoção ao template e sem arquivamento da FORJA V2. A ROM baseline `out/rom.bin` permanece V017 (`5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`).

## 2026-10-15 — primeira passagem do sweep com sete trajetórias — rejeitada

- Substituida a passagem em escada horizontal por sete trajetorias inteiras Q8 com posicoes e velocidades variadas, lancamentos escalonados, aceleracao horizontal leve, arcos verticais e ondulacao. O cue F178, a janela F180-F209 e o asset existente foram preservados.
- Medicao H40 dos 30 quadros: maximo 4 sprites/32 pixels por scanline. Contrato e report em `doc/curation/splash_v3_wind_sweep_motion_contract_20261015.json` e `out/logs/splash_v3_wind_sweep_scanline_20261015.json`.
- ROM de preview opt-in V019: 524288 bytes, SHA-256 `9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006`; capturas BlastEm suplementares em `out/evidence/splash_v3_wind_sweep_20261015/`, alinhadas pela cena lida na RAM. Review: `out/logs/splash_v3_wind_sweep_runtime_review_20261015.json`.
- Esta passagem foi rejeitada pelo usuário como monótona e sem a animação/energia combinadas. Sua ROM e medição ficam como histórico de falha; não contam como direção aprovada. A revisão e o rework estão registrados na entrada imediatamente acima.
- Revisao local `sgdk-code-reviewer`: passou sem findings de codigo, com riscos registrados para o validation report stale e a evidencia suplementar. Contexto de implementacao, metodologia e higiene passaram; `tools/measure_splash_v3_wind_sweep.py` esta declarado como ferramenta deste projeto.
- `freshness_audit.ps1` permanece em warning com cinco reports canonicos stale (`scene_contract_compile`, `res_graph`, `emulator_session`, `audio_validation`, `build_output`), zero ausentes obrigatorios e zero erros. O learning capture/audit guardou uma nota local e uma candidata de workflow; nenhuma skill compartilhada foi alterada.

## 2026-10-15 — revisão SAT F109 e otimização Q16/cache

- Captura diagnóstica SAT do estado r1 congelado em F109: 22 células cruzam a linha raster 99. As entradas 61 e 63 estão depois do teto H40; uma produz somente um texel opaco nessa linha e outra é transparente. O texel excedente não aparece no screenshot. O caso fica tolerado para comparação visual WIP, mas 22/20 continua fora do budget.
- Build r2 com tabela de convergência Q16 e cache de quadro de partículas: ROM isolada de 524288 bytes, SHA-256 0bfcb0e1d896d51fdb273a3d033b3d6f8235939beaeed011df6d076985029caa. Em F109 local, a probe observa 13 sprites e 104 pixels. out/rom.bin V017 e seu SHA não mudaram.
- Auditoria offline das posições Q16 nos passos 1–35 preservou as coordenadas inteiras da versão anterior; a captura comparativa F109 manteve screenshot, VRAM, CRAM e VSRAM idênticos ao build Q16 anterior. Build e capturas auxiliares: out/work_runs/splash_v3_convergence_q16_frame_cache_20261015/ e out/evidence/splash_v3_frame_cache_scene_frame_search_20261015/.
- Snapshot nativo parcial no frame externo 540: 318 amostras pós-aquecimento, 34 sobre o limiar de CPU, máximo 189; áudio dummy e amostra parcial não aprovam 60 fps sustentados. A rota é suplementar, não gate de entrega.
- Corrigido no registro de curadoria o falso alerta de excedente DMA: fila total 5832 bytes não pode ser comparada com 5760 bytes da maior operação como se fossem capacidade; SGDK 2.11 configura 7200 bytes para NTSC. Conclusão de DMA físico/VBlank continua pendente.
- Estado: em desenvolvimento, sem aprovação visual/sonora final, promoção do template ou arquivamento da FORJA V2.

## 2026-10-15 — V019 preview visual hash-bound

- Traduzido e integrado como variante opt-in o fundo cristalino V019: 320x224, 15 cores visíveis, 552 tiles H/V; provenance placeholder e qualidade `needs_review`. V006 segue default.
- Build isolado 524288 bytes, ROM SHA `6731a055ce88cbb2b122cfd2e03f1690ef8a430b890670477ef2438549d2019b`; `out/rom.bin` V017 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2` permaneceu inalterada. Capture exata selada e freshness ok em `out/evidence/splash_v3_v019_preview_20261015/blastem-linux-manual-v019-preview-20261015/evidence_manifest.json` pela rota experimental BlastEm 1.0.0/X11; helper canônico segue bloqueado por HTTP 404.
- Screenshot nativa mostra o lockup legível, facetas laterais e ignição inferior sem linha de chão contínua. `A: REVER` é prompt exclusivo do modo visual preview. Não há aprovação humana.
- Captura diagnóstica de movimento: 17 stills host-timed ligados ao mesmo SHA da ROM em `out/evidence/splash_v3_v019_motion_samples_long_20261015/motion_samples_manifest.json`, com contato `out/evidence/splash_v3_v019_motion_samples_long_20261015/motion_contact_sheet.png`. A sequência sugere partículas, contorno, preenchimento/FORGE e hold, mas os primeiros stills incluem startup e a cadência aproximada de ~0,5 s não permite localizar o sweep por frame nem afirmar ciclo completo. O GIF derivado foi rejeitado por corrupção de paleta e não é evidência utilizável.
- Telemetria V019: 14/20 sprites, 112/320 pixels, nenhum excedente H40 em 1200 quadros; 37/1200 quadros acima do budget CPU, pico 398 e 60.9 FPS instantâneos. 792 tiles em faixas declaradas; VDP completo/DMA físico não medidos. Áudio dummy, não ouvido.
- O r1 F109 22/20 continua exceção de tolerância visual WIP, sem mudar o teto H40. Sem promoção, arquivamento da FORJA V2, aprovação de áudio ou mudança da ROM baseline.
- A validação atual de recursos reporta 3 erros/19 avisos; os erros são o footprint de tiles carregados por C ainda não medido e a reconciliação entre relatórios ligados a ROMs diferentes, sem blocker específico da variante V019. Metodologia e higiene passaram.
- Curadoria e reports: `doc/curation/splash_v3_visual_curation_record_20261014.md`, `out/reviews/splash_v3_v019_visual_review_20261015/visual_quality_review.json`, `out/reviews/splash_v3_v019_visual_review_20261015/vdp_budget_report.json`, `out/reviews/splash_v3_v019_visual_review_20261015/code_review_report.json`, `out/logs/splash_v3_v019_runtime_telemetry_20261015/capture_route_override.json`.
## 2026-10-15 — V018 telemetria corrigida e decisao do pico H40

- ROM WIP isolada `d46bd88a26019625844ab8c1732d9c76187df5c247ff27aaf6a2877998ee2d9f` confirma contadores de particulas: 64 alocadas, 0 falhas. Na variante r2, maximo de 14/20 sprites e 112/320 pixels por linha em 1200 quadros.
- O pico r1 de 22 sprites em F109 (2/1200, 176 px) continua como excecao visual tolerada pelo usuario para comparacao WIP. H40 ainda tem teto fisico de 20; o contador superior nao sera chamado conforme ao budget. O gate visual nao deve descartar automaticamente o pico raro, mas o budget segue `over_limit_not_approved`.
- CPU: 37/1200 quadros sobre budget; maximo 398; snapshot 59,1 FPS sem prova de sustentacao. Fila DMA solicitada max 5832 bytes/29 entradas antes do VBlank; ranges de tiles sao declaracoes do loader, sem readback completo nem confirmacao de conclusao DMA.
- Captura exata selada pelo BlastEm instalado 1.0.0/X11 manual, em rota experimental; helper canonico falhou ao atualizar Flatpak pinned com HTTP 404. Relatorios em `out/reviews/splash_v3_v018_runtime_telemetry_20261015/`; decisao de budget `cabe_com_recuo`, status global ainda nao validado.
- Visual permanece `needs_review`; audio ainda sem escuta/aprovacao humana. Sem promocao do template nem arquivamento FORJA V2.

## 2026-10-15 — V018 de fundo cristalino executada em ROM WIP

- V017 foi preservada como controle negativo: a faixa clara horizontal continuava atravessando o fundo e a tradução ocupava 1104 tiles H/V únicos. V018 troca essa linha por facetas amplas, clusters assimétricos e uma prateleira inferior quebrada; a tradução mede 901 tiles H/V únicos de 1120 e 3,07% da máscara WIP do lettering acima do limiar diagnóstico de luma 32.
- A imagem V018 foi compilada somente com `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V018`. ROM isolada: 524288 bytes, SHA-256 `a94700a7a79b5fb6ffb074402909e2f7c2f0ddc89a790b05ac143e89edfeb493`; build e inputs em `out/work_runs/splash_v3_v018_visual_preview_retry_20261015/`. A tentativa anterior com argumentos incorretos de `PAL_fade` foi preservada separadamente em `out/work_runs/splash_v3_v018_visual_preview_20261015/`.
- BlastEm Flatpak 1.0.0 executou a cópia de ROM isolada; bundle da sessão `blastem-linux-20261015T040001Z-v018` foi selado para o mesmo SHA, screenshot semanticamente válido e janela de telemetria 1200/1200. O screenshot mostra SGDK/FORGE e o prompt legíveis; V018 segue placeholder WIP, sem aprovação humana.
- Runtime desta ROM usa r2: 14/20 sprites e 112/320 pixels na scanline máxima, sem quadros acima dos limites H40 medidos pela probe. Houve 37/1200 quadros acima do budget de CPU, pico 396; áudio foi dummy e FPS sustentado não foi validado. O pico r1 de 22/20 em F109 é outra variante e continua tolerado visualmente apenas para comparação WIP, sem aprovação do budget.
- O mapa estático da ROM compilada agora fecha os intervalos de tile: V018 901, SGDK 141, FORGE 91 e partículas 8 = 1141/1408 tiles seguros, com 267 livres antes da reserva automática de sprites. Relatório hash-bound: `out/logs/splash_v3_v018_vram_static_allocation_20261015.json`. A sonda ainda não exporta os intervalos em runtime, o dump é apenas o bloco VLAB de 204 bytes e DMA/VBlank não foram medidos.
- A validação geral de recursos terminou com 3 erros e 19 avisos: `res_graph` continua sem medição dos tiles carregados por C/VDP em runtime e há relatórios canônicos antigos ligados à ROM baseline. A captura V018 não foi publicada como evidência canônica de entrega.
- Freshness terminou em warning: 5 relatórios stale (`scene_contract_compile`, `res_graph`, `emulator_session`, `audio_validation`, `build_output`), 0 itens obrigatórios ausentes e 0 erros. Layout do workspace passou; aprendizado não encontrou lições qualificadas.
- V006 permanece default em `out/rom.bin` V017 (`5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`). Nenhuma aprovação, troca de template ou arquivamento da FORJA V2.

## 2026-10-15 — preview visual WIP V016 e esclarecimento do budget H40

- Registrado o preview ROM opt-in V016, com vinheta oval feathered derivada da fonte conceitual V015. A candidata mantém o campo central escuro, suaviza sua borda e mede 652 tiles H/V únicos; a diferença média frente a V015 é sutil. V006 permanece o fundo default; V015/V016 continuam sem seleção ou aprovação.
- ROM V016 isolada: SHA-256 `64d333bf4ec246bbf67c4d947ebae25f33fa5e7eed99e942c9c174d57f98a532`; captura selada do mesmo hash em BlastEm 1.0.0 experimental, 1200/1200 quadros. Máximo observado: 14 sprites/linha, 112/320 px; 37/1200 quadros acima do budget de CPU, pico 396 e 61,1 fps instantâneos. Áudio dummy e performance sustentada não validados.
- Curation record, TDD e memory bank registram que reprovar automaticamente o r1 apenas pelo aspecto visual do F109 seria conservador demais, mas 22/20 continua excedente técnico; a captura não prova emissão das 22 células pela SAT/VDP. Manter r2 default e permitir r1 apenas como comparação WIP/tolerância visual.
- Nenhuma aprovação, promoção do template, alteração da ROM padrão ou arquivamento da FORJA V2.

## 2026-10-15 — conceito visual WIP V015 registrado

- Criado o conceito de fundo V015 para explorar moldura cristalina mais assimétrica, com cluster alto à esquerda, topo direito simplificado e massa direita mais baixa. O reflexo inferior diminuiu, mas ainda precisa de ajuste. SHA-256 `87293cf5275564733d27d5a166f1071f04bb2b447257a07c5a3f0c6b9c0c9188`.
- Registrada a referência copiada e seu hash, o prompt, o sidecar de geração, o workset, o contrato de direção V015 e o índice de arte. Estado: candidata de conceito e fonte elegível para tradução; nenhuma aprovação humana ou promoção para `/res`.
- Próxima etapa visual: parsing semântico e safe area, controle `basic`, reautoria manual `elite` no grid 8x8, revisão de paleta/tiles e comparação nativa 320x224/ROM. O conceito high-res não foi usado em runtime; V006 e ROM V017 não mudaram.
- O estado permanece em desenvolvimento. Não houve aprovação de arte ou áudio, troca do template ou arquivamento da FORJA V2; a tolerância a 22/20 sprites em F109 permanece visual e não altera o limite H40.

## 2026-10-15 — captura direta de escuta V016 em duas passagens

- Adicionado ao preview apenas o harness de duas passagens para ouvir V016/VGM4 com cues; ROM isolada de 393216 bytes, SHA-256 `35af30bb5b0cfe52fb527858b9cd164ed496ee46f144e2396fd151841fb16e71`. Captura BlastEm mostra `MUSIC 358/358 DROP:0`; WAV stereo e fold-down mono de 8 s estao disponiveis em `out/audio/reviews/v009_v016_two_cycle_rom_capture_20261015/`.
- Atualizados memory bank, TDD, desenho de audio, briefing do curador e contrato de desenvolvimento com hashes e limites da evidencia. A escuta ainda precisa do julgamento do usuario; nenhuma qualidade musical, budget DAC ou performance sustentada foi aprovada.
- O recapture da versao que move a etiqueta `TWO PASSES DONE` para a area visivel falhou no dialogo GTK/Zenity. A ROM v2 compilou, mas sem screenshot/audio/SRAM validos; a tentativa esta registrada separadamente e nao invalida o WAV anterior. `out/rom.bin` V017, template e FORJA V2 nao foram alterados.
- O pico r1 22/20 em F109 permanece visualmente tolerado como WIP apos observacao do usuario, enquanto o limite H40 continua sendo 20 entradas por linha e r2 (13/20) segue como default.
- Fechamento operacional: `workflow_layout.py` passou; `audit_project_learning.ps1 -Mode Capture` reportou `no_qualified_lessons`; freshness ficou em warning com 5 stale, 0 missing required e 0 erros. Os reports estao em `out/logs/` e o run direto inclui seus hashes.

## 2026-10-14 — V016/VGM4: material de escuta em duas passagens

- Preparada uma prévia WAV de 6 s em stereo e um fold-down mono para avaliar a chamada-resposta, os espaços, o brilho cristalino e a emenda da candidata V016/VGM4.
- A fonte é o trecho de áudio já capturado na ROM V012; VGM, cues e `audio.c` têm os mesmos hashes da V017. O artifact repete duas vezes um ciclo capturado de 3 s; não é captura direta de duas cenas na ROM atual.
- Nenhuma composição, patch ou asset runtime foi alterado. Não houve normalização, ganho ou EQ adicional. Aprovação humana, captura frame-marked na ROM atual, orçamento DAC e performance seguem pendentes.
- Stereo: `out/audio/reviews/v008_v016_two_cycle_20261014/splash_v3_v016_two_cycle_stereo.wav`; mono: `out/audio/reviews/v008_v016_two_cycle_20261014/splash_v3_v016_two_cycle_mono_fold.wav`; hashes e proveniência no manifesto ao lado. Run: `out/work_runs/splash_v3_v016_two_cycle_audio_review_20261014/run.json`.


## 2026-10-14 — preview isolado V014 observado

- A tentativa inicial de ResComp bloqueou na inicializacao Java2D/X11 sem display. O wrapper `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh` agora gera makefiles com `-Djava.awt.headless=true`; a retry compilou a candidata em saida isolada.
- ROM V014: 393216 bytes, SHA-256 `cd3946fcd7de61709b590f77fec16f0066e3e30b3fe283fd5dad0f20a72cba5c`, flags `SPLASH_V3_VISUAL_PREVIEW` + `SPLASH_V3_BACKDROP_V014`. V017 em `out/rom.bin` (SHA `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`) permaneceu inalterada.
- BlastEm native 1.0.0, Xvfb/bwrap privado, captura diagnostica no frame 700: hold final com SGDK, FORGE e `A: REVER` legiveis. Still 640x480, audio dummy, sem ciclo frame-marked ou selo canonico; nao e aprovacao visual/sonora nem claim de performance. Screenshot `out/evidence/splash_v3_v014_headless_retry_20261014/native_diag_f700/window.png`, SHA `6bf7b5815b9ae2807a40b963e773042879aca9ce9c9a3f8031e3e450ffcf6613`.
- Residency ativa medida em 1096/1740 tiles (63%, 37% de margem): V014 856 + SGDK 141 + FORGE 91 + particulas 8. A auditoria alerta baixa deduplicacao da V014 (23,6%); provenance passou para 24 simbolos sem findings. Esses reports medem assets, nao VRAM runtime completa.
- Status `em_desenvolvimento`; V014 segue nao selecionada, score 0.6847 `needs_review`, bordas/CRT aguardam revisao. Sem alteracoes no template, na FORJA V2 ou em projetos consumidores. Curadoria atualizada; nenhuma promocao realizada.


## 2026-10-14 — novo estudo WIP de fundo V013/V014

- Registrada a fonte AI V013 em data/source_art/branding_v3/sources/ e sua copia externa em rascunho/entrada_visual/, com hashes, prompt e linhagem. A composicao nativa mostrou cristais atras do lockup e custo alto de tiles; V013 passou a controle de comparacao.
- A edicao V014 amplia a area escura real do lockup sem alterar a baseline. O painel rascunho/visual_lab/splash_v3_backdrop_v014_comparison_wip_v002_20261014.png apresenta source/basic/curated, V006 atual e V013.
- V014 usa 15 cores visiveis/4bpp, 870 tiles exatos e 856 com flips H/V; contra V006, o aumento estimado no estado e de 823 para 1096/1740 tiles. Nota estetica 0.6847 (needs_review), reutilizacao de tiles 0.2357 e ruido 0.1832.
- A traducao V014 esta em res/ apenas como placeholder de preview opt-in; o build candidato usa diretorio separado e V017 permanece intacta. Isso nao e aprovacao visual nem promocao de produto. Template/FORJA V2 nao foram tocados.
- Gate de direcao atualizado para a cena Splash V3 e bloqueia producao/ROM final. V013/V014, workset, fonte de verdade, proveniencia, memoria e curation record foram sincronizados.


## 2026-10-14 — menu corrigido e lockup V012 observado em hold

- Corrigido o texto duplicado do menu em `src/scenes/scene_menu.c`: coordenadas de `VDP_drawText` sao tiles; o deslocamento `+1,+1` desenhava uma segunda copia 8 px abaixo/direita. O helper agora desenha uma unica linha. A candidata de handoff tem ROM separada, 393216 bytes, SHA `df699c1aa002b1758921833ae5ec7ae70bd900db7a5cbcd8e2d436307569c852`; a captura mostra opcoes limpas. A, MODE e B produziram as transicoes visuais esperadas, sem prova de input ROM-side.
- Capturada a composicao final em build V012 isolada, 393216 bytes, SHA `e37f5409e19eb1c626e7554875e2ae8fd2006917d451446b7cb03e4ebe916456`, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V012`. SGDK, FORGE e o prompt estao legiveis no hold. Os samples escuros anteriores nao tinham frame marker e foram feitos em tempos intermediarios; revisao de `PAL_initFade` nao encontrou desalinhamento de cores, entao nenhuma paleta foi alterada.
- BlastEm Flatpak 1.0.0, Xvfb isolado; preflight bridge+SDL aprovado e sessao fechada graciosamente. A tentativa de seal ocorreu antes do encerramento; os logs mudaram e arquivos transitorios faltam no pacote pos-shutdown, portanto o recibo foi rebaixado a diagnostico sem selo efetivo. Evidencia local: `out/evidence/splash_v3_visual_v012_lockup_hold_retry_20261014/`. A versao 1.0 nao fecha o gate canonico pinned 0.6.2; sem frame markers, desempenho sustentado ou escuta de audio.
- Pico r1: a ROM natural mediu 22 celulas SGDK cruzando a linha em 2/1200 quadros, com 176/320 px. A sonda nao filtra X; no F109 todas as trajetorias permanecem dentro da area horizontal, entao o pico nao e inflado por sprites fora da tela. O usuario observou F109 sem defeito visual aparente: manter como tolerancia visual WIP, sem converter em budget aprovado; H40 continua limitado a 20 sprites por linha.
- Revisao formal do helper `menuDrawText`: `out/logs/sgdk_code_review_report_splash_v3_menu_text_fix_20261014.json`; decisao `review_passed_with_risk`, sem findings de codigo e com riscos de closeout registrados.
- V012 continua candidata WIP; V017 em `out/rom.bin` nao mudou. Sem aprovacao final, arquivamento FORJA V2 ou promocao do template.

## 2026-10-14 — trecho de audição V016 e proveniência reconciliada

- Criado corte de revisão integrado V016/VGM4 com 3,2 s em WAV stereo 48 kHz/16-bit e MP3 de conveniencia. O WAV deriva de uma captura BlastEm do preview visual V012 (ROM SHA `234f73abc68e94d9175fe2b4714bb5cd7d531904113f150bcd9c49751ff55eb7`), entre 1,0 e 4,2 s; filtro passa-altas de 20 Hz para remover DC, sem normalizacao. Sidecar registra proveniencia e hashes.
- O snapshot V012 e V017 usam o mesmo VGM4, cues PCM e `audio.c` por hash, mas o WAV nao e captura do binario V017. Nao prova aprovacao humana, dois ciclos/loop, budget DAC ou desempenho sustentado.
- Corrigido `doc/sfx_bank_manifest.json`: `mus_splash_v3` agora corresponde ao `.res`, VGM4, hash SHA-256 `fc9bacd1888d50634077c655c45068fbf07ee2e279a4a4bdcf85fda6f77af7d3`, `asset_version=4`; status continua `lab` aguardando escuta humana.
- `validate_audio.ps1` passou: 12 recursos, zero issues, estimativa 59,11 KB (1,44% do limite de 4 MB). Auditoria de proveniencia com `--verify-hashes` passou apos reconciliacao: 12 entradas, zero erros e zero avisos; relatorio em `out/logs/audio_provenance_v016_report_20261014.json`.

## 2026-10-14 — linhagem B e margem de scanline medidas

- O builder dos anchors agora cria a mascara em memoria a partir do recorte B autorizado da folha de modelo (`source_lettering_model_sheet_ai_v003_20261014.png`, SHA `d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8`) e nao le `/res`. A validacao de linhagem passou sem findings; os 64 anchors gerados continuam exatamente iguais aos anchors r2 atuais.
- Matriz source-B refeita e medida: 990 entradas. O perfil 64x8x8 passa com pico 13 sprites/104 px no F106; o candidato 80x8x8 passa com 16/128 no F104, mas ocupa os 80 links SAT. 48x16x16 chega a 19/304; 64x16x16 e 80x16x16 excedem os limites H40.
- Relatorio `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json`; o self-check local passou. O gate global permanece bloqueado por `project_source_mirror_stale`, portanto isso nao fecha budget global ou aprovacao visual.
- O usuario considera o pico r1 de 22 em F109 visualmente perfeito. A evidencia natural vinculada a ROM confirma 22 em apenas 2/1200 quadros, mas a probe mede demanda SGDK, nao a SAT final: o teto H40 de 20 continua, e o excedente nao foi promovido a budget aprovado. r2 permanece default.
- Auditorias locais posteriores: contexto, metodologia e higiene passaram sem blockers. Freshness rerun apos sincronizacao: status `warning`, 5 reports tecnicos stale (contrato de cena, grafo de recursos, emulador, audio e build), zero artefatos requeridos ausentes e zero erros; ver `out/logs/freshness_audit_report.json`.

## 2026-10-14 — sequencia natural r1 confirma pico de F109

- Build isolado sem o hold: 393216 bytes, SHA-256 `559b9c1d22f6738748ceee3cddd7eeb66872c0ae1a586eaa6efbb3e140bafbca`; anchors r1, fundo V006. V017 em `out/rom.bin` permaneceu inalterada.
- BlastEm Flatpak 1.0.0, sessao experimental `sess-20261014T181325-2928442c`; preflight bridge+SDL passou. Captura final mostra o lockup e `A: REVER`.
- MDRT/VLAB: janela completa 1200/1200; pico 22 sprites/scanline no frame global 110 (F109 local), soma de largura 176/320 px, 2/1200 quadros acima do limite de contagem e 0 acima do limite de largura. O hold anterior gerava 1182/1200 amostras por repetir F109; sem hold, a telemetria confirma que o excedente ocorre raramente.
- Curadoria: a geometria nao superestimou o pico. Tratar o pico como reprovação visual automática é conservador demais para esta direção, conforme a captura e a observacao do usuario; o limite físico H40 continua 20 e o status segue excedente observado, budget nao aprovado. O VDP pode omitir as duas celulas acima do teto.
- CPU max 399 e 37 quadros acima do threshold; 60.2 fps no titulo e apenas uma amostra. Performance sustentada, input/replay ROM-side, audio, aprovação visual e selo de entrega continuam pendentes.
- Relatorios e captura: `out/blastem_splash_v3_h40_r1_natural_20261014/` e `out/logs/splash_v3_h40_r1_natural_20261014/linux_wine_build_report.json`.

## 2026-10-14 — ROM r1 F109 capturada e medida no BlastEm

- Build isolado da r1 com hold diagnostico em F109: 393216 bytes, SHA-256 `b8b27ca7317d092a00e5236cbe6b558e2089877f7f88825797c4c915854c6abd`. A baseline `out/rom.bin` V017 nao foi alterada.
- BlastEm Flatpak 1.0.0, Xvfb privado, sessao experimental `sess-20261014T180248-e85c2771`. Screenshot do estado F109 e SRAM foram copiados para `out/blastem_splash_v3_h40_r1_f109_20261014/`.
- MDRT/VLAB da mesma sessao e ROM: pico 22 sprites/scanline em H40 no frame global 110 (estado local F109), soma de largura 176/320 px; 1182/1200 amostras acima do limite de contagem, causadas principalmente pela macro que mantem F109 congelado. A candidata natural, buildada e medida depois, registrou 2/1200 quadros acima do limite.
- Curadoria: a simulacao r1 nao esta conservadora quanto a contagem; a ROM mediu 22. A imagem pode ser toleravel, conforme observacao do usuario, mas o limite fisico de 20 sprites/scanline continua excedido e o budget nao esta aprovado. A captura nao prova que os dois sprites excedentes aparecem.
- Rota experimental nao selada como evidencia de entrega. Runtime, audio, input/replay, FPS sustentado e aprovacao final continuam pendentes.
- Relatorios: `out/blastem_splash_v3_h40_r1_f109_20261014/evidence_record.json`, `out/blastem_splash_v3_h40_r1_f109_20261014/runtime_metrics.json` e `out/logs/splash_v3_h40_r1_f109_20261014/linux_wine_build_report.json`.

## 2026-10-14 — preview V012 medido em BlastEm

- ROM isolada V012: 393216 bytes, SHA-256 `234f73abc68e94d9175fe2b4714bb5cd7d531904113f150bcd9c49751ff55eb7`; V017 em `out/rom.bin` nao foi substituida.
- BlastEm 1.0.0 em sessao Xvfb experimental. Bundle mesmo-session `sealed`, freshness `ok`, gate semantico da screenshot `passed`; evidencia em `out/blastem_splash_v3_visual_v012_preview_20261014/isolated_session/sess-20261014T173801-224faca3/`.
- Probe runtime do hash exato completou 1200 quadros: pico 14 sprites/linha e 112/320 pixels; zero quadros acima dos limites H40. A V012 usa anchors r2; nao valida o pico 22 da geometria r1. Reprovar automaticamente overflow decorativo e conservador demais no eixo visual, mas o limite fisico permanece 20 sprites/320 pixels.
- Max CPU 396, 37 quadros acima do budget e `performance_claim=unproven`; 60.0/59.8/58.0 fps sao amostras de janela, nao FPS sustentados. Tentativas A tiveram ack bridge/SDL sem mudanca visual; replay ROM-side pendente.
- WAV stereo de 12 s passou somente integridade de sinal (ativo, sem clipping); a aprovacao musical continua com o usuario. Preview visual e sonoro permanece WIP e exige revisao futura.
- Relatorio: `out/logs/splash_v3_v012_preview_capture_20261014.json`.

## 2026-10-14 — V010–V012: fundo de cristal com safe area medida

- V010/V011/V012 foram gerados a partir da direcao facetada e traduzidos para 320x224/15 cores. V010 ainda deixa 7,27% da mascara WIP clara; V011 deixa 1,13%, concentrado no S. V012 reduz para zero os pixels de luma >32 sob as mascaras atuais e mede 272 tiles H/V.
- Criado `audit_splash_v3_backdrop_safe_area.py`; self-check 5/5. A ordenacao automatica agora escolhe V012 como menor contaminacao medida sob a mascara WIP do lettering; continua sem selecao/aprovacao humana. Relatorio comparativo: `out/logs/splash_v3_backdrop_safe_area_20261014.json`. Workset atualizado para V012 e validado: 7 fontes elegiveis, 6 referencias.
- Todas as variantes ficam em `rascunho/visual_lab`; V006 permanece o asset de `/res` e a ultima ROM. V012 e comparativo WIP, sem selecao humana, build ou promocao.

## 2026-10-14 — Reconciliacao do pico de 22 sprites H40

- Registrado feedback do usuario: a observacao visual do pico de 22 sprites/linha em F109 pareceu funcionar perfeitamente. A medicao r1 e geometrica, sem ROM hash; seu pico e 176/320 px e todas as particulas estao dentro da area X visivel. A captura rastreavel V017 usa r2 (13 sprites/linha), nao valida r1.
- Reconciliacao: reprovar 22 como falha visual automatica seria conservador demais para este efeito decorativo. A ROM r1 agora liga o pico ao hash exato e a SRAM reporta 22 sprites/linha, com 176/320 px. Portanto o pico nao e conservador na contagem, embora a captura continue sem marcador desenhado e em rota experimental. O teto H40 permanece 20 sprites/linha e 320 pixels independentes; funcionamento aparente nao prova que os 22 foram renderizados. O hold diagnostico explica a maior parte das 1182/1200 amostras acima do teto e precisa ser separado da passagem natural da cena. Relatorios: `out/logs/splash_v3_h40_peak_review_20261014.json` e `out/blastem_splash_v3_h40_r1_f109_20261014/runtime_metrics.json`.

## 2026-10-14T15:23:22Z - V017: convergencia visual nos glifos SGDK WIP

- Task: splash_v3_glyph_anchored_visual_development
- Skills: sgdk-runtime-coder, cutscene-cinematic-direction, megadrive-vdp-budget-analyst, emulator-vdp-evidence-curator
- A coreografia de convergencia agora usa 64 anchors derivados de celulas 8x8 visiveis no SGDK WIP (SHA `f43440eb16fd5f3560fda61a9ce8109674113d5cf07439d432627e59400b4be9`), no lugar da grade uniforme. Builder, contrato de anchors e 990 entradas de medida local foram atualizados.
- A primeira ordem de anchors foi rejeitada por 22 sprites na scanline; a ordem selecionada mede 13 sprites/104 pixels na pior linha (F106), com 64 links. Isso e geometria local; o gate compartilhado esta bloqueado por espelhos stale e o budget total permanece em aberto.
- ROM V017: 393216 bytes, SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`; build SGDK 2.11 com `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V006`.
- Captura direta diagnostica do BlastEm mostra a sequencia, lockup e hint `A: REVER`; 16 imagens usam intervalo de relogio de parede, sem quadro exato, input ROM-side confirmado ou selo canonico. Report `out/logs/splash_v3_v017_visual_review_report_20261014.json`.
- V016/VGM4 permanece sem escuta humana; audio.raw nao e aprovacao musical. Lettering/model sheet, fundo, contraste, CRT/overscan, movimento, budgets e promocao continuam pendentes. Status mantido `em_desenvolvimento`; FORJA V2 e template inalterados.

## 2026-10-14T10:44:27.2533916-03:00 - splash_v3_visual_v006_wip_curation

- Task: splash_v3_visual_v006_wip_curation
- Skills: art-translation-to-vdp, visual-excellence-standards, megadrive-pixel-strict-rules, sgdk-runtime-coder, sgdk-build-wrapper-operator, emulator-vdp-evidence-curator
- Asset snapshots:
  - img_splash_backdrop_v3 -> v001 (/res/branding_v3/splash_backdrop_v3_320x224.png)
  - img_splash_backdrop_v3_v005 -> v001 (/res/branding_v3/splash_backdrop_v3_v005_320x224.png)
  - img_splash_backdrop_v3_v006 -> v001 (/res/branding_v3/splash_backdrop_v3_v006_320x224.png)
  - img_splash_sgdk_v3 -> v001 (/res/branding_v3/splash_sgdk_wordmark_v3_224x48.png)
  - img_splash_forge_v3 -> v001 (/res/branding_v3/splash_forge_wordmark_v3_192x32.png)
  - spr_splash_particle_v3 -> v001 (/res/sprites/splash_particle_v3_8x8_strip.png)
- ROM: build_v002 (sha256 22c6e3962c253b2588cd07d0b9d4fa2d890d4366b8e4de71a87b59e1b755baf4, 393216 bytes)
- Validation: errors=2, warnings=19
- Blockers: orphan_project_root_entry, noncanonical_project_entry_name, workflow_root_ownership_violation, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_stale, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, tilemap_flag_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: V006 foi mantida como candidata WIP em desenvolvimento: fundo traduzido, lettering B em revisao e captura BlastEm selada vinculada a ROM. Futuro review obrigatorio cobre legibilidade 320x224/CRT, logo e counters, paleta/contraste, tiles/residencia total, particulas/sweep/timeline, replay A, dois ciclos musicais, desempenho e budgets. Nenhuma aprovacao final, arquivamento FORJA V2 ou promocao do template.

## 2026-10-14T12:15:14Z - probes 4bpp de lettering A/B/C preparados

- Criado `data/source_art/branding_v3/build_splash_v3_lettering_native_probes.py`, que recorta as formas autoradas na fonte AI persistida, reduz sem desenhar glifos, quantiza ao grid VDP de 9-bit e grava placas de review fora de `res/`.
- Report `out/logs/splash_v3_lettering_native_probe_20261014.json`: seis placas indexed 4bpp, dimensoes SGDK 224x48/FORGE 192x32, 13-15 cores visiveis; previews por variante e contato de comparacao com o placeholder atual em `rascunho/visual_lab/`.
- A fica perto do placeholder atual; B traz facetas cristalinas mais claras e counters legiveis no probe; C inclina mais e pende ao esportivo. B e recomendacao curatorial para refinamento, sem selecao/aprovacao humana. Runtime, ROM, FORJA V2 e template nao foram alterados.

## 2026-10-14T12:09:08Z - comparacao de lettering sobre V005 criada

- Gerada a prancha conceitual A/B/C sobre o fundo V005 em `data/source_art/branding_v3/sources/source_lettering_runtime_context_ai_v001_20261014.png`, 1024x1536, SHA-256 `20fa2e32a125d829f26bf33287103339699b4e1fb99a55b32e42ce2341fee7d7`; sidecar, curadoria, proveniencia, workset e higiene registram entradas e limites.
- A imagem auxilia a comparar hierarquia/composicao, mas nao e captura real 320x224, conversao 4bpp ou model sheet. Nenhuma direcao foi escolhida; A segue apenas recomendacao de curadoria.
- Nenhum recurso, runtime ou ROM foi alterado. A imagem fica fora de `res/` e o usuario ainda pode escolher A/B/C ou solicitar revisao.

## 2026-10-14T12:05:22Z - folha de lettering WIP registrada para curadoria

- Persistida a folha AI de direcoes A/B/C para lettering, SHA-256 `d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8`, com ficha de curadoria e registro de geracao.
- A direcao A e recomendacao para teste de legibilidade nativa, sem escolha/aprovacao humana. A folha nao e model sheet, nao entrou em `res/` e nao alterou o runtime ou a ROM.
- Atualizados contrato de desenvolvimento, workset, manifestos de fonte e o registro visual/sonoro com pontos de revisao de lettering, proveniencia e leitura em 320x224.

## 2026-10-14T11:58:54Z - V005 visual WIP integrada e curadoria expandida

- Selecionado o backdrop V005 full-detail para o preview isolado; V004 permanece como comparacao. A fonte AI tem SHA-256 `bb32cf3c7e954b99d71fe71ed0197ba10685f1742847ccd1f75e91313016daea`; o PNG runtime 320x224 tem SHA-256 `ef75c6ec1c429e16ad3fa3aae55acf846631d4ff0d5f2a0f3c8b02fe47c39ab0`.
- O plano de cena agora referencia `img_splash_backdrop_v3_v005`: 744 tiles H/V no fundo e 948 no plano completo (30.336 bytes, 54,5% do teto estimado de 1.740). O controle de 40 tiles foi rejeitado por textura quadriculada. Isto e payload de assets, nao fechamento de VRAM/runtime.
- Build SGDK 2.11 Linux/Wine: ROM 262144 bytes, SHA-256 `d4d7e5c842d31e88652d7e06856d9eeb3b4b182bb918c11f5aa20eefe6532319`, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V005`.
- Capturas selecionadas do BlastEm local 1.0.0 mostram energia, reveal e lockup V005; o grupo final inclui quadros pretos de fade e nao fecha o ciclo visual frame-a-frame. WAV de monitor fisico ligado ao mesmo ROM hash tem 10,24 s e sinal presente; escuta/qualidade ainda aguardam o usuario. Relatorio `out/logs/splash_v3_visual_audio_review_report_20261014_v005.json`.
- Atualizados storyboard, contrato de desenvolvimento, workset, manifestos de fonte/proveniencia, TDD, especificacao, memoria e este registro. Nenhuma aprovacao final, arquivamento de FORJA V2 ou troca de template foi feita.
- `validate_resources.ps1`: 3 erros, 20 avisos, 21 verificacoes; `technical_incomplete`, closeout bloqueado por ownership aninhada, tiles carregados por codigo sem medicao e `claim_sources_missing`. Proveniencia (21/21), linhagem visual e self-check da residency V005 passaram; o audit de tiles manteve aviso historico do V004 comparativo.

## 2026-10-13T23:26:42Z - V3 visual WIP integrada e criterios de curadoria sincronizados

- Implementadas e integradas no laboratorio as placas BG_B/SGDK/FORGE e o strip de particulas 8x8; todas permanecem placeholders de desenvolvimento, sem aprovacao final.
- Atualizados storyboard, model sheet proposta, contrato de desenvolvimento, concepcao, GDD, TDD, spec de cena, memoria e curadoria com o runtime real: PAL0 fundo, PAL1 SGDK, PAL2 FORGE, PAL3 particulas; reveal por fade-in (sem placa separada de contorno); replay em A no fim.
- Criado `doc/contracts/visual_source_of_truth_branding_splash_v3.json` como contrato de direcao WIP. `validate_visual_source_of_truth.ps1` passou sem findings; esse resultado cobre linhagem e nao aprova arte final.
- Medidos novamente 990 inputs locais apos self-check dos dois instrumentos. Perfil 64x8x8: 17 sprites/136 pixels por linha, 64 links; sweep 7x8x8: 1 sprite/8 pixels. O report registra a guarda global ainda bloqueada por espelhos externos divergentes.
- Build de preview: 262144 bytes, SHA-256 `3478ae036d80d8df8fc99259ab6e1175c27ceeb9b33bf4f5ec4c724f8010cfd0`; BlastEm local 1.0.0, evidencias selecionadas `preview_observed_unsealed`.
- Adicionados recortes 640x448 dos frames de lockup e convergencia; capturas originais mantidas. Captura canonica, prompt final, video completo, SRAM/VDP dump, budgets e revisao humana continuam pendentes.
- FORJA V2, ROM canonica, template e projetos consumidores permanecem inalterados.

## 2026-10-12T13:39:32Z - estado de desenvolvimento e guardas visuais registrados

- Memoria operacional sincronizada com a decisao do usuario: V015 esta em desenvolvimento e requer futura revisao musical; a ROM canonica continua V2.
- A guarda de medicao global permanece bloqueada por 20 espelhos ativos desatualizados. O relatorio da tentativa de scanline identifica a varredura de 990 quadros como invalida, sem uso para decisoes.
- Registrado no memory bank o estudo de fundo e sua hash; a fonte permanece controle visual de laboratorio e nao entra no `.res`.

## 2026-10-12T13:37:45Z - estudo de composicao visual para a Splash V3

- Criado um conceito de fundo azul/ciano com energia angular convergindo para palco central, em `rascunho/visual_lab/branding_v3_backdrop_concept_20261012.png` (SHA-256 `d1e719488a7e21f0122c9a8a0680995988b887155a8c64c9992089a21ea94063`). A origem foi registrada na higiene do projeto.
- Gerados preview nativo 320x224 e composicao com o controle de lettering V001 para revisar enquadramento/hierarquia. Ambos permanecem em `rascunho/visual_lab`; nao sao assets VDP ou aprovacao visual.
- Adicionados registro de lacuna, estudo visual e plano de camadas em `doc/curation/`. O preview le o lockup em escala nativa, mas nao libera producao, pois o master tipografico e o model sheet aguardam decisao humana.
- Consultado `art_style_catalog.json` e preparado um trio de registros visuais em `doc/curation/`: matriz de estilos, decisao de direcao e master style manifest. `vibrant_16bit_pixel` e apenas a recomendacao de laboratorio; quality reference board, rota tipografica e aprovacao humana continuam ausentes.
- Diagnostico atualizado: os 16 assets ativos continuam tecnicamente adequados, mas a ROM V015 nao contem a cena visual. A guarda global de medicao segue bloqueada; a tentativa de 990 frames foi invalidada.

## 2026-10-12T13:29:20Z - V015 aceita para desenvolvimento; curadoria encaminhada para a cena visual

- O usuario autorizou desenvolver V015 e revisar a musica futuramente para aprimoramento. O status nao significa aprovacao musical final; a revisao de qualidade fica para depois da integracao visual.
- Registrado o historico de escuta para curadoria: som percebido como monofonico/abafado; qualidade ainda baixa; pedido por brilho cristalino; rejeicao de um resultado continuo e monotono sem a energia e a animacao combinadas. V012 permanece a referencia positiva; V013 e V014 permanecem rejeitadas.
- Atualizados briefing de curadoria, design de audio, TDD, memoria, matriz de eventos e reports V015. A ROM/hash de preview e a baseline V2 nao mudaram.
- O diagnostico visual encontrou 16 assets ativos tecnicamente adequados, mas a ROM V015 ainda exibe somente telemetria. O storyboard de sete estados e os controles de lettering permanecem em laboratorio; sem fonte final, model sheet aprovado, runtime V3 ou promocao ao template.
- A coreografia foi ampliada para medir o proximo degrau de 80 particulas e emitiu 990 inputs. A tentativa do simulador foi marcada invalida porque a guarda global ainda bloqueia medicao por `project_source_mirror_stale`; nenhum resultado orienta arte ou budget.
- FORJA V2 nao foi arquivada e o template nao foi substituido.

## 2026-10-12T12:04:08Z - composicao V013 com acentos cristalinos

- O usuario disse que V012 ficou bem melhor e pediu mais brilho cristalino. V012 foi preservada integralmente com score, builder, VGM/XGM2, ROM, captura e reports em `out/audio/revisions/v012/`.
- Mantido o motivo V012; acrescentado um quarto patch FM aditivo (FM_CH4) para tres notas curtas C6-G6-C7 nos score frames 30, 138 e 174, fora dos cues PCM. O gerador agora trata os bancos de registradores do YM2612 para canais 4-6, e o auditor de loop confere o estado dos seis canais.
- VGM V013 de 210 quadros: SHA-256 `8300e25f02a5e41b3e0f6e4e21c33f3d3607fd5e559a0d8da21b738cbbff5527`; XGM2 de 772 bytes: SHA-256 `3ec5b2d8f16d120b9781c8078206c96cf873521057ca183a4aedf9a695906fb0`.
- Validacao de audio: 12 declaracoes, zero issues; proveniencia: 12 entradas, zero erros/avisos; conversao XGM2 e relatorio estrutural do loop passaram. ResComp incluiu musica de 768 bytes e quatro cues PCM totalizando 22.272 bytes.
- ROM V013 buildada via bridge Linux/Wine a partir do SDK canonico do workspace: 262.144 bytes, SHA-256 `5eb765fc5e6d7655ae5b3b20d7a59cd521b5719945385bacdbcdea629eab83bd`.
- BlastEm Flatpak 1.0 executou o ciclo: `FRAME:309`, `CYCLE DONE`, quatro status PCM, `MUSIC 209/209 DROP:0`; captura `out/blastem_audio_probe_v013/splash_v3_audio_probe_v013.png`, SHA-256 `753d86f8bf889c653cf6dac50d217b0f8a24b55ab0e26b6de717bf46c36f5a18`. Janela deixada aberta; Z repete o ciclo.
- O valor 59.9 fps no titulo e instantaneo, nao prova taxa sustentada. A rota canonica BlastEm continua pendente pelo fetch 404 da versao fixada 0.6.2. V013 aguarda escuta do usuario; nenhuma promocao ou arquivamento da FORJA V2 foi feito.
- A ROM canonica V2 e o template permanecem intocados; V013 fica preservada em `out/audio/revisions/v013/`.

## 2026-10-12T11:42:07Z - composicao V012 e pre-escuta no BlastEm

- O usuario rejeitou V010 por baixa qualidade musical. V011 foi buildada e executada; a revisao do score encontrou a nota PSG inicial dentro da subida PCM e a quinta G5 atravessando sweep/tail. V011 foi preservada em `out/audio/revisions/v011/` e supersedida antes da revisao formal.
- Ajustado o score autoral para V012: a frase continua `C5-G5-E5-F5 | D5-G5-B5-C6`; os glints PSG agora estao nos score frames 75/105, e G5 ocorre por seis quadros em 174-179, fora das janelas PCM. O tail C/E/G completa o acorde aberto sem camada PSG concorrente.
- Render NTSC VGM de 210 quadros: SHA-256 `186edc0eafb1a288f702e7ca709fca9025a75e7116dd35032292ebf37ed8e6fd`; XGM2 oficial: `0c943c3bedcd24f87191a909421e44efe8f8ed0e26353abcfa5b585133997c42`. A auditoria estrutural do loop passou, com a emenda audivel ainda pendente.
- Proveniencia XGM2: 12 entradas, zero erros/avisos. `validate_audio.ps1` passou sem issues. ResComp compilou os recursos V012; os quatro payloads PCM somam 22.272 bytes.
- ROM V012 via SGDK Linux Wine bridge: 262.144 bytes, SHA-256 `770dd9a796f8c23a1aa76aab91e06d3a6a85bd2d9de399b23b72be3288b5009f`. BlastEm Flatpak 1.0 mostrou o ciclo completo, quatro cues PCM e `MUSIC 209/209 DROP:0`; screenshot `out/blastem_audio_probe_v012/splash_v3_audio_probe_v012.png`, SHA-256 `c29f1d9e6f340aef40b64f00a66f2b660af927e9c79dfc777478392059226a14`. ROM ficou aberta para o usuario ouvir; Z reinicia o ciclo.
- O fetch da versao BlastEm 0.6.2 exigida pela captura canonica retornou HTTP 404 antes do boot; a pre-escuta direta em 1.0 nao fecha o gate canonico. Qualidade musical de V012, FPS sustentado, budget DAC e integracao da cena V3 continuam pendentes. Nenhuma promocao foi feita.
- A ROM canonica V2, o template e o arquivo de FORJA V2 permanecem intactos.

## 2026-10-12T11:14:21Z - nova composicao sonora e ROM de pre-escuta V010

- Registrado em `doc/branding_v3_audio_curator_brief.md` o feedback de que a candidata anterior soava abafada, monofonica e fragmentada, junto ao novo alvo de 2-4 segundos, lead FM claro, harmonia audivel e resolucao maior. As referencias historicas foram tratadas apenas como caracteristicas gerais; nenhuma melodia ou marca foi copiada.
- Criado o score `data/source_audio/splash_v3_sonic_logo_score_v2.json`: frase autoral de oito notas em E maior, dois compassos 7/8, 210 quadros NTSC (3,5 s), brass FM no lead, harmonia de sino, baixo curto e glints PSG. A candidata anterior permanece em sua fonte e artefatos originais.
- Recompostos os cues em `data/source_audio/splash_v3_pcm_cues_v2.json`; subida e sweep usam tons de E maior, lock destaca E/B/E6 e tail reforca E/G#/B. WAVs v2 ficam isolados em `res/audio/branding_v3_v2/`.
- VGM gerado com SHA-256 `cd8a6d323b314ff1bc2989071006e4f4d189ce295d5fe1f41a975a627b0adb74`; conversao XGM2 oficial: `f24424a94f554beb48639e434ee3e486b73f8a79ee87d85fb13af9a6a3d2655f`. A checagem estrutural de loop passou; a emenda audivel segue pendente.
- Build isolado V010 passou pela rota SGDK Linux Wine bridge; ResComp reconheceu a musica e os quatro cues. ROM de 262144 bytes, SHA-256 `d6f823bac611bb17fd4fa7bd6eee3808686bb50d6c971ff629b71801d701fe97`.
- BlastEm Flatpak 1.0 abriu V010 e completou o ciclo: quatro status PCM e `MUSIC 209/209 DROP:0`; a janela foi deixada aberta para escuta, e a tecla Z (botao A no mapeamento do BlastEm) reentrou no ciclo. Capturas: `out/blastem_audio_probe_v010/splash_v3_audio_probe_v010.png` (SHA-256 `2fa7804357d330351b883df90b35056ab68248244683eac173e74f4db2e0879f`) e `splash_v3_audio_probe_v010_replay.png` (SHA-256 `37cdeb5901f4db2d472c70a356c7dd7734d331b310386f4649ac8598a94fa44b`).
- A escuta humana, aprovacao da composicao, medicao DAC e QA canonico continuam pendentes. A ROM canonica V2, o template e o arquivo de FORJA V2 nao foram alterados.

## 2026-10-12T10:41:25Z - pre-escuta rotulada V009

- A montagem local de `sega.s` agora usa `MG_ROM_HEADER_PATH`, com fallback para `out/rom_head.bin`; o cabeçalho do probe passou a identificar corretamente a build isolada.
- Ajustado o indice de foreground PAL1 do texto diagnostico para ciano, corrigindo a captura vermelha da V008.
- V009 buildada pelo SGDK Wine bridge e aberta no BlastEm Flatpak 1.0. Evidencia e limites em `out/logs/splash_v3_audio_probe_preview_v009_20261012.json`.
- A captura mostra quatro cues com status PCM e 209/209 amostras de `XGM2_isPlaying()` sem quedas. Mix audivel, qualidade humana, FPS sustentado, budgets e gate BlastEm canonico seguem pendentes; `out/rom.bin` V2 foi preservada.

## 2026-10-12T10:31:51Z - comparacao dos estudos de lettering v3

- Registrados dois estudos AI e previews encaixados nas placas do storyboard; ambos permanecem `visual_lab_control` em `rascunho`, sem promocao a `/res`.
- Corrigido o report v001: o master contem 16.654 valores RGB opacos distintos, portanto nao e uma arte de tres cores planas nem uma fonte pixel-native.
- `premium_source_manifest.json` e a concepcao agora distinguem explicitamente estudos de laboratorio de fonte de producao. Rota de lettering e model sheet continuam sem aprovacao.

## 2026-10-12T09:40:14Z - abertura de espaco para os cues finais

- Ajustada a frase de saida: o lead E5 libera exatamente no inicio do cue tail e o bass resolve de F#3 para E2, sustentado pelo pad E3.
- VGM reexportado, 840 quadros NTSC; SHA-256 `82744b6f00e6d067cca3eafa3ab17a5387fdc31e375063a8855e3d28dac4e5df`.
- Conversao XGM2 oficial repetida; SHA-256 `a0696fae619499281ff5f858a97993d968573daa40bd0ca91c56298908426313`.
- A separacao musical e estruturalmente validada pela partitura, mas a mix continua candidata `lab`, sem escuta em ROM.

## 2026-10-12T09:36:17Z - quatro cues PCM autorais v3

- Criados fontes e parametros de quatro cues (`energy_rise`, `mark_lock`, `sweep_pass`, `tail`) em `data/source_audio/splash_v3_pcm_cues.json` e `build_splash_v3_pcm_cues.py`.
- WAVs candidatos e payloads assinados foram escritos somente em `out/audio/splash_v3_pcm/`; nenhum recurso foi adicionado a `res/resources.res`.
- Conversoes XGM2 a 13.3 kHz passaram sem clipping e com alinhamento de 256 bytes. O conjunto soma 24.320 bytes antes do overhead de recurso.
- Resumo e bloqueios em `out/logs/splash_v3_pcm_candidate_format_audit_20261012.json`; cada cue tambem tem report de conversao e sidecar de lineage.
- Os samples continuam `lab`; ResComp, budget DAC, mix no BlastEm e aprovacao auditiva seguem pendentes.
- Acrescentados report de ownership, estimativa de payload DAC e findings de entrega. Ownership e budget seguem `not_observed` ate a integracao e a prova hash-bound.

## 2026-10-12T09:32:57Z - score e exportacao musical FM/PSG v3

- Criada partitura autoral E Dorian em 7/8, com bass, pluck/lead, pad e duas vozes PSG; fonte e patches em `data/source_audio/splash_v3_music_score.json`.
- Criado exportador deterministico VGM em `data/source_audio/build_splash_v3_music_vgm.py`; o ciclo NTSC tem 840 quadros e hash `58c7ff01cf4906bea5cc08820681d28a97c13ae724111a0a59d9e92d155987ff`.
- A conversao oficial SGDK gerou XGM2 com magic correto, FM block 512 bytes, PSG block 256 bytes e hash `a5966120247b13819e56e0894fcfd5f84c3fa36e6b45d96382f9cfa8fad8d4ca`.
- Linhagem e hashes em `out/audio/splash_v3_music.provenance.json`; relatorio de conversao em `out/logs/splash_v3_music_conversion_20261012.json`.
- O resultado permanece candidato `lab`: sem cues PCM, recurso `.res`, runtime ou escuta humana. Conversao e metadados nao validam qualidade sonora.

## 2026-10-12T09:20:12Z - fechamento da forma musical no tempo da splash

- O ciclo de 16 s anterior nao fechava: a splash parava em 3,5 s, antes do final da frase musical.
- Ajustada a composicao alvo para oito compassos em 7/8 a 120 BPM. O loop completo passa a 840 quadros NTSC (14 s); a splash ouve os dois primeiros compassos, de F030 a F240, e sai numa cadencia planejada.
- Sincronizados escopo de composicao, matriz de eventos, plano de integridade, TDD e design de audio.
- Isso e apenas direcao e contrato: nenhum score, sample, VGM/XGM2, runtime ou build foi criado.

## 2026-10-12T09:16:54Z - auditoria de API SGDK para runtime v3

- Inspecionados os headers e a implementacao do SGDK 2.11; report em `out/logs/branding_v3_api_reality_check_20261012.json`.
- Confirmados engine moderno, assinatura de cinco argumentos para `SPR_addSpriteEx`, pool fixo de 80 objetos e reserva de tiles feita por `SPR_initEx(vramSize)`.
- Corrigido o comentario de `SPR_initEx(16)` em `src/core/app.c`; nenhuma instrucao executavel mudou.
- O snapshot do gate visual foi sincronizado com o report global de medicao de 2026-10-12; nenhum budget foi medido.
- Nenhum runtime V3, asset, build ou evidencia nova foi produzido.

## 2026-10-12T09:09:46Z - contratos de audio autoral v3

- Substituida a direcao alvo herdada da FORJA no `doc/17-audio-design.md`; a baseline de runtime continua V2 ate a implementacao.
- Criados card XGM2, escopo de composicao, mapa de eventos, plano de mascaramento, integridade do loop e prova de audio BlastEm em `doc/branding_v3_*`.
- Corrigida a semantica de tempo: 735 e a quantidade de amostras VGM por quadro NTSC; o loop de oito compassos planejado tem 960 quadros, 16 segundos.
- Validacao Draft-07 passou para `branding_v3_audio_architecture_card.json` e `branding_v3_composition_scope_contract.json`.
- Os sete self-checks de ferramentas de audio passaram; report em `out/logs/branding_v3_audio_tool_selfchecks_20261012.json`.
- Nenhum score, WAV, VGM, XGM2, sample ou runtime V3 foi criado; qualidade auditiva e loop continuam sem prova humana.

## 2026-10-12T08:54:29Z - retomada autorizada da implementacao Splash V3

- O usuario autorizou implementar a V3 e, somente apos validacao completa, arquivar FORJA V2 e substituir a splash do template.
- O laboratorio mantem contexto `technical_demo`; o template nao foi alterado e os cinco projetos consumidores nao foram migrados.
- O gate global atual passou 30/30 self-checks, mas permanece bloqueado por 20 espelhos ativos de `runtime_probe` desatualizados em 11 projetos. Report: `out/logs/measurement_gate_report_workspace_20261012.json`.
- Nenhuma medicao V3 foi executada. A ROM vigente continua sendo a baseline V2; lettering, audio e runtime V3 nao foram produzidos.
- Rota de lettering e reconciliacao de espelhos aguardam resposta humana; nenhum arquivo externo foi modificado.

## 2026-10-12T02:15:43.0177427Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia


## 2026-10-12T02:58:24Z - auditoria de espelhos de runtime_probe

- Comparadas as 20 copias ativas desatualizadas em 11 projetos contra o canone; seis arquivos pertencem a tres consumidores protegidos.
- Gerado diff somente para revisao em out/logs/runtime_probe_mirror_review_20261012/. As substituicoes integrais variam de 4 a 841 linhas de diff e nao sao seguras em lote cego.
- Nenhum espelho externo foi alterado. O gate de medicao permanece bloqueado ate reconciliacao autorizada por projeto.

## 2026-10-12T02:55:49Z - selecao inequivoca do storyboard v3

- O loader de residencia escolhe doc/*storyboard*.json em ordem alfabetica; sem ajuste, o storyboard v2 herdado precedia e escondia o plano v3.
- Preservado o v2 com hash em rascunho/baseline_branding_v2, referencias locais atualizadas e spec esclarecida. O template e os projetos consumidores nao foram alterados.
- A leitura pelo loader sera verificada; nenhum budget ou medicao foi produzido.

## 2026-10-12T02:53:50Z - compatibilidade do plano de residencia

- Corrigida a estrutura de cada estado do storyboard para expor id e resident diretamente, conforme o consumidor real audit_tile_residency.py; a forma aninhada anterior passava no schema mas seria ignorada pelo auditor.
- Atualizada a spec, mantendo os simbolos e budgets como nao medidos. Nenhum auditor de tile residency ou simulador de scanline foi executado neste passo.

## 2026-10-12T02:48:10Z - diagnostico e higiene documental

- Diagnostico de assets do laboratorio: cenario de revisao de /res; 16 assets ativos conformes, sem blockers de build. As fontes em /data permanecem fora do grafo ativo e parte delas exige conversao.
- Arquivados 14 relatorios herdados do template em out/logs/template_baseline_snapshots/, com SHA-256 registrado; fontes de relatorio atualizadas para emitir em out/logs/.
- Referencias de relatorios foram atualizadas para os snapshots; fontes ativas nao mantem caminhos absolutos externos.
- Contexto, metodologia, higiene, layout e quatro schemas passaram. Os 798 inputs de frame seguem generated_unmeasured; o simulador nao foi invocado.
- Lettering continua aguardando decisao humana; gate de medicao global continua bloqueado. Sem pixel art V3, build, ROM ou evidencia de emulador.

## 2026-10-11 — bootstrap do laboratorio Splash v3

- Criada copia isolada do template em `_agent_laboratory`; 343 arquivos, 28,493,991 bytes, todos com SHA-256 igual a origem no instante da copia.
- Contexto classificado como `technical_demo`; teto de claim `technical_demo`.
- Materializacao `.agent` local corresponde a versao canonica `2026.09.05`; bootstrap reportou `degraded=0`.
- Nenhuma ROM ou captura foi criada. O gate global de medicao esta bloqueado por espelhos ativos `runtime_probe` defasados fora deste projeto.

- Removido do laboratorio o contrato de cena gerado herdado, que apontava para a spec absoluta do template; sera compilado novamente da spec local.
- Reescrita a spec de cena para a splash v3 e criados concepcao, context pack, storyboard de sete estados, TDD e contrato de transicao.
- GDD e roteiro agora descrevem o technical_demo e a narrativa em prosa; route decision record foi sincronizado na spec.
- Registradas as tecnicas planejadas com registry IDs, tags, owners, budget pendente e fallbacks; nenhum item foi promovido como implementado.
- Confirmado na documentacao local do ResComp que uma SpriteDefinition possui dimensao fixa por quadro; perfis 8x8 e 16x16 ficam separados.
- Confirmado no fonte SGDK 2.11 que SPR_initEx(16) reserva tiles de VRAM e que o object pool tem MAX_SPRITE=80; a matriz de 64 candidatos continua exigindo medicao de VRAM e scanline.
- Gerados 9 arquivos de serie e 798 inputs por quadro para os perfis 24/32/48/64, geometrias 8x8/16x16 e sweep; todos marcados unmeasured, sem chamada ao simulador.
- Mantidos os budgets em needs_review e a arte bloqueada. A rota de lettering aguarda decisao humana; o gate global de medicao continua bloqueado.
## 2026-10-12T05:29:04.6669713-03:00 - build_baseline_v2_preview

- Task: build_baseline_v2_preview
- Skills: sgdk-build-wrapper-operator
- Asset snapshots:
  - img_starfield_v2 -> v001 (/res/branding/starfield_320x224.png)
  - img_forge_bg_b -> v001 (/res/branding/forge_bg_b_320x224.png)
  - img_forge_bg_a_props -> v001 (/res/branding/forge_bg_a_props_320x224.png)
  - spr_forge_ember -> v001 (/res/branding/spr_forge_ember_16x16_strip.png)
  - spr_forge_shard -> v001 (/res/branding/spr_forge_shard_16x16_strip.png)
  - spr_forge_hammer -> v001 (/res/branding/spr_forge_hammer_48x48_strip.png)
  - img_logo_engine_v2 -> v001 (/res/branding/logo_engine_224x64.png)
  - img_logo_author_v2 -> v001 (/res/branding/logo_author_192x32.png)
  - img_logo_project_v2 -> v001 (/res/branding/logo_project_224x48.png)
  - img_presents_text_v2 -> v001 (/res/branding/presents_text_96x16.png)
  - img_presents_bar_v2 -> v001 (/res/branding/presents_bar_8x8.png)
- ROM: build_v001 (sha256 51a34305826e4120afa3c6ec63b750bf83d47b3125d087d01c5f3516323ae3f9, 262144 bytes)
- Notes: Linux bridge build succeeded for the existing A FORJA v2 dispatch; ROM SHA-256 51a34305826e4120afa3c6ec63b750bf83d47b3125d087d01c5f3516323ae3f9, 262144 bytes. Replaced only the lab ROM header placeholder. Preview opened in installed BlastEm Flatpak 1.0 and reached the menu; screenshot and hash are in out/blastem_preview and out/logs/blastem_manual_preview_report.json. Canonical capture remains blocked because the 0.6.2 pinned commit request returned 404. No SRAM/VDP dump, gameplay, audio, or sustained performance claim.


## 2026-10-12T09:44:51Z - auditoria estrutural de audio V3

- O loop VGM passou a auditoria estrutural byte a byte: 840 quadros no ciclo, ponteiro de loop valido e canais FM/PSG em estado silencioso na emenda e no fim do arquivo.
- Gerado out/logs/splash_v3_audio_loop_report.json; o report deixa claro que isso nao substitui duas voltas ouvidas, reentrada de cena ou prova de audio na ROM exata.
- 16 verificacoes de hash ligaram score, builders, VGM, XGM2, quatro WAVs, quatro payloads PCM e o report do loop. Resultado em out/logs/splash_v3_audio_artifact_integrity_20261012.json, teto integrity_pass_candidate_only.
- Sincronizados memory bank e findings de entrega. Sem alteracao de runtime, .res, template ou projetos consumidores.

## 2026-10-12T10:01:59Z - integracao candidata e probe de audio V3

- Declarados `mus_splash_v3` e os quatro cues PCM em `res/resources.res`; ResComp compilou todos os recursos na ROM candidata de integracao. Payload PCM total: 24.320 bytes.
- Implementado ownership de audio V3 em `src/system/audio.c`, com cues PCM nos canais CH2/CH3 e fallbacks PSG nomeados. O despacho normal do app e a cena V2 permanecem inalterados; o probe V3 e selecionado apenas por compile flag.
- ROM probe V004: 262.144 bytes, SHA-256 `847eb7b36e5d437420e9904edd35850f2e19a703a3c39b4a82478b69763f3e07`. BlastEm Flatpak 1.0 observou o ciclo de 240 quadros e as quatro chamadas PCM com retorno de sucesso; report `out/logs/splash_v3_audio_probe_preview_20261012.json`.
- Limites registrados no review: nao houve escuta humana; o indicador de playback da musica nao foi preservado na captura; sem medicao DAC/VDP, cena visual de producao, QA canonico ou validacao de 60 fps sustentados. Nenhum status de entrega foi promovido.
- Atualizados memory bank, TDD, desenho de audio, matriz de eventos, architecture card e findings para refletir a evidência candidate-level. FORJA V2, template canonico e projetos consumidores nao foram alterados.

## 2026-10-12T10:06:06Z - leitura persistente do estado XGM2 no probe

- O probe agora retém na tela o resultado de `XGM2_isPlaying()` amostrado no quadro 31, permitindo revisar o dado depois do ciclo sem confundi-lo com playback continuo.
- Build V005: ROM de 262.144 bytes, SHA-256 `129ca536a1da8051a674ee44b90e156dc4575cc9601c31cd56023368cc9b36b7`; BlastEm Flatpak 1.0 mostrou o ciclo completo, quatro chamadas PCM com retorno de sucesso e `MUSIC@31: PLAYING`.
- Screenshot: `out/blastem_audio_probe/splash_v3_audio_probe_v005.png`, SHA-256 `2cace86c11c33e6fc9301f667f8c42a9539b5a71b1baf883d67024b105c7f89d`.
- A leitura no quadro 31 nao comprova continuidade do playback nem qualidade audivel. Escuta humana, budgets, runtime visual de producao e captura canonica permanecem pendentes.

## 2026-10-12T10:09:08Z - reentrada observada no probe de audio

- A tecla A reiniciou o probe apos `CYCLE DONE`; a tela voltou ao quadro 010 e ao estado `MUSIC@31: WAITING`.
- Captura de reentrada: `out/blastem_audio_probe/splash_v3_audio_probe_v005_replay_check.png`, SHA-256 `2847839d18a99cac257373a23bd29e40ef1fa44b3849f09c8550423ce0722cfd`.
- Atualizados findings, matriz de eventos, relatorio de preview, code review e memoria operacional. A observacao cobre apenas o probe, nao valida a transicao da futura cena de producao.

## 2026-10-12T10:15:42Z - monitor de playback e conceito de lettering

- O probe V006 amostra `XGM2_isPlaying()` em todos os quadros 31-239 e reporta 209/209 amostras de playback e `DROP:0` em BlastEm Flatpak 1.0. Isso prova o estado do driver, nao saida audivel ou qualidade da mix.
- ROM V006: 262.144 bytes, SHA-256 `cdbfd418794de57adb07e660d654fc50401a4a70151978396ba2ee1682be922e`; captura principal em `out/blastem_audio_probe/splash_v3_audio_probe_v006.png` (SHA-256 `d3d69796cb8fa9b81616eddb76b7e6b7c93feaf0d7857c2a03e840771cf48dab`); replay por A confirmado.
- Criado conceito de lettering AI transparente para revisao, copiado a `rascunho/entrada_bruta/branding_v3_lettering_master_ai_v001.png`, SHA-256 `f776eb032d64f2de310676694b1483c00f9a4d532617f81dd1e8f2737e68879a`. `acceptance_status=visual_lab_control`; a rota permanece pendente e nenhum pixel foi promovido a `/res`.
- Atualizados TDD, audio design, matriz, findings, relatorio de preview e memoria. Template e FORJA V2 continuam intactos.

## 2026-10-12 - composicao sonora V014

- Registrada a rejeição humana de V013 por soar contínua e monótona, sem a energia e a animação combinadas. V013 foi preservada no arquivo de revisões como rejected_by_user.
- Criado o score candidato V014: motivo de oito notas baseado em V012, 6/8 a 120 BPM, ataques staccato, respirações entre frases, baixo e harmonia pontuados, três acentos FM cristalinos curtos e entrada após o cue de energia.
- Preview limitado a ROM de laboratório; nenhum status de aprovação musical, validação de budget, promoção ao template ou arquivamento da FORJA V2 foi concedido.

## 2026-10-12T12:52:11Z - ROM de audição V014

- Build V014 concluído pelo Linux SGDK Wine bridge; ROM de 262.144 bytes, SHA-256 f0fedae74ab9a2e64680022f98c9a2d90ab77334eb8687c9e5028dc1bc73d407.
- A ROM exata abriu em BlastEm Flatpak 1.0 e chegou ao fim do ciclo. O monitor mostrou 179/179 quadros de playback XGM2, zero quedas e os quatro cues PCM iniciados; captura dedicada em out/blastem_audio_probe_v014/.
- A checagem estrutural do loop 6/8 (180 quadros), conversão XGM2, validação de áudio (12 declarações, zero problemas) e auditoria de proveniência (12 entradas, zero erros/avisos) passaram. A escuta V014 pelo usuário, budget DAC, desempenho sustentado, captura canônica e cena V3 completa continuam pendentes.

## 2026-10-12 - estado do closeout geral da V014

- validate_resources.ps1 gerou validation_report.json, mas o closeout amplo ficou false: 11 erros e 16 avisos. Blockers incluem sync documental das tecnicas, insuficiencia do GDD para AAA/delivery, estado degradado de .agent e ausencia de reports visuais, scene compile, res graph e scene closeout. Nenhum desses resultados altera o passe das auditorias especificas de audio.
- freshness_audit.ps1 ficou em warning: generic build_output.log stale e scene_contract_compile/res_graph ausentes; os relatorios ficam vinculados ao candidato V014.

## 2026-10-12T13:19:30Z - rejeicao V014 e ROM candidata de audio V015

- O usuario rejeitou V014: o resultado ainda soava continuo e monotono, sem a proposta de animacao e energia. V014 permanece no arquivo de revisoes com status rejected_by_user.
- Recomposta a trilha a partir do contorno positivo de V012: oito ataques sincopados C5-G5-E5-F5 | D5-G5-B5-C6, releases FM mais rapidos, apenas 52/180 quadros de gate no lead, quatro stabs C3/F2/G2/C3 e tres pings aditivos E6/G6/C7 de 3-4 quadros. A pausa musical deixa o cue mark-lock sozinho; todas as notas terminam no quadro de cena 174, antes do sweep em 178.
- VGM V015: 180 quadros / 3 s, 1060 bytes, SHA-256 86a29044d2a280ec1cd4d8d612763202e435ed2856c3ac92932210b17662e739. XGM2 NTSC: 772 bytes, SHA-256 160980ab0d8ab1cab523ea54d0c90225c8fc1f726b0b82f0312d058cbcc9c50a.
- ROM de laboratorio buildada com SPLASH_V3_AUDIO_PREVIEW: 262144 bytes, SHA-256 20e99ff61ef49f73be2e39f341ce13162d87c5fc0c271a1125963ca550db92e6; SDK content identity corresponde a sdk/sgdk-2.11 do workspace. A ROM exata completou o ciclo em BlastEm Flatpak 1.0; captura mostra MUSIC 179/179, DROP:0 e os quatro cues PCM.
- Conversao XGM2, loop estrutural 180 quadros, auditoria de proveniencia (12 entradas, zero findings), ResComp e build passaram. Escuta musical e costura do loop aguardam o usuario; preview nao canonico, budget DAC e performance sustentada nao medidos.
- FORJA V2 e o template canonico permanecem inalterados ate a validacao completa da Splash V3.

## 2026-10-13 — V3 em desenvolvimento: correcao de coreografia e estudos visuais

- Registrada a decisao do usuario de manter Splash V3 em desenvolvimento, com revisao futura; sem aprovacao final de audio ou visual.
- Criados conceitos visuais de BG_B, lockup SGDK/FORGE e linguagem de fragmentos cristalinos em `rascunho/visual_lab/`; hashes e autorizacao exploratoria adicionados ao manifesto de higiene. Nenhum arquivo foi promovido a `data/`, `res/` ou ROM.
- Criado o model sheet de proposta e novo registro de curadoria visual. A rota de lettering, fonte de verdade, aprovacao humana e quality reference board permanecem pendentes.
- A coreografia anterior concentrava 24 particulas no centro e ultrapassava H40. O gerador agora espalha nascimentos em 60 quadros e inicia no anel de 8px. Medida completa de 990 quadros: perfil 64x8x8 passa com pico 17 sprites/136 px por linha; 80x8x8 falha em 23 sprites; perfis 16x16 falham em densidades mais baixas. Sweep 7x16x32 passa com pico de 1 sprite/16 px.
- A medicao usa o simulador v1.2.0 e runner com self-check valido; sete self-checks locais passaram. Storyboard V3 revalidado no schema cinematografico. Relatorio `out/logs/splash_v3_scanline_matrix_scoped_20261013_r3.json`; scope limitado a geometria de sprites. O gate global continua bloqueado por espelhos de probes externos; nenhuma copia de outro projeto foi alterada.
- A auditoria de fonte visual permanece bloqueada por contrato `visual_source_of_truth` ausente. V2, template, ROM canonica e consumidores nao foram alterados.
- Atualizado o gate global em 2026-10-13: 30/30 self-checks passam, mas os mesmos 20 espelhos ativos em 11 projetos mantem o bloqueio. Inventario read-only comparou diferencas por arquivo e recomenda merges individuais para preservar instrumentacao local; nenhum projeto externo foi modificado.

## 2026-10-14 — Splash V3 V004 em desenvolvimento

- Registrada a decisao do usuario: manter a Splash V3 em desenvolvimento e exigir revisao futura de curadoria. Nao houve aprovacao final de audio, arte, lettering/model sheet, ROM, template ou arquivo FORJA V2.
- V004 foi integrada como candidata visual WIP e buildada em ROM SGDK 2.11 via Linux/Wine bridge: 262144 bytes, SHA-256 `b852241c1058999cdf99056e9f6f95be159d17f70b85ddf7b99c0e29257aae97`; flag `SPLASH_V3_VISUAL_PREVIEW`.
- O preview local em BlastEm 1.0.0 observou estados selecionados, prompt legivel e replay com BUTTON_A apos focar a janela. Capturas manuais sem selo canonico: `out/logs/splash_v3_visual_preview_report_20261014_v004.json` e `out/blastem_splash_v3_visual_preview_20261014/v004_replay_sequence_contact_20261014.png`. A timeline segue nominal em 240 quadros; as legendas sao aproximadas e nao medem sincronismo frame-a-frame.
- O host nao tinha PulseAudio; SDL dummy foi usado, entao audio nao foi avaliado. V012 e referencia positiva; V013/V014 rejeitadas; V015 permanece WIP sem aprovacao ou escuta final.
- Fundo V004: 918 raw/916 tiles H/V unicos (18% dedup); residency total de arte 1120/1740 tiles (35.840 bytes; 64,4%). Remapeamentos automaticos 40/80/120/160 foram rejeitados por facetas fragmentadas. Reautoria em tiles reutilizaveis, sem repeticao mecanica, e item de curadoria futura.
- Revisao visual: avaliar centro negativo, cristais de borda, particulas sobre letras, hierarquia/contraste de FORGE, sweep e fade em 320x224; aprovar rota/model sheet do lettering antes de pixel final.
- Pendentes: dois ciclos de escuta com backend funcional, video frame-accurate, evidencia canonica BlastEm hash-bound, SRAM/VDP dump quando aplicavel, total VRAM/DMA/VBlank/CPU/DAC e 60fps sustentados.
- A classificacao de contexto `technical_demo` e metodologia passaram na fase de implementacao. A higiene local continua bloqueada por arvore `SGDK_projects/` aninhada nao classificada (`orphan_project_root_entry`, `noncanonical_project_entry_name`, `workflow_root_ownership_violation`); ownership exige inventario de consumidores, hashes e leases pelo workflow de armazenamento.
- `preflight_host`, contexto, metodologia e `validate_visual_source_of_truth.ps1` passaram. `scene_closeout_gate.ps1` terminou em `warn`; `res_graph_audit.ps1` emitiu `RG_CODETILE001`. `validate_resources.ps1` confirmou sincronizacao dos nove IDs e fechou com `closeout_gate=false` (3 erros, 19 avisos): ownership da arvore aninhada, `code_loaded_tiles_unmeasured` e `claim_sources_missing`. Freshness reporta 1 artefato stale e 0 required ausentes; conversao/flags/paleta, audio stale e snapshots de assets continuam em aviso.
- `audit_project_learning.ps1 -Mode Capture` registrou `no_qualified_lessons`; `canonical_promotion_performed=false`.
- IDs do registry sincronizados no memory bank e TDD: `fixed_point_trig_lookup`, `dma_transfer_safety`, `palette_state_transitions`, `shadow_highlight_slot_rule`, `palette_remastering_slot_audit`, `tile_flipping`, `tile_dedup_hvflip_hashing`, `xgm2_pcm_multiplexing`, `xgm2_audio_architecture`.
- FORJA V2, ROM canonica, template e consumidores permanecem inalterados.


## 2026-10-14 — lettering B ativo como WIP e build bloqueado antes de make

- Registrada a decisao do usuario de manter a Splash V3 em desenvolvimento, exigir revisao futura e continuar a etapa visual. B `faceted_crystal` e recomendacao curatorial ativa; nao foi escolhida nem aprovada pelo usuario.
- As placas B passaram para os caminhos isolados de `/res` com os baselines pre-B preservados: SGDK 224x48 (143 raw/141 H/V) e FORGE 192x32 (92 raw/91 H/V). Composite estatico 320x224: `rascunho/visual_lab/splash_v3_lettering_probe_b_v001_320x224.png`; isso nao e captura de ROM.
- Residency WIP recalculada: fundo 744 + SGDK 141 + FORGE 91 + particulas 8 = 984 tiles H/V, 31.488 bytes, 56,6% do teto de payload estimado. Proveniencia passou para 21/21 simbolos.
- Build pelo wrapper Linux/Wine bloqueou antes de make. Flatpak/bwrap falhou em `winepath` com `No space left on device`; `/run/user/1000` estava 100% ocupado (1.5G/1.5G), com diretorios pytest existentes como maiores consumidores visiveis. Nenhum dado temporario foi apagado. ROM e reports anteriores permanecem intactos.
- `out/logs/splash_v3_lettering_b_build_block_20261014.json` registra a triagem. `out/rom.bin` continua sendo o preview V005 pre-B, 262144 bytes, SHA-256 `d4d7e5c842d31e88652d7e06856d9eeb3b4b182bb918c11f5aa20eefe6532319`; nenhuma alegacao de runtime/qualidade para B.
- Checklist completo de curadoria visual/sonora atualizado em `doc/curation/splash_v3_visual_curation_record_20261014.md` e `doc/branding_v3_development_contract.json`. FORJA V2, template canonico e consumidores continuam inalterados.


## 2026-10-14T16:07:59Z — curadoria visual e handoff candidato Splash V3

- V007 registrado como rejeitado; V008 e V009 preservados como comparativos nativos 320x224. V008 tem centro mais limpo porem simetrico; V009 recupera direcao mas exige safe-area review. V006 nao foi alterado nem substituido.
- Implementado no laboratorio o perfil SPLASH_V3_MENU_HANDOFF: dreno de fade/DMA, cleanup de audio/scroll/window, mutex de 12 quadros e fade-in do menu. APP_update evita atualizar a cena nova no quadro da troca.
- Build canonico tentou rota Linux/Wine e parou antes da compilacao em resolve_wine_paths por bwrap: No space left on device; nenhum ROM foi produzido. Report out/logs/splash_v3_handoff_build_attempt_20261014.json.
- Estado segue em desenvolvimento. Sem aprovacao de audio/visual/model sheet, sem arquivamento FORJA V2 e sem troca do template.

## 2026-10-16 — sonda SAT e perfil calibrado

- Corrigido bitmask de visibilidade; sonda SAT submetida opt-in mede count/pixels e falha fechada em cadeia invalida. Duas capturas 255/241, convergencia 45/36, quinze cadeias iguais, oito casos de handoff.
- Tentativas de tile direto rejeitadas e fonte restaurada por hash; sem mudanca de pixels ou coreografia. Captura AV e laudo local em `out/reviews/splash_v3_convergence_cost_20261016/review_summary.json`. Baseline, template e FORJA V2 preservados. Status WIP, sem aceite visual/sonoro ou 60 fps.

## 2026-10-16 — contorno no fade e cadencia visivel

- Corrigida paleta enfileirada sobrescrita pelo fade: tres indices de contorno efetivamente azuis na CRAM. Fonte de48 cores, PAL3 sem dono visivel no fade.
- Selecionada O `04f24e1cd52f227c5e01547f2d30b9b915b45fde84a197873687243d5ef35c90`: dois traces242/241,216 quadros visiveis216/216, todos os estados SAT cobertos, pico13/104, oito casos de handoff,150 medicoes e SRAM final coerente. Assets/coreografia mantidos.
- Pool8/atualizacao, fundo4 linhas/atualizacao, mapas logo RAM e setters guardados. P sem ganho rejeitada, fonte O restaurada. `out/reviews/splash_v3_visible_deadline_20261016/review_summary.json`. Status WIP; sem promocao/arquivo ou aceite visual/sonoro.
