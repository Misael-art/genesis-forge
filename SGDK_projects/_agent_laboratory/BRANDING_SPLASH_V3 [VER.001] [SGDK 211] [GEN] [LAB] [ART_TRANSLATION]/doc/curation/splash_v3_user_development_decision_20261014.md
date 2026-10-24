# Decisao de desenvolvimento do usuario — Splash V3 — 2026-10-14

## Decisao registrada

O usuario autorizou manter a Splash V3 **em desenvolvimento**, exige revisao futura para aprimoramento, pediu o registro dos criterios de curadoria e autorizou continuar a parte visual que falta.

Esta decisao autoriza trabalho WIP e preview isolado dentro do laboratorio. Ela nao aprova a qualidade musical ou visual final, os pixels atuais, o model sheet, a ROM de producao, a promocao do template, o arquivamento da FORJA V2 nem a migracao de projetos consumidores. Essas acoes continuam condicionadas a validacao completa e a uma decisao humana final especifica.

## Criterios de curadoria preservados

- Audio: assinatura curta, memoravel, positiva, heroica e energetica, com articulacao, pausas audiveis, lead destacado e acentos cristalinos breves. Evitar som abafado, monofonico, continuo ou monotonamente sustentado. Referencias Capcom/Konami sao emocionais; nao copiar melodias, logos ou timbres identificaveis.
- Historico de escuta: V012 e a referencia positiva; V013 e V014 foram rejeitadas por baixa qualidade/continuidade monotona; V016/VGM4 e a candidata corrente integrada ao V017, ainda sem escuta ou aprovacao final. A avaliacao deve ocorrer na ROM visual completa por pelo menos dois ciclos.
- Visual: silencio inicial, expansao azul com energia, convergencia legivel, revelacao clara de SGDK, FORGE subordinado, acento cristalino direcional e encerramento limpo. Preservar espaco negativo e leitura do lockup em 320x224.
- Refinamento pendente: reduzir/reautorizar o vocabulario do fundo, cujo alvo curatorial e 20-40 tiles reutilizaveis; avaliar densidade dos cristais, movimento, hierarquia, sweep, lettering e ancoragem das particulas.
- Validacao: observar dois ciclos completos da ROM exata, capturar o prompt e demonstrar replay, reouvir dois ciclos, medir VRAM/residency, DMA/VBlank, CPU, ownership DAC e 60fps sustentados com audio.

## Limite de promocao

A V3 permanece no laboratorio e todos os assets continuam placeholders. FORJA V2, ROM canonica, template e consumidores permanecem intocados. A futura promocao exige gates tecnicos e visuais completos, registro de evidencias ligadas ao hash final e nova aprovacao explicita do usuario.

## Atualizacao de execucao — 2026-10-14

> Registro historico da etapa de lettering B, anterior ao build V006 e a rodada corrente V017.

- B `faceted_crystal` foi ativada como recomendacao curatorial WIP nas placas de lettering do laboratorio. A direcao nao foi escolhida pelo usuario, nem aprovada como model sheet ou pixels finais. Baselines anteriores estao preservadas.
- A proveniencia passou para 21/21 simbolos e a residency do plano V005/B passou com 984 tiles H/V. O preview estatico 320x224 nao e captura de ROM.
- O build candidato B foi bloqueado antes de make porque `/run/user/1000` esta sem espaco disponivel e o Flatpak falha em `winepath`. Report `out/logs/splash_v3_lettering_b_build_block_20261014.json`. Nenhum temporario compartilhado foi apagado.
- A revisao de emulador, audio, budgets, evidencia final e promocao continuam pendentes; FORJA V2 e template permanecem intactos.

## Atualizacao de execucao — rodada V017

- A Splash V3 permanece `em_desenvolvimento`; a revisao futura para aprimoramento e obrigatoria. Este registro nao muda a aprovacao de arte ou musica e nao autoriza promocao ou arquivamento.
- Avanco visual WIP: as 64 particulas convergem para celulas visiveis da placa SGDK atual. A geometria passou a medicao local em 13/20 sprites e 104/320 pixels por scanline na pior linha; anchors derivados do placeholder ainda exigem model sheet e revisao humana.
- Build ROM WIP: `out/rom.bin`, 393216 bytes, SHA-256 `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2`. A sequencia foi observada em amostras diagnosticas diretas do BlastEm; a captura nao tem selo canonico, marcadores exatos de quadro nem confirmacao de input ROM-side.
- O hold final mostra `A: REVER` e lockup preservado; dois screenshots de hold tem hashes iguais antes/depois do pedido de A. Isso nao substitui um trace de input independente ou uma captura de ciclo completo.
- Pontos e limites completos ficam em `doc/curation/splash_v3_visual_curation_record_20261014.md` e `out/logs/splash_v3_v017_visual_review_report_20261014.json`. FORJA V2, template canonico e consumidores continuam intactos.
