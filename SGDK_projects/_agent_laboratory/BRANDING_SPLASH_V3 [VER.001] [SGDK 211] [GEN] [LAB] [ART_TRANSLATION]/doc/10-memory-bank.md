# Registro de pausa - 2026-10-24

**BRANDING-001 pendente por solicitacao humana.** Registrar e preservar em
commit/PR de rascunho para retomar depois; sem nova implementacao nesta rodada.
Owner: este laboratorio. Fonte atual inclui Q (limpeza enfileirada) e R
(blackout do menu), enquanto entradas historicas abaixo ainda selecionam O.

- Ler `doc/pending/branding_v3_resume_20261024.md` antes de retomar: confusoes de
  direcao, laboratorio/template, identidades, instrumentos e escopos de prova.
- Baseline local: `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`.
- Q: `eba5b0451246dc84d620746ab79aadc311ac200eeccc705891cb173e6596b632`.
  Dois registros historicos de241/241 VBlanks/updates; provas completas em Q
  nao sao automaticamente provas de R.
- Ultima candidata R: `8900504ca480cbddc7aa0c01351ff82c2638476eb5fce2ec1402e906a3d1ae7d`.
  Build e verificacao pontual de blackout registrados; validacao integral aberta.
- `doc/pending/branding_v3_checkpoint_20261024.json` fixa caminhos, hashes, flags,
  fontes e dependencias da preservacao. ROMs/capturas ficam locais em `out/`;
  nao estao neste checkpoint Git. Conferencia de hash nao recertifica runtime.
- Particulas e contorno aguardam aceite humano; musica continua em
  desenvolvimento para revisao futura. Menu ainda depende da arte/BGM V2.
- Nao arquivar FORJA V2, promover template, migrar consumidores ou canonizar
  skills como parte desta pausa. Contexto permanece `technical_demo` WIP.

O bloco gerado e as entradas datadas abaixo sao historicos da baseline e das
rodadas anteriores; nao representam uma unica ROM atual aprovada.

<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-10-15T22:20:10.8311890-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 22
- Ultimo build versionado: build_v002
- ROM vigente: `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2` (`393216` bytes)
- Validation summary: errors=3 warnings=20
- Blockers vigentes: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_stale, changelog_missing, emulator_evidence_stale, code_loaded_tiles_unmeasured, scene_tilemap_conversion_report_missing, tilemap_flag_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, project_documentation_sync_stale, scene_closeout_gate_stale, report_rom_identity_mismatch, report_status_conflict
- Evidencia de emulador: rom_identity_mismatch
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=nao_testado performance=unproven audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - BRANDING_SPLASH_V3 [VER.001] [SGDK 211] [GEN] [LAB] [ART_TRANSLATION]

## Atualizacao 2026-10-16 — contorno corrigido e todos os atos visiveis no prazo

- Auditorias de contexto/metodologia/higiene passaram com zero blockers. Learning Capture/Audit:9 licoes locais e5 candidatos, sem promocao canonica. Preload confirmado por RAM:64 atores em F7,10 linhas de cache em F10,28 linhas BG_B em F20 e paletas pretas antes de F24.

- Candidata tecnica selecionada O: `out/profiling/splash_v3_visible_deadline_v015_20261016/rom.bin`, SHA `04f24e1cd52f227c5e01547f2d30b9b915b45fde84a197873687243d5ef35c90`, 524288 bytes. Todos os inputs compilados conferem com a fonte atual. Baseline `out/rom.bin` continua `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`; template e FORJA V2 intocados.
- Duas sequencias identicas: 242 VBlanks/241 updates. Todos os 216 quadros visiveis F24-F239 usam um VBlank por update; F0 preto ainda usa dois. Convergencia passou de45/36 em G para36/36. Nao declarar60fps integral de boot nem FPS real do host.
- Hardware: todos os216 estados visiveis cobertos em dez boots privados por lotes, cadeias SAT submetidas iguais a VRAM, pico13 sprites/104px por linha H40, zero excedentes. Sonda pos-aquecimento:150 medicoes, CPU max91, zero acima do limiar, zero SAT invalida. Oito casos de handoff passaram. Sao provas distintas, sem fundir suas fases.
- Corrigida causa real do contorno: a escrita de tres cores era enfileirada, mas `PAL_fadeOut` lia a CRAM antiga e sobrescrevia o reforco. Fonte explicita de48 cores inclui os indices17-19. CRAM F210 mudou de[0,0,0] para[2048,3104,3648]; F230 ainda[512,1024,1056], F239 preto intencional. As outras45 cores usadas mantem os valores do controle nos snapshots. PAL3 nao tem dono visivel nos30 estados de fade e fica fora dele.
- Mantidos64 objetos, todas as6324 coordenadas compiladas, seis caminhos de vento e os assets. Melhorias: posicao manual guardada, tile manual guardado/inlining, faixa exata da sonda, mapas de logo preparados em RAM, pool em lotes de8 e fundo em7 lotes de4 linhas durante o preto. Primeiro export SRAM vai paraF120, depoisF180 eF239;150 medicoes retidas e64 palavras MDRT iguais a RAM. `SRAM_writeWord` reduziu o bloco final de486206 para312053 MCLK. O ensaio P de adiar o primeiro load nao ganhou cadencia e foi retirado, restaurando a fonte O por SHA.
- Video14s, WAV39,21s e SRAM flush em `out/evidence/splash_v3_visible_deadline_v015_20261016/flatpak_sessions/sess-20261016T214645-93bd29a3/`. Screenshot e contato amostrado vistos; sem playback integral, escuta ou aceite humano. Screenshot nativo take07 ficou preto e nao sustenta claim visual. Coleta longa inicial interrompida com28 dumps foi rejeitada; substituta limita24 estados por script e verifica cobertura completa.
- Laudo: `out/reviews/splash_v3_visible_deadline_20261016/review_summary.json`. Ainda abertos: F0, gate canonico/pin, validacao generica da baseline, fechamento integral VDP/DMA/DAC, qualidade visual humana e musica em desenvolvimento para revisao futura. Remover dependencias V2 do menu antes de propor arquivo/promocao. Deficiencias de direcao anteriores e a nova falha de ownership de CRAM ficam na curadoria local, sem promover skill compartilhada.

## Atualizacao 2026-10-16 — sonda SAT corrigida e custo medido

- Candidato tecnico selecionado: `out/profiling/splash_v3_sat_pressure_v007r2_20261016/rom.bin`, SHA `8aed3920593594b56b9bf4acc62699ff21c9082baeead6e1a13d2642764cd9d7`, 524288 bytes. Fonte compilada e baseline conferidas por hash; nenhuma mudanca em PNG, trajetoria ou densidade nesta rodada.
- A sonda antiga comparava o bitmask `Sprite.visibility` com o enum `HIDDEN=1`, contando particulas ocultas. Fallback corrigido para zero; variante opt-in agora mede a cadeia SAT submetida, conta sprites e pixels por linha e rejeita cadeia invalida com sentinel/contador distinto. 1024 fixtures x3 com sanitizers; 15 cadeias reais iguais a VRAM, 12 amostras pos-aquecimento de largura corretas e zero invalidas. O pico ativo F109 continua 13/104 nesta candidata; nao altera o historico r1 de 22/20.
- Duas capturas repetiram exatamente 255 VBlanks/241 updates, contra 278 na candidata anterior. Convergencia caiu de 66 para 45 VBlanks/36 updates; expansao 60/60 e sweep 30/30. Ainda nao sustenta 60 fps. Perfil usa `cycle` do debugger oficial, calibrado em cinco quadros VDP; mediana do bloco da sonda caiu de 520835 para 261842 MCLK (inclui overhead/interrupts).
- Troca direta de atributo de tile foi rejeitada: 7680 casos de equivalencia passaram, mas r1 custou 276 VBlanks por perda de inlining; r2 recuperou 255, sem ganho. Fonte exata da candidata G restaurada, snapshots e provas negativas preservados. Build inicial da sonda falhou no link; r2 corrigiu, sem ocultar a tentativa.
- Oito casos de handoff passaram na nova ROM. Video 14 s, WAV 39,34 s e SRAM flush em `out/evidence/splash_v3_sat_pressure_v007r2_20261016/flatpak_sessions/sess-20261016T184130-0e8d6227/`. Audio/video tem inicios independentes. Contatos de frames foram vistos; sem escuta, playback integral ou aceite artistico. Deficiencia anterior da direcao de cena continua registrada para curadoria; nao vira sucesso por medicao geometrica.
- Registro consolidado: `out/reviews/splash_v3_convergence_cost_20261016/review_summary.json`; sete eixos WIP em `out/logs/evidence_closeout_report.json`. Proximo: custo das trocas sincronizadas, reveal do mapa e primeiro export SRAM. Gate canonico, budget integral, revisao humana e dependencias V2 do menu continuam abertos. Audio segue em desenvolvimento para aprimoramento futuro, conforme decisao do usuario. Sem arquivo V2 ou promocao do template.

## Atualizacao 2026-10-16 — handoff observado e coreografia mais barata

- Auditorias de implementacao passaram: contexto, metodologia, higiene e proveniencia 28/28 (zero blockers/avisos). Simulador/coletor nativo selecionados: 2/2 self-checks. Learning Capture/Audit: 6 licoes locais, zero promocao canonica. Freshness: warning com 7 reports stale, zero required ausentes e zero erros. `out/logs/evidence_closeout_report.json` vincula o candidato selecionado aos seus claims, limites e sete eixos ainda WIP.

- Ultimo candidato tecnico selecionado: `out/profiling/splash_v3_stable_geometry_v005_20261016/rom.bin`, SHA `7407e48ee36f0f060c41761cd84aa6f1e0742069abef38f6fcaf462adfaf335f`, 524288 bytes. Flags de handoff, V019, LUT e geometria fixa; sonda completa ativa. E opt-in, sem trocar a baseline. As notas abaixo sobre LUT isolada sao historico do passo anterior.
- Geometria fixa usa guarda positiva nos oito frames compilados e fallback SGDK. Nove cadeias SAT fisicas identicas a LUT sem a especializacao. Duas capturas repetiram a mesma sequencia: 278 VBlanks/241 updates; expansao 60/60 e sweep 30/30. Convergencia ainda 66/36. O cache de visibilidade nao trouxe ganho e foi retirado, restaurando o SHA exato da fonte deste build.
- Oito casos de handoff passaram na ROM selecionada. AV em `out/evidence/splash_v3_stable_geometry_v005_20261016/flatpak_sessions/sess-20261016T175910-58afe69b/` inclui video, WAV e SRAM com fechamento gracioso. Audio/visual nao aprovados e gate canonico aberto. Matriz de custo, tentativas rejeitadas e proximo teste discriminante: `out/reviews/splash_v3_handoff_motion_20261016/cpu_frame_budget_report.json`.
- Proxima acao tecnica: perfilar F90-F119 com custo do observador separado. A ROM diagnostica sem tick caiu para 258 VBlanks, mas ainda perdeu deadlines; nao a promover nem ler sua telemetria ausente como zero. O menu tambem ainda depende de arte/BGM V2, a remover antes de propor arquivo/template.

- Mutex corrigido para liberar input somente depois da entrada do menu, fade inativo e fila DMA vazia. Contador de HUD de 12 quadros deixou de controlar prontidao. Oito casos funcionais com B/START observados por RAM da ROM: `out/evidence/splash_v3_motion_lut_v002_20261016/native_handoff_01/handoff_observation.json`.
- Candidata opt-in LUT `4096089a3c868ac8342ccfa8029769e30266af1e496d5391e2818ef269031396`, 524288 bytes. Todos os 6.324 pares de coordenadas compiladas coincidem com a referencia C. Flags: `SPLASH_V3_MENU_HANDOFF`, `SPLASH_V3_BACKDROP_V019`, `SPLASH_V3_MOTION_LUT`. Assets e coreografia visual conservados.
- Cadencia emulada: 241 intervalos em 345 VBlanks antes, 282 com LUT. Sweep de 30 updates caiu de 58 para 30 VBlanks; convergencia ainda excede o quadro. A tentativa de varredura linear da sonda nao mudou a cadencia, foi rejeitada e a fonte da sonda foi restaurada. Sem claim de 60 fps sustentados.
- Captura Flatpak da candidata de handoff inicial `80521392fe7736dd867195e68aa184b6934075dde6d8a6f21153fac6764885ae` mostra menu/splash/menu/demo e inclui audio em disco, video e SRAM no projeto. Bundle: `out/evidence/splash_v3_handoff_readiness_v001_20261016/flatpak_sessions/sess-20261016T172035-299904fe/`. Inicios de audio/video nao alinhados; sem escuta humana ou gate final.
- Contrato v005 corrigiu dois handles Y divergentes no contrato offline anterior. Medida exata reconciliada: 22,09 px, nao 23,54 px; 154 posicoes ativas comparadas com as funcoes C. Referencias: `doc/curation/splash_v3_wind_dispersal_contract_v005_20261016.json` e `out/logs/splash_v3_wind_dispersal_scanline_v005_20261016.json`.
- Continuidade: isolar custo do tick da sonda, manter comparacao emulada e leitura de performance separadas, revisar AV da candidata final e eliminar dependencias V2 do menu antes de propor arquivo/template. Aprovacao estetica e sonora continua aberta. `out/rom.bin` baseline `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2` preservada.

## Atualizacao 2026-10-15 — dispersao v004 e contorno do wordmark

- Feedback novo do usuário sobre v003: as fagulhas ainda se agrupavam; pediu três ou mais velocidades alternadas, duas mudanças de posição não uniformes e contorno de SGDK legível depois que o azul escurece.
- Implementado em `scene_branding_v3.c`: seis caminhos individuais, três bandas médias de velocidade (lenta 5,83/6,15; média 8,19; rápida 12,09/12,64/14,38 px/quadro) e vento de amplitude 2 px em `spark_2`/`spark_4`, com fases distintas. No F210, o código realça três índices existentes do contorno PAL1; não houve mudança nos assets.
- Contrato `doc/curation/splash_v3_wind_dispersal_contract_v004_20261015.json`; medição local dos 30 frames F180-F209: distância mínima 23,54 px em F192, nenhum par abaixo de 16 px, máximo 2 sprites/16 pixels por scanline e 12 links. São métricas apenas da geometria do sweep.
- Build candidato isolado v004: 524288 bytes, SHA-256 `c06e20c46c7eb211f5300ed1919f38192cc9d76425605987d31b22f699f8cc1f`. Captura visível no BlastEm: `out/evidence/splash_v3_wind_dispersal_preview_v004_20261015/local_blastem_x11/wind_dispersal_runtime_v004.mp4`; bundle vinculado ao hash no relatório de runtime da mesma pasta.
- Estado continua WIP e aguardando aceite humano. A ROM baseline `out/rom.bin` permanece `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`; V3 não foi promovida ao template e FORJA V2 não foi arquivada. Revisão sonora, FPS sustentado e budget total permanecem abertos.

## Atualizacao 2026-10-15 — rejeição humana e rework do sweep

- O usuário rejeitou explicitamente o preview ROM SHA `9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006`: a passagem ficou monótona e não carregou a animação/energia pedida. A avaliação anterior que a chamava de “promissora” foi retirada como conclusão artística; o contrato, report e capturas antigos continuam preservados como histórico rejeitado.
- A falha de direção de cena está registrada: a primeira entrega variou posições, mas omitiu o ciclo de vida visual de cada fagulha, o rastro orientado pela trajetória, pulsação assíncrona, dissipação e um piso de aceitação. A lição e a deficiência do handoff para `cutscene-cinematic-direction` estão em `doc/agent_learning/` e no contrato novo; skill compartilhada não foi modificada.
- Rework implementado: seis fagulhas com Bézier/easing, variação determinística de vento de até 1px, gravidade pesada removida, nascimento de quatro quadros, fase ativa com flicker individual em parte das instâncias, seis rastros direcionais opcionais e resfriamento por redução de cobertura. Contrato: `doc/curation/splash_v3_wind_lifecycle_motion_contract_v002_20261015.json`.
- Geometria do beat isolado medida em 30 quadros: máximo de 12 links visíveis no quadro, 10 sprites/80 pixels por scanline H40 em F202-F204 e zero excedentes. Report `out/logs/splash_v3_wind_lifecycle_scanline_v002_20261015.json`; isso não prova leitura visual nem budget global.
- Build isolado v003: ROM de 524288 bytes, SHA-256 `558fee0aabbee64ea98582a47fd9284866c649f02f2add179b6d0085a9e151ae`; report `out/logs/splash_v3_wind_lifecycle_build_v003_20261015/linux_wine_build_report.json`. BlastEm capturou 5,53 s diretamente da janela em `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/wind_lifecycle_runtime_review_v003.mp4`; contato em `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/runtime_contact_sheet.png`. A sequência mostra o lockup e as fagulhas em movimento. A captura é suplementar, sem marcadores ROM-side; não fecha FPS sustentado, áudio, budget VDP integral nem aceitação estética. Baseline V017 em `out/rom.bin` preservada; V3 continua em desenvolvimento, sem promoção do template nem arquivamento FORJA V2.
- O heading da cena foi alinhado ao parser: `scene_contract_compiler` agora extrai uma cena, com lint lab sem erros/warnings; `SC090` informativo mantém boot determinístico ignorado no modo de laboratório. A validação geral atual reporta 3 erros/20 avisos: VDP code-loaded tiles sem prova completa, incompatibilidade dos reports com a ROM baseline e conflito de status. Contexto, metodologia e higiene passaram. Report: `out/logs/validation_report.json`.

## Atualizacao 2026-10-15 09:32Z — reconciliacao F109 e otimização de convergencia

- O pico r1 de 22/20 sprites em F109 continua acima do teto H40. A revisão SAT exata encontrou 22 células cruzando a linha raster 99; as células 61 e 63 ficam além do limite. Uma delas contribui somente um texel opaco na linha e a outra está transparente; o pixel excedente não aparece no screenshot. Isso sustenta a tolerância visual WIP relatada pelo usuário, sem transformar 22 em budget aprovado. Evidência e hash das ROMs naturais/diagnósticas estão no registro de curadoria atualizado.
- O candidato r2 isolado é a ROM de 524288 bytes SHA-256 0bfcb0e1d896d51fdb273a3d033b3d6f8235939beaeed011df6d076985029caa. Em F109 local mediu 13 sprites/104 pixels; a captura de quadro está em out/evidence/splash_v3_frame_cache_scene_frame_search_20261015/frame_220/.
- src/scenes/scene_branding_v3.c usa uma tabela de pesos de convergência Q16 e guarda a posição inicial de cada partícula uma vez. A comparação offline dos passos 1–35 preserva as coordenadas inteiras da curva anterior. sParticleFrameIndex evita reemitir seleção de quadro quando ela não muda e é reiniciado para 0xFF quando o pool é criado. Revisão de código: out/reviews/splash_v3_frame_cache_h40_review_20261015/code_review_report.json.
- O snapshot suplementar do candidato no frame externo 540 contém 318 amostras pós-aquecimento, 34 sobre o limiar de CPU e pico 189; áudio dummy e duração parcial impedem qualquer claim de 60 fps sustentados.
- Corrigida a interpretação do diagnóstico de DMA: 5832 bytes representam soma da fila e 5760 a maior operação individual. A rotina compartilhada compara a soma com o campo de maior operação como se fosse capacidade; no SGDK 2.11 a capacidade configurada NTSC é 7200 bytes. Não há excedente provado por essa comparação, mas VBlank físico e duração de conclusão continuam sem medição. Wrapper compartilhado não foi alterado.
- A ROM baseline V017 em out/rom.bin permanece SHA-256 5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2. Nenhuma promoção, aprovação final, substituição de template ou arquivamento da FORJA V2.

## Atualizacao 2026-10-15 04:02Z — preview visual V018 em ROM

- V017 foi mantida como controle negativo: o conceito ainda formava uma faixa horizontal e a tradução usava 1104/1120 tiles H/V. V018 traz facetas amplas, clusters assimétricos e uma prateleira inferior interrompida; a imagem 320x224 usa 14 cores, 909 tiles exatos / 901 com flips H/V. Na máscara WIP do lettering, 3,07% dos pixels de fundo excedem luma diagnóstica 32. O limiar não aprova legibilidade nem a tipografia.
- ROM opt-in V018: 524288 bytes, SHA-256 `a94700a7a79b5fb6ffb074402909e2f7c2f0ddc89a790b05ac143e89edfeb493`; run `out/work_runs/splash_v3_v018_visual_preview_retry_20261015/run.json`. Bundle experimental BlastEm 1.0.0, sessão `blastem-linux-20261015T040001Z-v018`, ROM e screenshot ligados ao hash; janela MDRT/VLAB 1200/1200 completa. Screenshot SHA-256 `ece64b486de3b46fb2a7c4867c9a34d68b1b85c8d5710d9b8bab25e3b648808f` em `out/evidence/splash_v3_v018_visual_preview_retry_20261015/blastem-linux-20261015T040001Z-v018/`.
- O still em execução mantém SGDK/FORGE e `A: REVER` legíveis; a faixa inferior já não domina como linha contínua. Revisão em 320x224/CRT/overscan, interação animada das partículas, sweep, densidade das bordas e julgamento visual humano continuam necessários. V018 é placeholder, não arte aprovada.
- A ROM V018 usa anchors r2: 14 sprites e 112 pixels no pico scanline H40, zero quadros acima dos limites medidos pela probe. O r1 de F109 (22/20, 176/320, 2/1200) permanece uma tolerância visual WIP separada; a probe não confirma emissão das 22 entradas pela SAT/VDP. O limite H40 segue 20.
- Relatório estático ligado ao hash V018 fecha os intervalos compilados: backdrop 901 + wordmark SGDK 141 + FORGE 91 + partículas 8 = 1141 tiles/36512 bytes. O espaço seguro de tiles do usuário tem 1408 tiles antes da reserva automática SGDK; restam 267. BG_B/BG_A, janela, HScroll e SAT usam as bases H40 esperadas. `out/logs/splash_v3_v018_vram_static_allocation_20261015.json`; a medição não substitui `runtime_vram_load_ranges`, dump integral nem DMA/VBlank de runtime.
- Desempenho e som não foram aprovados: 37/1200 quadros acima do budget de CPU, máximo 396; FPS sustentado não medido; captura usou áudio dummy. O `validate_resources.ps1` terminou com 3 erros e 19 avisos, incluindo tiles carregados por C/VDP ainda sem medição e reconciliação canônica apontando para ROM/reportes antigos.
- `freshness_audit.ps1` terminou em warning com 5 relatórios stale (`scene_contract_compile`, `res_graph`, `emulator_session`, `audio_validation`, `build_output`), 0 obrigatórios ausentes e 0 erros. Metodologia/higiene passaram; `workflow_layout.py` passou e `audit_project_learning.ps1 -Mode Capture` encontrou 0 lições qualificadas. Os reports estão em `out/logs/`.
- V006 segue default e `out/rom.bin` segue V017, SHA `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`. Estado do usuário continua `em_desenvolvimento`, revisão futura obrigatória; sem aprovação final, promoção do template ou arquivamento da FORJA V2.

## Atualizacao 2026-10-15 — preview visual V016 e leitura do pico H40

- V016 é uma tradução WIP derivada da fonte V015: a transição oval suaviza a borda do campo escuro, mas a diferença para V015 é sutil (1,37/255 de diferença média por canal). São 652 tiles H/V únicos; V015 usa 708. O screenshot do preview mostra o campo central ainda marcado, então manter ambas como comparação sem seleção final.
- ROM opt-in V016 SHA-256 `64d333bf4ec246bbf67c4d947ebae25f33fa5e7eed99e942c9c174d57f98a532`; screenshot SHA-256 `a6b31554cf2e9d723f657efbd1aa5ec86d76516d39b3731f972a2e7f9fb13596`; bundle em `out/evidence/splash_v3_v016_visual_preview_20261015/blastem-linux-20261015T033848Z-v016/`. Captura selada na rota experimental BlastEm 1.0.0, 1200/1200 quadros. V006 e ROM V017 padrão `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2` continuam inalteradas.
- Runtime V016: máximo 14 sprites/linha, 112/320 px; 37/1200 quadros excederam o budget de CPU, pico 396 e 61,1 fps instantâneos. Áudio dummy; 60 fps sustentados, review sonoro e qualidade visual final permanecem abertos.
- Resposta curatorial ao F109: o veto visual automático seria conservador demais, mas o teto técnico não é uma margem de segurança: H40 continua em 20 sprites/linha. As 22 entradas SGDK foram medidas em 2/1200 quadros naturais, 176/320 px. A medição conta caixas que cruzam Y e não lê a SAT final; o screenshot aparentemente intacto autoriza tolerância WIP, não aprovação de budget nem prova de que todos os sprites foram emitidos. r2 segue como default até revisão.
- O preview helper canônico ainda aponta para BlastEm 0.6.2 e retornou 404; a captura direta instalada 1.0.0 foi selada como rota experimental, não como gate final. Splash V3 segue `em_desenvolvimento`; sem aprovação, promoção do template ou arquivo da FORJA V2.

## Atualizacao 2026-10-15 03:15Z — conceito visual V015 registrado

- Criado o conceito V015 de fundo cristalino, 1500x1049 RGB, SHA-256 `87293cf5275564733d27d5a166f1071f04bb2b447257a07c5a3f0c6b9c0c9188`. A composição reforça a assimetria: cluster alto à esquerda, topo direito mais leve e massa direita deslocada para baixo; o reflexo horizontal inferior foi reduzido, mas continua visível.
- A referência de geração foi copiada para `rascunho/entrada_visual/visual_generation_input_v015_20261015.png`, SHA-256 `8f74eaaa903e365c3621963d556800bf43d1e350777d2a57c5a3f0c6b9c0c9188`. Prompt, hashes e limites estão no sidecar e inventário V015.
- O workset aponta para V015 como fonte elegível de tradução; `doc/artifact_registry.json` a indexa como `candidate`, com `approved=null`. O gate `art_gameplay_direction_gate_v015.json` mantém produção, promoção a `/res` e AAA bloqueadas.
- A alfabetização semântica manual a classifica como uma única placa BG_B. A heurística `infer_source_structure.py` retornou `stage_board` com falso preview/recorte de céu/solo; a divergência foi preservada como blocker de revisão, sem usar essa decomposição como base de pixels.
- Ainda é concept art high-res, não pixel art Mega Drive: não foi inserida em `/res`, na ROM ou na timeline. Faltam parsing semântico, variantes `basic`/`elite`, reautoria manual em grid 8x8, medidas de paleta/tile e revisão nativa 320x224/ROM. V006 e a ROM V017 permanecem inalteradas.
- Splash V3 continua `em_desenvolvimento`; escuta humana V016 e gates finais seguem pendentes. A tolerância visual do usuário a 22/20 em F109 segue separada do teto H40; não houve aprovação de budget, arte, áudio, template ou arquivamento da FORJA V2.

## Atualizacao 2026-10-15 03:01Z — escuta direta V016 em duas passagens

- A candidata V016/VGM4 foi buildada em ROM de preview isolada e executada no BlastEm Flatpak 1.0.0. A ROM de escuta tem SHA-256 `35af30bb5b0cfe52fb527858b9cd164ed496ee46f144e2396fd151841fb16e71`; `out/rom.bin` V017 permaneceu intacta (`5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`).
- A captura vinculada mostra a timeline P1/P2 e o monitor XGM2 `358/358 DROP:0`. Os WAVs stereo/mono de 8 s derivam do audio direto dessa ROM e incluem as duas passagens. Proveniencia, hashes e limites estao em `out/audio/reviews/v009_v016_two_cycle_rom_capture_20261015/splash_v3_v016_two_cycle_rom_review.json`; run e screenshot em `out/work_runs/splash_v3_v016_rom_two_cycle_capture_20261015/run.json` e `out/evidence/splash_v3_v016_rom_two_cycle_capture_20261015/`.
- A captura e experimental e sem selo canonico; nao prova musica aprovada, budget DAC ou performance sustentada. Uma segunda build compilou a etiqueta de conclusao em area visivel, mas a recaptura encontrou falha GTK/Zenity e nao gerou evidencia valida. O primeiro WAV continua valido para escuta porque a segunda mudanca alterou somente texto do preview, nao musica, cues ou timing.
- `freshness_audit.ps1` segue em warning com 5 artefatos stale (contrato de cena, grafo de recursos, sessao de emulador, validacao de audio e build), zero ausentes obrigatorios e zero erros. `audit_project_learning.ps1 -Mode Capture` nao encontrou licoes qualificadas; nenhuma promocao canonica ocorreu.
- O usuario ja considerou 22/20 em F109 visualmente aceitavel; manter essa tolerancia WIP separada do limite H40. r2 em 13/20 continua default. O estado geral permanece `em_desenvolvimento`, sem aprovacao final, promocao de template ou arquivo da FORJA V2.


## Atualizacao 2026-10-15 02:41Z — escuta V016 em duas passagens preparada

- A faixa candidata continua V016/VGM4; nenhum patch/score/runtime foi alterado. Foram gerados WAVs de escuta de 6 s: ciclo capturado de 3 s repetido duas vezes, em stereo e fold-down mono, sem processamento adicional. O WAV de origem tinha somente o passa-altas de 20 Hz previamente aplicado.
- Origem: captura BlastEm da ROM V012; VGM4/cues/`audio.c` coincidem por hash com V017, mas o sample nao veio do binario atual. A segunda passagem e duplicacao offline e nao prova replay/loop integrado.
- Artefatos: `out/audio/reviews/v008_v016_two_cycle_20261014/`; run pai ligado ao preview V014 em `out/work_runs/splash_v3_v016_two_cycle_audio_review_20261014/run.json`. Escuta humana ainda pendente, assim como captura direta de dois ciclos, budget DAC e desempenho sustentado.
- Status permanece `em_desenvolvimento`; sem aprovacao musical, promocao ao template ou arquivamento da FORJA V2.


## Atualizacao 2026-10-14 22:09Z — V014 buildada e observada

- A primeira tentativa isolada parou em Java2D/X11 sem display; o wrapper Linux/Wine passou a iniciar ResComp em modo headless. A retry compilou V014: 393216 bytes, ROM SHA-256 `cd3946fcd7de61709b590f77fec16f0066e3e30b3fe283fd5dad0f20a72cba5c`, flags de preview visual + fundo V014. O build ficou isolado; `out/rom.bin` V017 continuou com SHA `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`.
- BlastEm native 1.0.0 diagnostico capturou frame 700 do hold final: SGDK, FORGE e `A: REVER` legiveis. Screenshot 640x480 ligado ao hash da V014, mas rota nao selada, audio dummy e sem ciclo/frame markers. Nao declarar `testado_em_emulador`, FPS estavel ou aprovacao humana por esta captura.
- Residency de assets foi medida em 1096/1740 tiles (63%, margem 37%) para V014 + lockup B WIP + particulas. V014 responde por 856 tiles H/V de 1120 brutos, com warning de baixa deduplicacao. Proveniencia: 24 simbolos, zero blockers/warnings. Isso ainda nao e ResGraph, VRAM total ou budget fechado.
- V014 continua candidata visual WIP nao selecionada, nota automatica 0.6847 `needs_review`; revisar safe area, ruido de borda, CRT/overscan e sequencia frame-marked. Audio nao foi avaliado. Nenhum asset baseline, template ou FORJA V2 foi substituido.
- Curadoria do pico r1: reprovar a direcao visual automaticamente por F109 seria conservador demais. O usuario tolera visualmente o efeito; 22/20 continua excedente tecnico em 2/1200 quadros, e a probe nao prova que todas as celulas foram emitidas. r2 (13/20) permanece default; status de budget segue nao aprovado.

**Ultima atualizacao:** 2026-10-15T03:05Z
**Fase atual:** Splash V3 em desenvolvimento com revisao futura obrigatoria. V017/V006 permanecem baseline; candidatos visuais e sonoros continuam WIP. A escuta direta V016 de duas passagens foi capturada em ROM isolada para revisao humana, ainda sem aprovacao. Registros em `out/work_runs/splash_v3_v016_rom_two_cycle_capture_20261015/`, `out/evidence/splash_v3_v016_rom_two_cycle_capture_20261015/` e `out/audio/reviews/v009_v016_two_cycle_rom_capture_20261015/`.
**Proxima fase:** ouvir a faixa V016 diretamente da ROM em stereo/mono; continuar curadoria visual nativa 320x224/CRT, lettering/model sheet, safe area, contraste, facetas e timing. Depois fechar VRAM/ResGraph/DMA/VBlank/CPU/DAC, replay ROM-side, captura frame-marked canonica e desempenho sustentado. Sem gates e aprovacao humana, nao arquivar FORJA V2 nem substituir o template.


## Registro historico 2026-10-14 21:24Z — estudo visual V013/V014

- V013 foi rejeitada como fonte candidata de runtime: no lockup 320x224, cristais competem com letras; 796 tiles unicos / 790 H/V.
- V014 amplia o campo escuro e melhora a hierarquia visual no painel comparativo, mas 870 tiles unicos / 856 H/V e visual score 0.6847 (needs_review) mantem custo e revisao em aberto. Estimativa de estado com V014: 1096/1740, nao medida por ResComp.
- V014 foi adicionado a res/ como placeholder opt-in; a baseline V017 e o default V006 nao mudaram. A fonte, o gate e o builder estao registrados; a ROM candidata isolada preserva V017.
- O excedente r1 de 22 sprites em F109 foi visualmente tolerado pelo usuario, mas budget H40 permanece excedido. r2 segue como default.

**Registro original:** 2026-10-14T21:24Z
**Fase registrada naquele ponto:** Splash V3 permanecia em desenvolvimento e exige revisao futura. V017 (5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2) e o fundo V006 seguem como baseline. O novo estudo visual V013/V014 permanece WIP: V013 foi mantido como controle; V014 esta em res/ apenas como placeholder opt-in para preview isolado, sem mudar a selecao default V006, e melhora a janela escura do lockup, mas mede 856 tiles unicos com flips e nota 0.6847 (needs_review). O estado completo V014 foi estimado em 1096/1740 tiles pela substituicao offline do V006, sem auditoria ResComp nem preview ROM. r1 continua visualmente toleravel em WIP, mas 22/20 em dois quadros permanece excedente H40; r2 de 13/20 continua default. V016/VGM4, lettering B, model sheet e aprovacoes finais visual/sonora seguem pendentes. Nenhuma alteracao no template ou FORJA V2.
**Proxima fase naquele ponto:** revisar o preview isolado V014 contra V006 e conferir leitura CRT/safe area; fechar tiles ResComp, VRAM, DMA, CPU/DAC e 60 fps sustentados. Manter input/replay ROM-side e escuta integrada de dois ciclos em aberto. Nenhuma promocao ao template ou arquivamento da FORJA V2 antes dos gates e revisao humana.

## Atualizacao 2026-10-14 20:40Z — lockup V012 e menu observado

- A correcao em `src/scenes/scene_menu.c` removeu a segunda linha fantasma: `VDP_drawText` recebe coordenadas em tiles, logo o antigo deslocamento `+1,+1` criava outra copia 8 px abaixo/direita. O helper agora desenha uma unica vez. Captura: `out/evidence/splash_v3_visual_v012_menu_fix_20261014/menu_capture_game_area.png`; ROM separada SHA `df699c1aa002b1758921833ae5ec7ae70bd900db7a5cbcd8e2d436307569c852`.
- Build diagnostico V012 em ROM isolada, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V012`: 393216 bytes, SHA `e37f5409e19eb1c626e7554875e2ae8fd2006917d451446b7cb03e4ebe916456`. A V017 em `out/rom.bin` permanece inalterada.
- A captura de hold mostra SGDK e FORGE claros, legiveis e com hierarquia; `A: REVER` tambem esta legivel. Os samples anteriores nao tinham marcador de frame e cairam em beats diferentes. A implementacao `PAL_initFade` copia a quantidade solicitada a partir do ponteiro, compativel com o subarray de cores SGDK; nao houve mudanca de paleta. Evidencia: `out/evidence/splash_v3_visual_v012_lockup_hold_retry_20261014/`.
- BlastEm Flatpak 1.0.0 em Xvfb privado, sessao `sess-20261014T203001-92381073`; preflight bridge+SDL passou e a sessao fechou graciosamente. A tentativa de seal ocorreu antes do shutdown; hashes de blastem.log/xvfb.log mudaram e .lock/.seq/.seq.lock nao foram copiados. O recibo fica sem selo efetivo. A versao instalada nao fecha o gate canonico pinned em 0.6.2. O titulo 60.3/60.8 fps e instantaneo, nao prova desempenho sustentado. Audio ficou em dummy e nao foi avaliado.
- O pico r1 nao veio do hold: a ROM natural registrou 22 celulas da lista SGDK em 2/1200 quadros e 176/320 px. A sonda ignora X, mas em F109 as particulas ficam em X=48..256, dentro da area; portanto nao ha inflacao por celulas fora da tela. Considerar esse efeito decorativo visualmente toleravel evita veto automatico excessivo; H40 continua excedido em 2 quadros e budget nao aprovado. A pergunta e a decisao estao registradas no relatorio de curadoria.
- Status segue `em_desenvolvimento`: preview V012 comparativo, sem aprovacao final de visual/audio, input ROM-side, budget total, template ou arquivamento FORJA V2.

## Atualizacao 2026-10-14 15:52 -03 — V016 pronta para primeira escuta

- Trecho WAV de 3,2 s e MP3 de conveniencia em `out/audio/reviews/v007_current_v16_audio_review_20261014/`; sidecar preserva a origem V012, hashes, corte 1,0–4,2 s, filtro 20 Hz e ausencia de normalizacao.
- A ROM da captura e V012, SHA `234f73abc68e94d9175fe2b4714bb5cd7d531904113f150bcd9c49751ff55eb7`. Os hashes de musica VGM4, cues e `audio.c` coincidem com V017; o recorte nao e prova de audio da ROM atual nem de aprovacao, loop, budget DAC ou performance.
- A auditoria encontrou e corrigiu o path/hash divergente de `mus_splash_v3` no manifesto. `validate_audio.ps1` passou com 12 declaracoes, zero issues e 59,11 KB estimados; a auditoria de proveniencia com `--verify-hashes` passou com 12 entradas, zero erros e zero avisos, registrada em `out/logs/audio_provenance_v016_report_20261014.json`.

## Atualizacao 2026-10-14 18:34Z — linhagem B e matriz de scanline

- `validate_visual_source_of_truth.ps1` passou sem findings. O gerador de anchors agora recria a mascara em memoria a partir do recorte B autorizado (source SHA `d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8`, crop `[401,362,1276,518]`), sem ler `/res`; os 64 anchors sao exatamente os mesmos do contrato r2 anterior. Nenhum pixel/runtime default mudou.
- Matriz completa com 990 entradas: 64x8x8 = 13 sprites/104 px no F106; 80x8x8 = 16/128 no F104, com os 80 links SAT ocupados; 48x16x16 = 19/304, perto dos dois limites; 64x16x16 e 80x16x16 excedem. Relatorio `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json`.
- Self-check do runner e do simulador canonico passou. O gate global continua bloqueado por `project_source_mirror_stale`; esta medicao e apenas geometria de scanline, sem budget VDP/DMA/CPU/ROM. A probe de runtime mede a lista SGDK de sprites, nao a SAT final nem pixels renderizados apos o limite.
- O feedback do usuario aceita F109 visualmente. Isso nao reprova a imagem por si so, mas os 22 objetos solicitados excedem o teto H40 de 20; r1 nao foi promovida a default e o budget segue nao aprovado.
- Contexto, metodologia e higiene passaram sem blockers. Freshness permanece em warning com 5 reports tecnicos stale (contrato de cena, grafo de recursos, sessao de emulador, audio e build), zero ausentes obrigatorios e zero erros; ver `out/logs/freshness_audit_report.json`.

## Atualizacao 2026-10-14 18:15Z — sequencia natural r1

- Build sem hold, anchors r1/V006: 393216 bytes, SHA-256 `559b9c1d22f6738748ceee3cddd7eeb66872c0ae1a586eaa6efbb3e140bafbca`. V017 continua sendo a ROM baseline do projeto.
- BlastEm Flatpak 1.0.0 em sessao privada; preflight bridge+SDL passou. O fim da sequencia mostra SGDK/FORGE e `A: REVER`. O titulo marcou 60.2 fps, snapshot instantaneo; FPS sustentado nao foi provado.
- MDRT/VLAB completou 1200/1200 quadros: max 22 sprites/linha em H40, pico no quadro global 110 (estado local F109), 2 quadros acima de 20, largura maxima 176/320 px, zero acima do limite horizontal. SRAM SHA-256 `a411834693616c8daed780adf62c22779fd7990be758ef0b036e3f811d3d7013`.
- Comparacao com o hold: a sessao held contou 1182/1200 por repetir o quadro; a sequencia natural confirma somente 2/1200. A geometria r1 acertou o pico, e o seu efeito visual nao deve ser automaticamente reprovado por esse excedente raro. O limite H40 de 20 continua; 22 nao passa budget e a probe nao prova que ambas as celulas extras foram exibidas.
- CPU max 399, 37 quadros acima do threshold. Performance sustentada, input/replay ROM-side, audio, arte final, model sheet, aprovacao humana e selo de entrega permanecem pendentes.
- Evidencia em `out/blastem_splash_v3_h40_r1_natural_20261014/`; report de build em `out/logs/splash_v3_h40_r1_natural_20261014/linux_wine_build_report.json`.

## Atualizacao 2026-10-14 18:06Z — ROM r1 F109 e telemetria H40

- Build isolado com `SPLASH_V3_PARTICLE_ANCHORS_R1` e `SPLASH_V3_H40_F109_HOLD`: 393216 bytes, SHA-256 `b8b27ca7317d092a00e5236cbe6b558e2089877f7f88825797c4c915854c6abd`. V017 em `out/rom.bin` permaneceu inalterada.
- BlastEm Flatpak 1.0.0 executou a ROM em Xvfb privado. A captura local F109 esta em `out/blastem_splash_v3_h40_r1_f109_20261014/splash_v3_h40_r1_f109.png`; duas capturas consecutivas sao identicas. A sessao fechou normalmente e o SRAM foi copiado junto com os metadados.
- MDRT/VLAB do mesmo SRAM/hash: H40 320x224; pico de 22 sprites/scanline no frame global 110, correspondente ao estado local F109; largura maxima 176/320 px; 0/1200 quadros acima do teto de largura; 1182/1200 acima do teto de contagem; 64 sprites ativos. A macro manteve F109 parado, portanto essas 1182 amostras nao medem a frequencia de overflow na coreografia normal. Performance sustentada permanece sem prova.
- Interpretacao: o pico de contagem nao e conservador; o runtime o confirmou. A imagem capturada nao mostra defeito visual evidente e o usuario ja relatou funcionamento perfeito, entao r1 segue candidata visualmente toleravel. Isso nao remove o limite fisico de 20 nem demonstra que as 22 celulas foram exibidas. Status de budget: excedente observado no preview de emulador, ainda nao aprovado.
- Evidencia: `out/blastem_splash_v3_h40_r1_f109_20261014/evidence_record.json`, `runtime_metrics.json`, `save.sram`, `capture_001.json`, screenshot full e recorte. Rota `isolated_session_experimental`, sem selo de entrega; gameplay completo, input, audio, FPS sustentado, arte final e model sheet seguem pendentes.

## Atualizacao 2026-10-14 17:38Z — preview V012 e telemetria H40

- Preview separado SGDK 2.11: 393216 bytes, SHA-256 `234f73abc68e94d9175fe2b4714bb5cd7d531904113f150bcd9c49751ff55eb7`, flags `SPLASH_V3_VISUAL_PREVIEW`/`SPLASH_V3_BACKDROP_V012`. `out/rom.bin` continua V017 e inalterada.
- BlastEm Flatpak 1.0.0, commit `b0e3d27d6993b84933aadd707535d752e955c668f2c9459d9b67519623bcd704`, rota `isolated_session_experimental`; bundle `sealed`, freshness `ok`, screenshot semantico `passed`. Artefatos em `out/blastem_splash_v3_visual_v012_preview_20261014/isolated_session/sess-20261014T173801-224faca3/`.
- MDRT/VLAB: 1200/1200 quadros, cena 0, maximo 14 sprites e 112 pixels por linha, zero quadros acima de 20 sprites ou 320 pixels. Esta ROM usa r2 e nao reproduz o pico geometrico r1 de 22 sprites; a tolerancia visual a overflow nao muda o limite H40.
- Max CPU 396, 37 quadros acima do budget; performance continua `unproven`. Titulos 60.0/59.8/58.0 fps sao amostras e nao provam estabilidade.
- A no P1/P2 teve ack de SDL, sem mudanca visivel nas capturas: recepcao ROM-side/replay nao confirmada. Audio stereo 12 s: sinal presente e sem clipping; qualidade continua aguardando escuta do usuario. Relatorio: `out/logs/splash_v3_v012_preview_capture_20261014.json`.

## 1. Estado operacional

- documentado: storyboard, concepcao, curadoria, model sheet WIP, contrato provisiorio de fonte visual, runtime decision log e evidencias de preview.
- implementado: sim, cena WIP de sete beats; quatro assets indexados placeholder; V016/VGM4 e quatro cues integrados.
- buildado: ROM V017 de 393216 bytes, SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`.
- preview em emulador: 16 amostras diagnosticas diretas de BlastEm local 1.0.0 mostram a sequencia e o lockup final; `out/logs/splash_v3_v017_visual_review_report_20261014.json`, status `preview_observed_unsealed`, sem frame markers nem confirmacao ROM-side do input.
- testado_em_emulador: nao; a captura canonica BlastEm nao foi selada.
- validado_budget: nao; scanline local e apenas geometria de sprites.
- audio: V016/VGM4 esta integrada ao V017 e ainda nao foi ouvida pelo usuario; V012 e referencia positiva; V013/V014 permanecem rejeitadas. A candidata atual nao tem aprovacao final.
- ready_for_aaa: false.

## 2. Bloqueios atuais

- Medicao global: bloqueada por `project_source_mirror_stale` em 20 espelhos `runtime_probe` de 11 projetos. Nenhuma copia externa foi alterada. Os self-checks globais passaram, mas isso nao libera a guarda.
- Contexto `technical_demo/implementation`, metodologia e higiene local passaram sem blockers; reports em `out/logs/project_context_report.json`, `out/logs/project_methodology_report.json` e `out/logs/project_hygiene_report.json`. Freshness: warning com 5 reports tecnicos stale, zero artefatos requeridos ausentes e zero erros; report em `out/logs/freshness_audit_report.json`.
- Auditorias de fase anteriores a B: preflight, contexto `technical_demo/implementation`, metodologia e linhagem visual passaram. `scene_closeout_gate` ficou em `warn`; `res_graph_audit` alerta `RG_CODETILE001`. `validate_resources.ps1` fechou com `closeout_gate=false`, 3 erros e 20 avisos antes da ativacao dos wordmarks B; o report geral nao foi atualizado depois da integracao WIP. Erros ja observados: arvore aninhada sem ownership, tiles carregados por codigo sem telemetria/dump e `claim_sources_missing`; ver `out/logs/validation_report.json` e `out/logs/scene_closeout_gate_report.json`.
- Scanline local: 64x8x8 chega a 13 sprites/104 pixels na linha F106, 64 links; 80x8x8 chega a 16/128 em F104 e usa os 80 links; sweep 7x8x8 chega a 1/8. Report atualizado `out/logs/splash_v3_scanline_glyph_anchor_v002_source_b_final_20261014.json`; gate global continua bloqueado por espelho stale.
- Assets WIP V006/B: backdrop 1120 raw/583 H/V tiles; SGDK 143 raw/141 H/V; FORGE 92/91; particle strip 8/8. Plano: 823 tiles H/V (26.336 bytes, 47,3% do teto de payload 1.740). Index 0, grid 8x8, 4bpp e papeis de paleta passaram no builder; nenhum pixel final ou model sheet aprovado.
- Curadoria visual: V006 permanece acima do vocabulario curatorial 20-40; o controle automatico de 40 tiles foi rejeitado por gerar padrao quadriculado. Revisar convergencia, cristais de borda, centro negativo, sobreposicoes, sweep, hierarquia/contraste, lettering/model sheet e prompt. A geracao de anchors foi corrigida para a fonte B autorizada e reproduz as coordenadas r2; os pixels e o runtime continuam WIP.
- Fonte visual: `doc/contracts/visual_source_of_truth_branding_splash_v3.json` esta travado apenas para direcao WIP. O scan de linhagem passou sem findings, mas nao aprova arte final.
- Captura: V017 tem 16 quadros por amostra de relogio de parede, contato mostra a sequencia e hold `A: REVER`; falta ciclo frame-accurate, trace de input ROM-side e captura canonica selada para este hash.
- Budgets pendentes: residency e VRAM completas, fila total de DMA/VBlank, custo CPU, DAC, audio e estabilidade sustentada. Codigo carrega em chunks de ate 180 tiles por imagem e quadros de particula; confirmar pior quadro e throughput em auditoria runtime.
- FORJA V2, ROM canonica V2, template e projetos consumidores continuam intactos.

## Preview executavel da baseline (2026-10-12)

- A ROM atual veio do despacho `SCENE_brandingV2*` em `src/core/app.c`; e a cena v2 herdada, nao a splash v3.
- `build_v001`: 262144 bytes, SHA-256 `51a34305826e4120afa3c6ec63b750bf83d47b3125d087d01c5f3516323ae3f9`; titulo do cabeçalho atualizado somente na copia do laboratorio para `A FORJA V2 LAB BASELINE`, removendo o placeholder que impedia a finalizacao.
- BlastEm Flatpak 1.0 abriu a ROM; a janela foi deixada aberta no menu, que oferece B para rever a marca. Captura dedicada: `out/blastem_preview/manual_preview_screenshot.png` (SHA-256 `0312bf877de2458be229ad990fba00bb3e6b308a4ef481878d1500c441f95b4d`).
- O titulo da janela mostrava 59.9 fps naquele instante; isso nao mede desempenho sustentado. A rota canonica tentou fixar BlastEm 0.6.2 e recebeu HTTP 404 antes de iniciar a captura; nao ha SRAM/VDP dump nem selo. Gameplay, audio e budget continuam sem validacao.

## Retomada da implementacao V3 (2026-10-12)

- O usuario autorizou implementar a splash V3 e, somente apos validacao completa, arquivar FORJA V2 e substituir a abertura do template. A classificacao continua `technical_demo`; `ready_for_aaa` permanece falso.
- O template segue intacto durante a fase de laboratorio. As migracoes dos cinco consumidores continuam fora do escopo sem aprovacao individual.
- A verificacao global atual passou 30/30 self-checks e segue bloqueada por 20 espelhos ativos `runtime_probe` desatualizados em 11 projetos; nenhum espelho foi alterado e nenhuma medicao V3 foi executada.
- A rota do master de lettering e a reconciliacao dos espelhos foram submetidas ao usuario; ate a resposta, apenas trabalho independente desses gates pode avancar.
- A direcao sonora foi reescrita para energia digital E Dorian, com ownership XGM2, mapa de quatro cues, mascaramento e loop de oito compassos 7/8 (840 quadros NTSC). Score FM/PSG e quatro cues PCM foram convertidos em candidatos `lab`; o estado posterior de integracao esta registrado abaixo.
- A ROM canonica observada continua sendo `build_v001`, a baseline V2. Nenhum pixel ou runtime V3 de producao foi produzido; existe uma ROM de probe de audio isolada, sem validacao auditiva ou QA canonico.
- Auditoria do SGDK 2.11 registrada em `out/logs/branding_v3_api_reality_check_20261012.json`: o engine moderno usa `SPR_addSpriteEx` com cinco argumentos; `SPR_initEx(16)` reserva 16 tiles, enquanto o pool fixo de sprites e de 80 objetos. O comentario incorreto no bootstrap foi corrigido; nenhum comportamento executavel mudou.
- O snapshot do gate visual agora aponta para o report de medicao de 2026-10-12; o bloqueio e o status permanecem os mesmos.
- A forma musical foi ajustada para 7/8 a 120 BPM: os 210 quadros entre o inicio da cama em F030 e o Exit em F240 fecham exatamente dois compassos. A trilha completa tem oito compassos (840 quadros); o score e a primeira renderizacao candidata vieram depois.
- Score autoral em `data/source_audio/splash_v3_music_score.json` e builder em `data/source_audio/build_splash_v3_music_vgm.py` geraram VGM NTSC de 840 quadros e conversao XGM2 tecnica. Hashes VGM/XGM2 e metadados estao em `out/audio/splash_v3_music.provenance.json` e `out/logs/splash_v3_music_conversion_20261012.json`.
- Quatro cues PCM candidatos foram gerados e convertidos a 13.3 kHz; todos passaram sem clipping e com payload alinhado a 256 bytes. O conjunto ocupa 24.320 bytes em payloads isolados; ver `out/logs/splash_v3_pcm_candidate_format_audit_20261012.json`. Nao ha auditoria ResComp, integracao, budget DAC ou escuta humana.
- Ownership, estimativa de DAC e findings de entrega estao em `out/logs/splash_v3_audio_channel_ownership_report_20261012.json`, `out/logs/splash_v3_dac_stream_budget_report_20261012.json` e `out/logs/splash_v3_audio_delivery_findings_20261012.json`; sao contratos e estimativas, nao observacao de runtime.
- A mix candidata agora libera o lead em F210 e sustenta a cauda PCM sobre E2/E3; score recompilado e XGM2 reexportado. Hashes atualizados no changelog e na linhagem.
- Auditoria estrutural do loop musical passou: 840 quadros totais e no loop, estado de canais silencioso na emenda estrutural; isso nao aprova a emenda audivel. A verificacao de integridade ligou 16 hashes de fontes/candidatos e conversoes em `out/logs/splash_v3_audio_artifact_integrity_20261012.json`.

## 2026-10-12 — integracao candidata e probe de audio V3

- `res/resources.res` declara `mus_splash_v3` e os quatro WAVs XGM2. ResComp compilou o conjunto em `out/tests/splash_v3_audio_integration_v001/rom.bin`; payload PCM total de 24.320 bytes. Esse primeiro build confirmou integracao de recursos, ainda sem despacho runtime.
- O subsistema `src/system/audio.c` ganhou ownership V3, cues PCM CH2/CH3 e fallbacks PSG nomeados. O preview compile-flag-only em `src/scenes/scene_branding_v3_audio_preview.c` agendou musica no quadro 30, cues nos quadros 24/118/178/210 e Exit no 240.
- Build V004 da ROM probe: 262.144 bytes, SHA-256 `847eb7b36e5d437420e9904edd35850f2e19a703a3c39b4a82478b69763f3e07`. BlastEm Flatpak 1.0 mostrou o ciclo completo e retorno de sucesso nas quatro chamadas PCM; report `out/logs/splash_v3_audio_probe_preview_20261012.json` e review `out/logs/splash_v3_audio_code_review_20261012.json`.
- Limite: nao houve escuta humana; V006 observou o driver reportar playback em 209/209 amostras de quadro 31 a 239, sem provar saida audivel ou qualidade da mix. A reentrada por A foi observada no probe, sem substituir QA da cena de producao. Continuam pendentes arte/model sheet aprovados, despacho na cena de producao, medicao de DAC/VDP e FPS sustentado, captura BlastEm canonica e QA final. Nenhum status de entrega ou promocao foi elevado.

## 2026-10-12 — monitor de playback e conceito de lettering

- ROM probe V006: 262.144 bytes, SHA-256 `cdbfd418794de57adb07e660d654fc50401a4a70151978396ba2ee1682be922e`. BlastEm Flatpak 1.0 mostrou `MUSIC 209/209 DROP:0`, quatro chamadas PCM com retorno de sucesso e reentrada por A; report em `out/logs/splash_v3_audio_probe_preview_20261012.json`.
- O monitor amostra `XGM2_isPlaying()` a cada quadro entre 31 e 239. Zero quedas observadas comprovam apenas o estado do driver, nao sinal audivel nem qualidade de mix. O usuario ainda precisa ouvir a ROM exata.
- Criado conceito transparente do lockup SGDK/FORGE via built-in ImageGen e copiado para `rascunho/entrada_bruta/branding_v3_lettering_master_ai_v001.png`; SHA-256 `f776eb032d64f2de310676694b1483c00f9a4d532617f81dd1e8f2737e68879a`. Report `out/logs/branding_v3_lettering_concept_review_20261012.json` marca `source_kind=ai_generated`, `acceptance_status=visual_lab_control`; nao e asset pixelado nem pode entrar em `/res`.
- Segundo estudo AI v002 e previews de placa em 320x224 foram comparados em `out/logs/branding_v3_lettering_concept_comparison_20261012.json`; os dois continuam `visual_lab_control`, com rota humana pendente, sem model sheet aprovado e sem fonte de producao. O report v001 foi corrigido: o master tem 16.654 valores RGB opacos distintos, nao tres regioes de cor plana.
- O manifesto de source continua `pending_human_choice`; sem model sheet, arte final, medicao VDP/DAC ou runtime de producao. Nenhuma promocao foi feita.

## 2026-10-12 — ROM de pre-escuta V009

- O cabeçalho da ROM usa `MG_ROM_HEADER_PATH` na montagem local, com fallback para `out/rom_head.bin`; isso corrigiu o caminho fixo que fazia builds isolados mostrarem o título da baseline.
- O probe define o foreground do texto em PAL1 index 15, corrigindo a captura vermelha anterior. V009 foi buildado pela rota Linux SGDK bridge e executado em BlastEm Flatpak 1.0 com o título `SGDK FORGE V3 AUDIO PREVIEW`.
- ROM: `out/tests/splash_v3_audio_probe_v009/rom.bin`, 262.144 bytes, SHA-256 `0b081c8d67e00e7bdb6e16187f3273a644e2f02c9d60451f1d67351a3abb693a`; screenshot: `out/blastem_audio_probe_v009/splash_v3_audio_probe_v009.png`, SHA-256 `c20d5ed178f8abe3bc8db818c296717dd44affdcd4d1c05c033cd5567c8ffddd`.
- Captura mostra `CYCLE DONE`, quatro cues `PCM` e `MUSIC 209/209 DROP:0`. O valor 59.8 fps no titulo e instantaneo, nao prova FPS sustentado; V009 ainda nao tem aprovacao auditiva ou captura canonica. `out/rom.bin` permanece a baseline V2 com SHA-256 `51a34305826e4120afa3c6ec63b750bf83d47b3125d087d01c5f3516323ae3f9`.

## 2026-10-12 — composicao V012 e pre-escuta no BlastEm

- A escuta do usuario rejeitou V010 por baixa qualidade musical. V011 foi buildada e executada, mas a revisao de score encontrou duas notas PSG dentro das janelas PCM; V011 e preservada em `out/audio/revisions/v011/` e registrada como supersedida antes da revisao formal.
- V012 conserva o motivo autoral C5-G5-E5-F5 | D5-G5-B5-C6, com as duas notas PSG em score frames 75/105 e a quinta G5 em 174-179, fora das quatro janelas PCM. O PCM tail sustenta C/E/G sobre a cadencia FM.
- O score gerou VGM NTSC de 210 quadros, SHA-256 `186edc0eafb1a288f702e7ca709fca9025a75e7116dd35032292ebf37ed8e6fd`; conversao XGM2 SHA-256 `0c943c3bedcd24f87191a909421e44efe8f8ed0e26353abcfa5b585133997c42`. Loop estrutural passou, mas emenda audivel continua pendente.
- Auditoria de proveniencia passou para 12/12 recursos e `validate_audio.ps1` passou sem issues. ResComp incluiu musica de 768 bytes e quatro cues PCM de 22.272 bytes no total.
- ROM probe V012: 262.144 bytes, SHA-256 `770dd9a796f8c23a1aa76aab91e06d3a6a85bd2d9de399b23b72be3288b5009f`. BlastEm Flatpak 1.0 mostrou ciclo concluido, quatro status PCM e 209/209 amostras de playback sem queda; screenshot `out/blastem_audio_probe_v012/splash_v3_audio_probe_v012.png`, SHA-256 `c29f1d9e6f340aef40b64f00a66f2b660af927e9c79dfc777478392059226a14`. Janela deixada aberta; Z repete o ciclo.
- A rota de captura canonicamente fixada tentou preparar BlastEm 0.6.2 e retornou HTTP 404 antes de abrir. A pre-escuta direta em BlastEm 1.0 e evidencia de execucao candidata, nao evidencia canonica, FPS sustentado ou aprovacao musical. O usuario ainda precisa ouvir a ROM exata V012.
- A ROM `out/rom.bin`, o template canonico, a baseline V2 e o arquivo FORJA V2 nao foram alterados; nenhuma promocao foi feita.

## 2026-10-12 — composicao V013 com acentos cristalinos e BlastEm

- O usuario ouviu V012 e disse que ficou bem melhor; pediu uma camada mais cristalina. V012 foi copiada com score, builder, VGM/XGM2, ROM, captura, relatorios e hashes para `out/audio/revisions/v012/`.
- V013 preserva o motivo `C5-G5-E5-F5 | D5-G5-B5-C6` e adiciona tres acentos FM aditivos, curtos e fora dos cues PCM: C6 em score frame 30, G6 em 138 e C7 em 174. O novo patch ocupa FM_CH4/hardware channel 4; o gerador agora mapeia corretamente os registradores YM2612 do segundo port e o auditor de loop acompanha o estado de todos os seis canais.
- VGM V013: 210 quadros, 1.162 bytes, SHA-256 `8300e25f02a5e41b3e0f6e4e21c33f3d3607fd5e559a0d8da21b738cbbff5527`. XGM2: 772 bytes, SHA-256 `3ec5b2d8f16d120b9781c8078206c96cf873521057ca183a4aedf9a695906fb0`.
- A conversao, a auditoria estrutural de loop, a validacao dos 12 recursos e a auditoria de proveniencia passaram sem issues, erros ou avisos. ResComp incluiu musica de 768 bytes e quatro payloads PCM de 22.272 bytes.
- ROM probe V013: 262.144 bytes, SHA-256 `5eb765fc5e6d7655ae5b3b20d7a59cd521b5719945385bacdbcdea629eab83bd`; fonte do SDK verificada pelo report de identidade do `sdk/sgdk-2.11` canonico. BlastEm Flatpak 1.0 mostrou `FRAME:309`, `CYCLE DONE`, quatro cues PCM e `MUSIC 209/209 DROP:0`. Captura `out/blastem_audio_probe_v013/splash_v3_audio_probe_v013.png`, SHA-256 `753d86f8bf889c653cf6dac50d217b0f8a24b55ab0e26b6de717bf46c36f5a18`; a janela esta aberta, Z reinicia o ciclo.
- O titulo mostrou 59.9 fps em um instante; nao e medicao sustentada. A captura canonica BlastEm continua pendente devido ao fetch 404 da versao fixada 0.6.2. V013 aguarda avaliacao auditiva do usuario; budget DAC, integracao visual e gates de producao continuam pendentes.
- ROM canonica, template e arquivo FORJA V2 permanecem intocados; V013 foi arquivada como candidata isolada em `out/audio/revisions/v013/`.

## 3. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.


## Splash v3 — abertura do laboratorio (2026-10-11)

- Estado: `documentado`; laboratorio criado e contexto `technical_demo` classificado.
- Teto de claim: `technical_demo`; sem `ready_for_aaa`, sem build e sem evidencia de emulador.
- Copia do template verificada por SHA-256 em `out/logs/template_copy_inventory_20261011.json`.
- Inventario pre-arquivo do template: `out/logs/branding_prearchive_inventory_20261011.json`.
- Gate global de ferramentas de medicao: `blocked` por 20 espelhos ativos de `runtime_probe` defasados em outros projetos; 30/30 self-checks passaram. Medicoes de budget permanecem pendentes.
- Promocao ao template e migracoes de consumidores seguem como gates humanos separados.

- Higiene: removido do laboratorio o `doc/scene-contracts.json` herdado que apontava para caminho absoluto do template; sera regenerado da spec local.
- Atualizadas a spec de cena, concepcao, storyboard cinematografico, TDD, contrato de transicao e manifesto de tecnicas do laboratorio.
- Substituidos os placeholders de GDD e roteiro por escopo de technical_demo, narrativa da splash e route decision record.
- O storyboard declara sete estados e 240 quadros NTSC; todos os budgets permanecem needs_review. A origem de lettering continua pendente.
- A rota de sweep por banda de sprites foi tratada como escolhida no plano do usuario. O ResComp local confirma dimensao fixa por SpriteDefinition; 8x8 e 16x16 serao perfis separados.
- A leitura do SGDK 2.11 confirmou que SPR_initEx(16) reserva tiles de VRAM; o pool de objetos e MAX_SPRITE=80. A capacidade de instancia nao e o bloqueio da matriz; VRAM e scanline continuam sem medicao.
- Nao foi executado o simulador de scanline nem foi criado pixel art. Proximos dados de coreografia serao inputs nao medidos para execucao futura.

- Diagnostico local: 16/16 assets ativos referenciados em /res estao conformes, sem blockers; 106 fontes em /data incluem material legado que exige conversao. Laudo: out/logs/art_diagnostic_report_splash_v3.json.
- Arquivados 14 relatorios herdados do template em out/logs/template_baseline_snapshots/, com hashes no manifesto. Relatorios ativos ficam em out/logs/; documentos e fontes ativas nao mantem caminhos absolutos externos.
- Contexto, metodologia, higiene, layout e quatro schemas passaram em 2026-10-12. Essa validacao nao mede budget nem promove arte/runtime.

- Compatibilidade do plano de residencia corrigida: cada estado agora expoe id e resident no nivel consumido pelo audit_tile_residency.py. A vista aninhada segue para documentacao; todos os valores continuam not_measured, sem alegacao de budget.

- O loader de audit_tile_residency escolhe o primeiro storyboard raiz em ordem alfabetica. O storyboard v2 foi preservado com SHA em rascunho/baseline_branding_v2, e suas referencias locais foram atualizadas; o v3 passa a ser a unica fonte que o loader encontra.

- A comparacao somente-leitura do gate esta em out/logs/runtime_probe_mirror_review_20261012/. Sao 20 copias ativas em 11 projetos, seis em tres consumidores protegidos; os diffs de substituicao integral sao grandes e nao foram aplicados. A medicao depende de reconciliacao por projeto com os respectivos owners.


## 2026-10-12 - rejeicao V013 e reautoria V014

- O usuário rejeitou V013 após ouvir a ROM: som contínuo e monótono, sem o ânimo e a energia combinados. A classificação foi atualizada para rejected_by_user; a ROM e o score permanecem preservados como histórico.
- V014 parte do contorno de V012 (referência que recebeu retorno positivo) e troca as linhas quase legato por ataques curtos em 6/8, pausas reais, baixo pontual e três lampejos FM cristalinos. Entrada musical passa ao quadro 60, depois do cue de subida; a faixa fecha em 180 quadros e sai no quadro 240.
- O preview visual e auditivo ainda é de laboratório. A aprovacao musical do usuário, a cena Splash V3 completa, o budget DAC/performance e o gate canônico BlastEm continuam pendentes.
- ROM de audição V014: buildado, SHA-256 f0fedae74ab9a2e64680022f98c9a2d90ab77334eb8687c9e5028dc1bc73d407; abriu em BlastEm Flatpak 1.0 e mostrou 179/179 amostras de XGM2 sem quedas e quatro cues PCM iniciados. Captura em out/blastem_audio_probe_v014/splash_v3_audio_probe_v014.png. Preview não canônico; aprovacao humana e medição de desempenho permanecem pendentes.
- Validação geral do projeto V014: report em out/logs/validation_report_v014_20261012.json, closeout_gate=false (11 erros, 16 avisos; 12 blocking_statuses). O freshness audit ficou em warning (1 artefato stale, 2 relatórios obrigatórios ausentes). Os blockers são do fechamento amplo da cena/contratos/documentação; as validações específicas de áudio passaram.

## 2026-10-13 — Preview visual WIP integrado e pontos de curadoria

- O usuario autorizou manter a V3 em desenvolvimento para aprimoramento futuro e pediu registrar os criterios de curadoria. Isso permite preview isolado; nao aprova visual, audio, model sheet, ROM final ou promocao.
- Composicao V003 traduzida a quatro assets de placeholder em `res/`; fontes originais e hashes preservados em `data/source_art/branding_v3/sources/`, `premium_source_manifest.json` e `doc/asset_provenance_manifest.json`.
- O runtime usa PAL0 fundo, PAL1 SGDK, PAL2 FORGE, PAL3 particulas; nao ha placa de contorno separada. O sweep e sete instancias 8x8 do particle strip, diagonal em y=76..124.
- Build local SGDK 2.11 via Linux/Wine bridge: 262144 bytes, SHA-256 `3478ae036d80d8df8fc99259ab6e1175c27ceeb9b33bf4f5ec4c724f8010cfd0`; capturas selecionadas estao ligadas a esse hash no report `preview_observed_unsealed`.
- O viewport final mostra hierarquia clara; a convergencia sobrepoe particulas ao SGDK. Cantos inferiores, movimento completo do sweep e prompt final permanecem sob revisao.
- Medicao local atualizada: 990 entradas; 64x8x8 passa com 17 sprites/136 px por scanline; 7x8x8 passa com 1/8. Perfis 80x8x8 e geometrias 16x16 maiores excedem limites. Report em `out/logs/splash_v3_scanline_visual_runtime_20261013.json`; o gate global continua bloqueado por espelhos externos.
- A verificacao de linhagem visual passou para o contrato de direcao WIP; status `needs_review` e nenhuma promocao a pixels finais.
- Retornos musicais continuam vinculantes: V012 positiva, V013/V014 rejeitadas por monotonia, V015 somente desenvolvimento e ainda sem escuta final da cena integrada.
- Revisao futura: dois ciclos audiovisuais, leitura 320x224, rota/model sheet autorais, tile vocabulary do fundo 20-40, budgets de VRAM/DMA/CPU/DAC, 60fps sustentados e evidencia BlastEm hash-bound.
- FORJA V2, ROM canonica, template e consumidores nao foram alterados.

## 2026-10-14 — V004 observada e curadoria de desenvolvimento

- O usuario promoveu Splash V3 para estado em desenvolvimento com revisao futura obrigatoria. Nenhuma aprovacao final de visual, audio, lettering/model sheet, ROM ou promocao foi dada; FORJA V2, template e consumidores continuam intactos.
- V004 foi selecionada como candidata visual WIP: fonte AI de conceito com centro negativo mais amplo, cristais laterais e convergencia inferior. ROM SGDK 2.11 Linux/Wine buildada: 262144 bytes, SHA-256 `b852241c1058999cdf99056e9f6f95be159d17f70b85ddf7b99c0e29257aae97`, flag `SPLASH_V3_VISUAL_PREVIEW`.
- BlastEm local 1.0.0 mostrou estados selecionados de energia, contorno/preenchimento, FORGE, sweep, fade e prompt. BUTTON_A reiniciou a cena quando a janela estava focada e a tecla foi mantida por 180 ms. Evidencia `out/logs/splash_v3_visual_preview_report_20261014_v004.json` e contact sheet `out/blastem_splash_v3_visual_preview_20261014/v004_replay_sequence_contact_20261014.png`; status `preview_observed_unsealed`, sem claim `testado_em_emulador`.
- A folha de contato usa labels temporais aproximados; a timeline de 240 quadros ainda precisa de marcador de frame e captura completa. A janela mostrou 60.3 fps instantaneos, sem prova de performance sustentada.
- Host sem PulseAudio; SDL dummy foi usado. Audio nao foi escutado nem avaliado nessa rodada. V012 continua referencia positiva; V013/V014 rejeitadas por monotonia/energia insuficiente; V015 permanece candidata sem aprovacao.
- Tile audit V004: 1.120/1.740 tiles de payload de arte (64.4%, 35,840 bytes), apenas 18% deduplicacao do fundo. Variantes automaticas de 40/80/120/160 tiles foram rejeitadas visualmente; reautoria manual/reutilizavel continua aberta. Isso nao fecha VRAM total, DMA/VBlank, CPU, DAC ou FPS.
- Pontos para curadoria: centro negativo e leitura do SGDK durante todos os beats; contraste/hierarquia FORGE; densidade de cristais e particulas sobre as letras; direcao e timing do sweep; brilho sem ruido; prompt; rota e model sheet de lettering; vocabulary de tiles sem repeticao mecanica; dois ciclos audiovisuais; budgets e evidencia canonica.
- IDs do registry ativos no escopo, sincronizados com GDD/TDD: `fixed_point_trig_lookup`, `dma_transfer_safety`, `palette_state_transitions`, `shadow_highlight_slot_rule`, `palette_remastering_slot_audit`, `tile_flipping`, `tile_dedup_hvflip_hashing`, `xgm2_pcm_multiplexing`, `xgm2_audio_architecture`.

## 2026-10-14 — V005 integrada como candidata visual WIP

- V005 substituiu V004 como fundo selecionado somente no build de preview com `-DSPLASH_V3_BACKDROP_V005`. A fonte AI persistida tem SHA-256 `bb32cf3c7e954b99d71fe71ed0197ba10685f1742847ccd1f75e91313016daea`; o PNG runtime `res/branding_v3/splash_backdrop_v3_v005_320x224.png` tem SHA-256 `ef75c6ec1c429e16ad3fa3aae55acf846631d4ff0d5f2a0f3c8b02fe47c39ab0`.
- A traducao 320x224 usa 15 cores, index 0 preto, 1120 tiles brutos, 755 unicos sem flip e 744 apos H/V. Frente ao V004 (916 H/V), poupa 172 tiles (18,8%) e chega a 33,6% de deduplicacao. O controle V005 de 40 tiles foi rejeitado por textura quadriculada; reautoria manual continua aberta.
- ROM de preview: 262144 bytes, SHA-256 `d4d7e5c842d31e88652d7e06856d9eeb3b4b182bb918c11f5aa20eefe6532319`, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V005`. BlastEm local 1.0.0 mostrou campo de energia, reveal SGDK e lockup SGDK/FORGE em capturas selecionadas e aproximadas; o ciclo completo, prompt e replay ainda nao estao documentados frame-a-frame. O relatorio `out/logs/splash_v3_visual_audio_review_report_20261014_v005.json` permanece sem selo canonico.
- A captura WAV de monitor fisico ligada ao hash da ROM dura 10,24 s, 48 kHz stereo, PCM 16-bit, pico 23282 e RMS 2626,3; SHA-256 `3f68234a59889ed7f337e0c1d72534dd955eecd52a4a6e79282af0c22b45f453`. Isso confirma sinal capturado, nao qualidade musical; o usuario ainda precisa ouvir e avaliar dois ciclos, articulacao, timbres, energia, brilho e emenda.
- A auditoria do plano V005/B calcula 984/1740 tiles H/V (31.488 bytes; 56,6%), sem fechar VRAM real, tiles carregados por codigo, VBlank/DMA, CPU, DAC ou 60fps sustentados. O aviso do resource graph para tiles code-loaded continua.
- Validacoes focadas depois de B: self-check de residency passou e mediu 984 em todos os sete estados; o aviso permanece apenas no recurso V004 de comparacao. Proveniencia passou para 21/21 simbolos pixel-bearing e `validate_visual_source_of_truth.ps1` passou sem findings. A ROM B nao foi buildada.
- `validate_resources.ps1` atualizado: 3 erros, 20 avisos, 21 verificacoes; produto `technical_incomplete`, `technical_ready=false`. Erros: `workflow_root_ownership_violation`, `code_loaded_tiles_unmeasured`, `claim_sources_missing`. Closeout permanece bloqueado.
- Pontos completos para curadoria estao em `doc/curation/splash_v3_visual_curation_record_20261014.md`; V2, template e consumidores permanecem inalterados.
- Capture local de aprendizado terminou em `no_qualified_lessons`; nenhuma promocao canonica foi realizada.

## 2026-10-14 — folha de direcoes de lettering para curadoria

- Persistida a folha AI V003 `data/source_art/branding_v3/sources/source_lettering_model_sheet_ai_v003_20261014.png` (SHA-256 `d28a90d516d1d04dd77bd84211dbd5cc21e49637b08c7879004225f4878796e8`) e sua ficha em `doc/curation/splash_v3_lettering_direction_board_20261014.json`.
- Direcoes A `heroic_ice`, B `faceted_crystal` e C `forward_energy` foram comparadas em probe nativo. B e recomendacao curatorial para refinamento, sem escolha humana; A fica como baseline e C como alternativa energetica/esportiva.
- Folha permanece controle de fonte em `data/source_art/` e `rascunho/visual_lab/`. B foi copiada para os dois caminhos WIP de `/res` com baselines pre-B preservadas; nao ha ROM reconstruida com B nem integracao final aprovada.
- Antes de arte final: revisar 320x224, spelling e legibilidade de cada glifo, espacamento, hierarquia SGDK/FORGE, silhueta, regras de faceta/contorno, paleta 4bpp/indices e piso de contraste; so depois consolidar model sheet e proveniencia.
- A prancha `data/source_art/branding_v3/sources/source_lettering_runtime_context_ai_v001_20261014.png` (1024x1536, SHA-256 `20fa2e32a125d829f26bf33287103339699b4e1fb99a55b32e42ce2341fee7d7`) compara A/B/C sobre V005. Ajuda na hierarquia e composicao, mas nao e viewport 320x224 verificado, nem pixels 4bpp ou placa runtime.
- Feitas provas deterministicas A/B/C com `data/source_art/branding_v3/build_splash_v3_lettering_native_probes.py`: seis placas indexed 4bpp, index 0 transparente, tamanhos 224x48/192x32, 13-15 cores visiveis. B foi ativada como placeholder WIP nos caminhos existentes de `/res`; comparacoes A/B/C e frame 320x224 continuam em `rascunho/visual_lab/`. A ROM ainda nao contem B.
- O probe atual mostra A muito proxima do placeholder, B com facetas mais fortes e counters ainda abertos, e C mais inclinada/esportiva. A recomendacao mudou para refinar B; escolha humana e model sheet continuam pendentes.


## 2026-10-14 — B ativa como lettering WIP; build pendente

- Usuario confirmou desenvolvimento com revisao futura e autorizou avancar a etapa visual. Direcao B `faceted_crystal` foi ativada como candidate curatorial WIP, sem selecao humana ou aprovacao final.
- Placas B indexadas em `/res`: SGDK SHA `f43440eb16fd5f3560fda61a9ce8109674113d5cf07439d432627e59400b4be9` (224x48, 143 raw/141 H/V, 15 cores); FORGE SHA `0bcb75cbf646b36ba00c44d7ec11b826715d033cd87374c91af594643e2e674c` (192x32, 92 raw/91 H/V, 14 cores). Baselines pre-B preservadas e restauracao reversivel.
- Composite estatico 320x224 `rascunho/visual_lab/splash_v3_lettering_probe_b_v001_320x224.png`, SHA `15e97ea38a63f48b45d7a97a35ad7cb47d85b3161ed967e452243cc4964d1745`; nao e captura de ROM ou aprovacao de legibilidade em CRT.
- Residency V005/B: 984 tiles H/V, 31.488 bytes, 56,6% do payload estimado; self-check passou. Proveniencia passou em 21/21 simbolos. A ROM candidata nao foi gerada.
- Build canonico foi bloqueado antes de make: Flatpak/bwrap falhou ao resolver `winepath`; `/run/user/1000` estava 100% ocupado. O consumo visivel vem principalmente de diretorios pytest existentes na pasta temporaria compartilhada. Nada foi removido; ver `out/logs/splash_v3_lettering_b_build_block_20261014.json`. ROM existente continua no hash V005 pre-B `d4d7e5c842d31e88652d7e06856d9eeb3b4b182bb918c11f5aa20eefe6532319`.
- Curadoria aberta: revisar counters/spelling, silhueta e facetas por glifo; piso numerico de contraste; hierarquia SGDK/FORGE; safe areas e leitura em 320x224/CRT; fundo, convergencia, particulas, sweep, reveal/fade/prompt; vocabulario de tiles sem repeticao; ouvir dois ciclos V015 com comparacao V012; fechar budgets e evidencia vinculada ao hash.

## 2026-10-14 13:36Z — V006/B WIP em desenvolvimento

> Registro historico de runtime e evidencia V006/B; o estado corrente e V017 abaixo.

- Decisao do usuario mantida: Splash V3 segue `em_desenvolvimento`, com revisao futura obrigatoria para aprimoramento. Nenhuma aprovacao final, troca do template ou arquivamento de FORJA V2.
- O fundo V006 runtime (`res/branding_v3/splash_backdrop_v3_v006_320x224.png`, SHA `bd50ab81a7900806dc9f1e1fcdd0ccba76dad7fcebf8996162f3af46825c069b`) preserva centro negativo e cristais laterais; fonte SHA `f3e924c1580c8ead73b0df84b9b557cef69af45eeff4e311bf236b7b371829b8`. B continua placeholder WIP em `/res` e foi incluida na ROM, mas nao escolhida/aprovada pelo usuario.
- A revisao do screenshot levou a tres ajustes no hold de preview: PAL0 agora transita para uma paleta de repouso em vez de preto; o hint tornou-se `A: REVER`; foi centralizado em coluna 16/linha 21, abaixo do logo e fora do topo do flare. O screenshot semantico nao substitui julgamento artistico.
- Build pelo wrapper SGDK 2.11: 393216 bytes, SHA-256 `22c6e3962c253b2588cd07d0b9d4fa2d890d4366b8e4de71a87b59e1b755baf4`, flags `SPLASH_V3_VISUAL_PREVIEW` e `SPLASH_V3_BACKDROP_V006`; report `out/logs/linux_wine_build_report.json`.
- BlastEm Linux Flatpak 1.0, sessao `blastem-linux-20261014T133648Z-289753`: cena 0, 1200/1200 quadros, screenshot SHA `a5a189903c49e7f6e58a32c5e89365870650669207c8e9da5c99bef5f18a2b5a`, semantic gate `passed`, freshness `ok`, bundle selado em `out/blastem_splash_v3_visual_v006_hold_wip_v004_20261014/blastem-linux-20261014T133648Z-289753`. Inclui SRAM, VLAB telemetry block, runtime metrics e audio.raw. O dump VLAB tem 204 bytes; nao e VRAM integral.
- Medidas: snapshot do titulo 57.7 FPS (nao prova estabilidade); 37/1200 quadros acima do budget, CPU max 459, 64 sprites ativos e pico 17 sprites/linha. `performance_claim=unproven`; otimizar e provar 60fps sustentados com audio.
- Residency V006/B: 823 tiles H/V (26.336 bytes; 47,3% de 1.740) incluindo 583 backdrop + 141 SGDK + 91 FORGE + 8 particulas. O target curatorial de 20-40 tiles continua aberto sem repeticao mecanica.
- Proveniencia real passou 22/22 simbolos, sem blockers: `out/logs/splash_v3_asset_provenance_wip_post_v006_20261014.json`.
- Pendencias: revisao humana 320x224/CRT; model sheet por glifo e contraste numerico; captura frame-marked dos sete beats; trace do replay BUTTON_A; escuta de dois ciclos e emenda musical; VRAM/code-loaded tiles/DMA/VBlank/CPU/DAC; performance sustentada.
- Registro completo de pontos para curadoria: `doc/curation/splash_v3_visual_curation_record_20261014.md`; contrato `doc/branding_v3_development_contract.json`.

## 2026-10-14 15:23Z — V017: convergencia de particulas para o lettering

- Mantido o status `em_desenvolvimento`, com revisao futura. Aprovacoes finais, promocao do template e arquivamento da FORJA V2 continuam falsos.
- Os 64 alvos 8x8 agora sao derivados de celulas visiveis no SGDK WIP, substituindo a grade uniforme. Uma atribuicao r1 mediu 21 sprites/linha em F108 e 22 em F109 (176/320 px); o usuario relatou que o pico pareceu perfeito e questionou a severidade do gate. Tratar como candidato visualmente toleravel com overflow controlado, nao como falha visual automatica, se as particulas excedentes forem decorativas; isso nao muda o limite H40 de 20 sprites/linha nem prova que todos os 22 aparecem. A simulacao nao tem hash de ROM e a captura V017 usa r2, portanto o feedback e visual, nao validacao de budget. Todas as particulas r1 cabem na area X, sem inflacao por sprite fora de tela. A r2 atual mede 13 sprites/104 pixels em F106 e 64 links. Detalhes: `out/logs/choreography_inputs_splash_v3_glyph_anchor_v001_20261014_r2/particle_glyph_anchor_contract.json`, `out/logs/splash_v3_scanline_glyph_anchor_v002_20261014.json` e `out/logs/splash_v3_h40_peak_review_20261014.json`.
- Build V017: 393216 bytes, SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`. A amostra visual diagnostica mostra energia, reveal, FORGE, sweep, lockup e prompt, mas nao fornece frame markers, input ROM-side ou selo canonico.
- A ROM inclui V016/VGM4 (C maior, 6/8, 120 BPM, 180 quadros; baixo, harmonia e acentos separados no stereo). A escuta humana ainda esta pendente; o `audio.raw` nao substitui a revisao.
- Lista completa de curadoria e limites: `doc/curation/splash_v3_visual_curation_record_20261014.md`; resumo de evidencia: `out/logs/splash_v3_v017_visual_review_report_20261014.json`.






## 2026-10-14T16:07:59Z — V008/V009 visuais e handoff V3

- Mantido em desenvolvimento; revisao futura obrigatoria. V007 rejeitado por ruido/custo (719 tiles H/V). V008: 438 tiles, centro limpo, simetria estatica. V009: 438 tiles, mais assimetrico/direcional; raios precisam de safe-area review. Ambos continuam em rascunho/visual_lab; V006 permanece baseline de res.
- O perfil de handoff foi implementado com lock de input/update de 12 quadros, espera por fade/DMA drain, teardown da Splash, entrada/fade do menu. Sem build: Flatpak/bwrap falhou antes da compilacao devido ao tmpfs /run/user/1000 cheio. V017 continua ultima ROM, SHA 5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2.
- APIs checadas contra SGDK 2.11. Revisao estatica ficou com risco por falta de compilacao/BlastEm. MENU ainda herda arte/BGM V2.
- Mantidos todos os gates humanos em falso; audio ainda precisa resolver feedback de abafado/monofonico, continuidade monotona e falta de energia; V016/VGM4 nao recebeu escuta de dois ciclos.

## 2026-10-14 — V010–V012: area segura do lettering

- Foram geradas, traduzidas e preservadas as fontes V010–V012 e os paineis de comparacao; V006 continua sendo o fundo em `/res` e na ultima ROM.
- O instrumento `data/source_art/branding_v3/audit_splash_v3_backdrop_safe_area.py` passou 5/5 self-checks e comparou a mascara atual do lettering em 320x224. A ordenacao automatica atualizada classifica V012 em primeiro por menor contaminacao medida sob as letras; isso nao e selecao estetica. V012 mede luma medio/P95/max 3/3/3 sob as letras, sem amostras acima de 32, e 272 tiles H/V. V011 tinha 1,13% de pixels acima de 32 concentrados sob o S; V010 7,27%; V009 14,54%.
- Report e hashes: `out/logs/splash_v3_backdrop_safe_area_20261014.json`; traducao V012: `out/logs/splash_v3_backdrop_v012_translation_report_v002_20261014.json`. `forge_art workset-validate` passou com a epoca V012 ativa, 7 fontes de producao e 6 referencias.
- V012 e a melhor candidata WIP medida para proteger o logo. Nao esta selecionada nem promovida: o campo negativo e as bordas ainda precisam ser julgados com lettering final, particulas, sweep, 320x224/CRT e ROM hash-bound. Nenhuma aprovacao final ou promocao foi dada.


## Atualizacao 2026-10-14 20:53Z — selo corrigido e revisao formal

- O recibo da sessao V012 hold foi corrigido: seal tentado antes do shutdown nao e efetivo para o bundle pos-shutdown, com `.lock`, `.seq`, `.seq.lock` ausentes e hashes de `blastem.log`/`xvfb.log` diferentes. A ROM e a screenshot seguem verificadas por hash independente; status apenas `preview_observed_unsealed`.
- Revisao formal `out/logs/sgdk_code_review_report_splash_v3_menu_text_fix_20261014.json`: correcao de texto aprovada com risco; riscos abertos para closeout, selo canonico, input ROM-side e budget.
- Validacao geral corrente no momento da revisao: 14 erros e 7 avisos; `technical_ready=false`, `visual_gate_ready=false`, `validado_budget=false`, `testado_em_emulador=false`. O trabalho permanece em desenvolvimento.
- Pico r1: 22 celulas/176 px em F109 e 2/1200 quadros naturais; a probe ignora X, mas a trajetoria F109 fica em X=48..256. O usuario relata que o quadro funcionou perfeitamente. Isto registra tolerancia visual WIP, nao budget aprovado: H40 continua com teto 20. V017 permanece em `out/rom.bin`, r2 default.
- Nenhuma promocao do template ou arquivamento da FORJA V2.

## 2026-10-15 04:43Z — criterio H40 e V018 r2 com telemetria corrigida

- O usuario relata que o pico r1 de 22 sprites em F109 pareceu perfeito. Tratar como tolerancia visual WIP, nao como budget conforme: H40 continua limitado fisicamente a 20 sprites por scanline. O limite nao e margem conservadora. Nao rejeitar a imagem apenas por um pico raro; manter `over_limit_not_approved` ate reduzir a demanda ou inspecionar SAT/VDP real. r1 mede 22/176 px em 2/1200 frames; sao geometrias da lista SGDK, nao prova de 22 sprites efetivamente apresentados.
- ROM V018 r2 corrigida `d46bd88a26019625844ab8c1732d9c76187df5c247ff27aaf6a2877998ee2d9f`: 14 sprites/112 px maximos, nenhum frame acima dos limites H40; 64 particulas criadas, 0 falhas. Captura selada experimental em `out/evidence/splash_v3_v018_sprite_alloc_telemetry_20261015/blastem-linux-manual-v018-sprite-alloc-telemetry-20261015/`.
- Limites abertos: 37/1200 frames excederam budget CPU, max 398; snapshot 59,1 FPS nao prova 60 sustentados. Fila DMA solicitada max 5832 bytes/29 ops, amostrada antes do VBlank; intervalos de VRAM sao declaracoes do loader e dump de 244 bytes e apenas VLAB, portanto sem leitura integral/conclusao fisica.
- Canonical BlastEm segue bloqueado por HTTP 404 no Flatpak pinned; a captura direta 1.0.0/X11 e experimental. Audio nao recebeu escuta humana e V018 segue `needs_review`. Nenhuma promocao de template ou arquivamento FORJA V2. Relatorios: `out/reviews/splash_v3_v018_runtime_telemetry_20261015/`.


## 2026-10-15 — V019 exact-hash visual preview

- V019 é candidata opt-in de fundo, não seleção final. O conceito AI derivado da referência V006 (`9fc213cc726c3a2fbbfff0ff9e9f9e15023e29f74459398c0a5af9802536840e`) foi traduzido a 320x224 indexado, 15 cores visíveis, 552 tiles H/V (`b8b403f30c170554df647ac1b6b2a54fc83b3e3c76a695765ec4ac0ec313e819`). O teste técnico de pixels passou; status de arte continua placeholder/needs_review.
- ROM isolada: `out/profiling/splash_v3_v019_backdrop_preview_retry_20261015/rom.bin`, 524288 bytes, SHA `6731a055ce88cbb2b122cfd2e03f1690ef8a430b890670477ef2438549d2019b`; build `out/work_runs/splash_v3_v019_backdrop_preview_retry_20261015/reports/linux_wine_build_report.json`. `out/rom.bin` não mudou e permanece V017 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`. A identidade de conteúdo do build corresponde à fonte canônica `sdk/sgdk-2.11`.
- Captura BlastEm exata e selada: `out/evidence/splash_v3_v019_preview_20261015/blastem-linux-manual-v019-preview-20261015/evidence_manifest.json`; screenshot `1d65db41a51ba5dfd130235ae30a98aaedc51dd17a90399855642fc54cefe4b2`, semantic gate passou, freshness ok. Rota instalada 1.0.0/X11 manual experimental; helper canônico continua bloqueado por HTTP 404. Preview único em hold; `A: REVER` é instrução de revisão exclusiva do build de preview.
- Runtime V019: 1200/1200 quadros, 14 sprites/112 px por linha, zero excedentes H40, 64 partículas/0 falhas; CPU sobre budget em 37/1200, max 398; FPS 60.9 é leitura instantânea. Faixas de loader declaram 792 tiles, sem readback total; fila DMA de 5832 bytes/29 entradas observada antes do VBlank, sem conclusão física.
- Curadoria do quadro final: centro escuro e lockup legível; facetas assimétricas e ignição inferior dão movimento, sem horizonte contínuo visível. Pedir revisão humana a 320x224/CRT e durante reveal/sweep; a revisão frame-accurate completa dos beats continua pendente. Áudio foi dummy, sem escuta/aprovação, DAC ou performance com áudio.
- A sequência V019 foi observada também em 17 stills host-timed, vinculados ao mesmo SHA da ROM, em `out/evidence/splash_v3_v019_motion_samples_long_20261015/motion_samples_manifest.json`; o contato está em `out/evidence/splash_v3_v019_motion_samples_long_20261015/motion_contact_sheet.png`. A sequência sugere partículas, contorno, preenchimento/FORGE e hold, mas inclui atraso de inicialização e amostragem aproximada de ~0,5 s, sem marcadores de frame: não fecha o timing do sweep nem o ciclo completo. A tentativa GIF foi rejeitada por corrupção de paleta e não serve como evidência visual.
- O pico r1 de 22 sprites em F109 permanece tolerável como direção visual WIP rara, mas fora do limite físico H40 de 20; não rejeitar automaticamente por aparência nem chamar conforme ao budget.
- Validação de recursos em 2026-10-15: 3 erros/19 avisos; erros em tiles carregados por código C e reconciliação de reports para ROMs distintas (baseline vs candidata), sem blocker específico V019. Metodologia e higiene passaram. Freshness ainda marca reports de runtime anteriores como stale. V006 segue default; estado `em_desenvolvimento`; sem aprovação final, promoção do template ou arquivamento da FORJA V2. Relatórios de review: `out/reviews/splash_v3_v019_visual_review_20261015/visual_quality_review.json`, `out/reviews/splash_v3_v019_visual_review_20261015/vdp_budget_report.json`, `out/reviews/splash_v3_v019_visual_review_20261015/code_review_report.json`.


