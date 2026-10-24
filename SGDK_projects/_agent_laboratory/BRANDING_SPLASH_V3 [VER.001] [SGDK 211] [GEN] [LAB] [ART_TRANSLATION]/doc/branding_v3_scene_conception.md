# Concepcao de cena — branding_sequence_v3

## Intencao

A splash mostra energia azul reunindo-se numa assinatura tecnica. A pausa inicial deixa a entrada respirar; a expansao cria escala; a convergencia prepara o lock; SGDK surge por fade-in de paleta; FORGE entra como segunda linha; seis fagulhas 8x8 cruzam o conjunto com arcos independentes, rastros curtos e dissipação. O preview atual termina em fade e aguarda A para reiniciar, sem entregar ao menu. O antigo sweep de sete linhas foi rejeitado pelo usuário por monotonia.

Referencia primaria de movimento e clima: o boot do Xemu descrito no brief do usuario. A referencia orienta timing e linguagem azul; nenhum pixel, logo, fonte ou arquivo dela e fonte de asset.

## Planta baixa

- canvas 320x224, H40
- ponto de origem/lock: centro (160,112)
- campo de particulas: raio maximo de coreografia 88 px; LUT inteira de 16 setores
- reserva SGDK: (48,72), 224x48
- reserva FORGE: (64,128), 192x32
- sweep WIP: seis núcleos 8x8, partidas F180-F185, control points individuais e easing suave; até seis rastros 8x8 ficam 4-5px atrás da tangente local. As trajetórias iniciam em x=18-40 e terminam em x=284-300, entre y=97-145; contrato completo em `doc/curation/splash_v3_wind_lifecycle_motion_contract_v002_20261015.json`.
- BG_A recebe as placas WIP SGDK/FORGE; BG_B recebe o fundo de cristais WIP
- nao ha WINDOW, H-Int, terceiro plano, blending alpha ou pixels visuais desenhados por codigo

As reservas delimitam composicao e nao fixam desenho final de letras. No preview, as particulas convergem para uma grade uniforme dentro da placa SGDK; nao seguem anchors dos glifos e nao existe placa separada de contorno. O lettering atual e um placeholder derivado de referencia AI.

## Ritmo

- 0-23: preto e silencio; preload incremental de tiles em lotes de ate 180 tiles por chamada.
- 24-83: 64 particulas 8x8 nascem de forma escalonada, expandem para ate 88 px e iniciam a contracao. O cue de energia dispara em F24; XGM2 inicia em F60.
- 84-119: particulas convergem para a reserva retangular de SGDK. A placa inteira surge no BG_A por fade-in de paleta. Nao existe mapeamento de particulas para pixels dos glifos nem contorno separado.
- 120-149: a paleta completa de SGDK e mantida; a imagem permanece fixa. O cue de lock ocorre em F118 e a rampa termina em F120.
- 150-179: FORGE entra abaixo de SGDK com fade de 12 quadros; o lockup fica em leitura.
- 180-209: seis fagulhas 8x8 percorrem arcos Bézier assíncronos, com easing e ruído discreto de vento; cada núcleo nasce em quatro quadros, pode pulsar individualmente e esfria com menos pixels visíveis. Até seis rastros curtos acompanham a direção local. O cue ocorre em F178. A passagem anterior em sete linhas foi rejeitada por monotonia.
- 210-239: hold curto e fade das 64 cores CRAM para preto. O cue tail ocorre em F210.
- F240 em diante: o preview interrompe o audio, limpa BG_A, desenha `A: REPLAY SPLASH V3` e espera BUTTON_A. O prompt final ainda nao tem captura visual limpa.

## Fonte e aprovacao

As referencias AI de fundo, lettering e particulas foram copiadas para `data/source_art/branding_v3/sources/`, registradas com hashes e traduzidas para quatro assets indexados WIP em `res/`. Eles obedecem grid 8x8, index 0 transparente e cores 9-bit; seguem placeholders e nao sao pixels finais.

A rota definitiva do lettering, fonte autoral e model sheet seguem pendentes. O contrato `doc/contracts/visual_source_of_truth_branding_splash_v3.json` trava apenas a direcao WIP autorizada; nao libera arte final. O fundo atual usa 610 tiles unicos frente ao alvo curatorial de 20-40, ponto explicito para reautoria/otimizacao futura.

## Referencias de oficio

- Xemu startup identity: energia azul e cadencia de lockup; nao copiar arte.
- A barra viva em `doc/03_art/18_live_scene_bar.md` define criterios de oficio, nao fonte de pixels.
- Real Bout Fatal Fury Genesis e KOF Mega Drive permanecem apenas referencias de oficio; sprites, personagens, cenas, pixels e IP nao serao copiados.

## Limites de claim

Estado: em desenvolvimento no laboratorio. O build/ROM/hash, capturas selecionadas e medicao local de scanline estao em `out/logs/splash_v3_visual_preview_report_20261013.json` e `out/logs/splash_v3_scanline_visual_runtime_20261013.json`. O gate global segue bloqueado por espelhos `runtime_probe` externos; residencia total, VBlank/DMA, CPU, DAC, FPS sustentado e qualidade final nao estao fechados. FORJA V2 e o template canonico permanecem intactos.
