# Registro de lacuna visual — Splash V3

Data: 2026-10-12  
Owner: laboratorio BRANDING_SPLASH_V3  
Estado: em desenvolvimento; nenhuma promocao visual.

## Evidencia atual

- O storyboard `doc/branding_v3_cinematic_storyboard.json` descreve sete estados em 240 quadros NTSC: escuro/silencio, energia azul, convergencia em SGDK, preenchimento, entrada de FORGE, faixa direcional e fade/teardown.
- A ROM V015 observada em BlastEm mostra telemetria de audio e nao a cena V3. A ROM canonica continua sendo a baseline FORJA V2.
- `art_diagnostic_report.json` encontrou 16 recursos ativos no `.res`: todos tecnicamente legiveis, sem ausencias ou bloqueios de conversao. Sao recursos herdados/introdutorios; isso nao comprova os assets previstos para V3.
- Existem dois previews de lettering (`rascunho/visual_lab/branding_v3_lettering_plate_preview_ai_v001.png` e `..._v002.png`). O manifesto os classifica como `visual_lab_control`; nao sao fontes premium, assets de producao ou arte aprovada.
- Foi criado `rascunho/visual_lab/branding_v3_backdrop_concept_20261012.png` como estudo de composicao. Ele traz shards azul/ciano nas bordas, um arco direcional e espaco negativo central; permanece RGB/high-res e nao e asset VDP.
- O manifesto de fonte premium de V3 tem `sources: []`, `source_route: pending_human_choice` e `production_source_ready: false`.
- A matriz preliminar de estilo recomenda `vibrant_16bit_pixel` como ancora tecnica para clusters limpos e contraste arcade; esta recomendacao nao e aprovacao de producao. Ver `splash_v3_style_candidate_matrix_20261012.json` e `splash_v3_art_direction_decision_record_20261012.json`.

## Lacunas para implementar

1. Resolver a rota do master tipografico e criar/revisar um model sheet de SGDK/FORGE.
2. Definir e autorar o fundo de profundidade para BG_B e a superficie de palco limpa em BG_A.
3. Traduzir o campo de energia e particulas para arte indexada nativa; a animacao precisa ler como ondas que se expandem e convergem, nao como pontos decorativos estaticos.
4. Fechar anchors e tempos de entrada/saida dos dois wordmarks com a arte escolhida.
5. Fechar a faixa de luz, brilho, fill e fade com paletas e ownership explicitos.
6. Medir cada estado com a fonte de medicao liberada; depois ajustar a coreografia ao budget medido.
7. Integrar a cena ao runtime sem substituir a baseline V2; construir uma ROM isolada e observar o ciclo completo em BlastEm.

## Criterios visuais de revisao

- Identidade do logo reconhecivel em 320x224 e no screenshot sem ampliacao.
- Hierarquia: energia conduz o olhar para SGDK; FORGE completa o lockup; o fundo nao compete com os nomes.
- Cristalino significa clusters definidos, brilho azul/ciano e separacao de planos, sem blur/glow difuso que desapareca no VDP.
- Movimento precisa ter ritmo e direcao: expansao, retorno, resolucao da marca, sweep e fade com saidas visiveis.
- Paleta, grade 8x8, residencia, sprites por scanline, VRAM/DMA/CPU e contraste devem ser medidos com ferramentas cujo gate esteja liberado.
- Aprovar um preview/controle nao promove automaticamente pixels para `res` nem aceita o model sheet.

## Bloqueios vigentes

- Rota de lettering nao escolhida; o manifesto registra duas opcoes e recomenda lettering pixel autoral.
- Model sheet humano aprovado ainda nao existe.
- A guarda global de medicao esta bloqueada por `project_source_mirror_stale` (20 copias ativas desatualizadas; 30/30 self-checks passaram). A varredura exploratoria de 990 entradas foi invalidada e nao deve ser usada para decidir producao.
- Nao ha assets finais, runtime visual V3, evidencia visual da cena V3 nem budget aprovado.

## Proximo handoff

Curador visual: resolver a rota do lettering e revisar um model sheet antes de pixels de producao. Owner tecnico: limpar o bloqueio da guarda de medicao no escopo autorizado, depois repetir coreografia, scanline, tile residency e budget. Runtime owner: integrar apenas assets aceitos em cena isolada; preservar V2 ate o gate completo.
