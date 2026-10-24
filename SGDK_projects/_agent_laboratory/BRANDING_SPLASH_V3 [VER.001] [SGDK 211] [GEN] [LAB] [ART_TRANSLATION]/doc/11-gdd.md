# 11 - GDD — BRANDING_SPLASH_V3

## Project brief

- Promessa: apresentar a assinatura SGDK Forge em quatro segundos, com energia azul articulada que converge para a marca. A implementacao atual e um preview WIP de laboratorio.
- A pessoa que assiste observa uma sequencia de identidade; nao ha acao de jogador nem loop de gameplay.
- O Mega Drive e tratado como hardware real: composição 320x224, duas backgrounds, sprites, paletas finitas e prova de budget.
- O laboratorio nao e jogo completo, vertical slice jogavel, release ou promocao do template.

## Visao

Uma abertura breve, escura e silenciosa desperta em pontos azuis. A energia se
espalha e converge; SGDK aparece por fade-in de paleta; FORGE entra abaixo; seis
fagulhas individuais atravessam o lockup em arcos suaves e se dissipam. O preview
atual termina em fade e aguarda A para reiniciar, sem entregar ao menu.

O tom e tecnico e autoral, sem reproduzir os pixels do Xemu. O foco e fazer a
marca aparecer como consequencia da energia e dar tempo para que ela seja lida.
Este projeto nao altera a identidade ou os contratos do template nem dos cinco
consumidores protegidos.

## Core loop

Nao aplicavel: a splash e uma cena temporizada de identidade, sem gameplay.

## Feature scope map

### Entra no laboratorio

- Sete estados cronometrados, 240 quadros NTSC, implementados no preview isolado.
- Campo WIP de 64 particulas 8x8 e movimento por LUT; a geometria foi medida localmente em 990 entradas.
- Placa SGDK com fade-in de paleta e placa FORGE subordinada; nao existe placa separada de contorno.
- Sweep WIP de seis fagulhas 8x8 com trajetórias Bézier assíncronas, nascimento/fade e rastros direcionais reutilizados; ROM isolada em revisão no BlastEm. A prévia termina com prompt A de replay. Contrato: `doc/curation/splash_v3_wind_lifecycle_motion_contract_v002_20261015.json`.
- Placas, sprite FX, composicao V015 e runtime estao integrados como placeholders no laboratorio.

### Entra depois, somente apos gates

- Master tipografico, model sheet aprovado, pixels finais, composicao sonora aprovada e budgets completos.
- Captura canonica BlastEm, SRAM/VDP dump, validacao de audio/performance e fechamento de QA.
- Promocao do resultado ao template por aprovacao humana explicita.
- Migracao individual dos cinco consumidores, cada uma com aprovacao humana propria.

### Fora de escopo

- Jogo completo, gameplay, multiplayer, AAA, release e ROM pronta.
- Alterar arquivos, contratos ou .agent locais dos cinco consumidores.
- Editar o template antes da aprovacao de promocao.
- Promover pixels WIP a finais antes de aprovacao humana da fonte/model sheet.

## Identidade de front-end

- Fantasia inicial: energia tecnica se reunindo numa assinatura legivel.
- Linguagem: fundo escuro, energia azul, placas SGDK/FORGE com papeis separados.
- Vida visual: expansao e contracao temporal, mudanca de paleta e faixa esquerda-direita.
- Feedback: lock sonoro acompanha a revelacao; nao existe cursor nem selecao.
- Fora de tom: copia de logo/fonte externa, ruído sem funcao, flicker ou texto placeholder.

## Ambicao tecnica, visual e sonora

- quality_promise: o lockup deve ler no viewport 320x224; a qualidade final sera revisada depois de motion capture, model sheet e aprovacao humana.
- visual_direction: placas indexadas WIP e quatro papeis de paleta implementados; os assets atuais continuam placeholders.
- sound_direction: V015 autoral em XGM2 e quatro cues estao integrados no preview; qualidade musical final continua sem aprovacao humana.
- gameplay_quality_bar: nao aplicavel; a cena nao promete gameplay.
- hardware_strategy: BG_A para placas, BG_B para fundo, sprites para FX, CRAM com owner unico; sem WINDOW e H-Int.

## Tecnicas escolhidas

As linhas abaixo continuam como direcao tecnica. Movimento radial, preload em
fila, mudancas de paleta e ownership XGM2 estao implementados no preview WIP;
apenas a geometria de sprites foi medida localmente. Nenhuma tecnica fecha por
si so o budget total ou libera promocao. Contratos: doc/tdd_contract.json.

| Cena/sistema | Registry ID e tags | Funcao | Papel visual/sonoro | Owner skills | Budget/evidencia | Fallback |
|---|---|---|---|---|---|---|
| Particulas | fixed_point_trig_lookup — FIXED_POINT_MATH, TRIG_LOOKUP, CPU_OPTIMIZATION | Expandir e contrair ao redor do lock sem float | Movimento radial repetivel | code/sgdk-runtime-coder; hardware/megadrive-vdp-budget-analyst | CPU e scanline por todos os quadros, depois BlastEm | Direcoes e raios precomputados |
| Entrada de recursos | dma_transfer_safety — DMA_OPTIMIZADO, DMA_QUEUE, VBLANK_BUDGET_AUDIT | Evitar upload inseguro durante a cena | Preservar continuidade visual | hardware/megadrive-vdp-budget-analyst; code/sgdk-runtime-coder | Envelope de entrada e pior quadro VBlank | Adiar carga ou reduzir residency medido |
| Contorno, fill e fade | palette_state_transitions — PALETTE_MANAGEMENT_AVANCADO, PALETTE_TRANSITION, PALETTE_FLASH | Revelar a marca sem redesenhar pixels | Progressao de contorno a preenchimento | art/visual-excellence-standards; code/sgdk-runtime-coder | Owner de CRAM, report de paleta e runtime | Um estado preenchido e fade simples |
| Slots de paleta | shadow_highlight_slot_rule — PALETTE_MANAGEMENT_AVANCADO, SHADOW_HIGHLIGHT, PALETTE_REMASTERING | Evitar uso acidental de slots especiais | Reservar papeis de cor; S/H fica desligado | art/visual-excellence-standards | Auditoria de slots depois do master | Nao habilitar Shadow/Highlight |
| Remasterizacao | palette_remastering_slot_audit — PALETTE_REMASTERING, PALETTE_MANAGEMENT_AVANCADO, SHADOW_HIGHLIGHT | Eliminar cores mortas e definir PAL0-PAL3 | Manter leitura entre os estados | art/art-conversion-pipeline; hardware/megadrive-vdp-budget-analyst | Slot audit e dead-color report depois da arte | Simplificar rampas |
| Tiles BG_B | tile_flipping — CUSTOM_SPRITE_COMPOSITION, METASPRITE_OPTIMIZATION, SPRITE_ENGINEERING, VRAM_TILE_INDEX_MANAGEMENT | Reusar orientacoes por flags do VDP | Variar fundo sem duplicar pixel art | art/megadrive-pixel-strict-rules | Relatorio de flags e indice de tile | Manter tiles distintos quando leitura exigir |
| Residency BG_B | tile_dedup_hvflip_hashing — TILE_DEDUP_HVFLIP, VRAM_TILE_INDEX_MANAGEMENT, METASPRITE_OPTIMIZATION | Medir economia real por tile 8x8 | Controlar custo do fundo | art/art-conversion-pipeline; hardware/megadrive-vdp-budget-analyst | Unique tiles, savings, collision e residency reports | Reautorar vocabulario do fundo |
| Audio de evento | xgm2_pcm_multiplexing — AUDIO_ENGINEERING, MULTIPLEXING, PCM_AUDIO, XGM2_AUDIO, YM2612_AUDIO, DAC_AUDIO | Dar owner aos cues junto do loop | Fazer som marcar energia e assinatura | code/xgm2-audio-director; code/sgdk-runtime-coder | Audio card, sample audit, prova simultanea e BlastEm | Remover cues secundarios |
| Arquitetura sonora | xgm2_audio_architecture — AUDIO_ENGINEERING, XGM2_AUDIO, FM_SYNTHESIS, YM2612_AUDIO, PSG_AUDIO, DAC_AUDIO | Unificar loop, cues e handoff | Evitar cortes e mascara sonora | code/xgm2-audio-director; architecture/scene-state-architect | Loop report, ownership e audio proof | Loop simples sem PCM simultaneo |

### Tecnicas adiadas

| Registry ID | Decisao | Motivo | Condicao para reconsiderar |
|---|---|---|---|
| sprite_temporal_multiplexing | adiada | O desenho nao usa flicker nem reaproveitamento temporal de SAT | Medicao mostrar que a populacao nao cabe com alocacao normal |
| sprite_band_slot_allocator | adiada | A faixa tem sete segmentos comuns; nao existe slot overcommit planejado | Pressao medida exigir arbitragem por banda |
| h_int_control_plane | adiada | A direcao nao usa raster nem troca mid-frame | Nova direcao aprovada com singleton e teardown |
| contextual_scene_transition_system | adiada | A saida usa fade temporizado sem H-Int | Nova transicao rasterizada for aprovada e medida |
| source_baked_pixel_art_standard | adiada | Rota do lettering segue pendente | Decisao humana do master |

## Mecanicas, progressao e first playable

Nao aplicavel: nao ha mecanicas, progressao jogavel ou first playable neste
laboratorio. A proxima tela e o menu herdado, tratado somente como destino da
transicao.

## Route decision record

- context_type: cena_nova
- dominant_route: planning
- first_skill: art/cutscene-cinematic-direction
- first_tool: data/source_art/branding_v3/choreograph_splash_v3.py para gerar inputs de geometria, sem chamar medicao
- resource_loading_model: scene_local_preload
- asset_strategy: placas IMAGE e FX SPRITE indexados; nenhuma arte procedural ou fonte externa aprovada
- evidence_required: storyboard validado, scanline de todos os quadros, tile residency, DMA, validacao de recursos, BlastEm, SRAM, screenshot, VDP dump e freshness
- forbidden_shortcuts_until_evidence: nao criar pixels finais antes da decisao de lettering; nao rodar medicao enquanto o gate global falhar; nao editar template/consumidores; nao declarar budget, build ou runtime por intencao

## Escopo atual

- Fase: V3 em desenvolvimento; arte WIP e runtime integrados; revisao visual/sonora e budgets ainda abertos.
- Fora de escopo: arte final, promocao ao template, migracoes e claims de entrega.


## Atualizacao de escopo — 2026-10-14

A Splash V3 continua em desenvolvimento isolado. O preview e o perfil candidato de handoff sao modos distintos: a V3 deve preceder o menu, mas o candidato SPLASH_V3_MENU_HANDOFF ainda nao foi compilado. Tecnica de transicao: fade_transition com palette_state_transitions e dma_transfer_safety, owner do app scene manager, 12 quadros de fade-in; futuro handoff requer evidência BlastEm. FORJA V2 e o template permanecem intactos.
