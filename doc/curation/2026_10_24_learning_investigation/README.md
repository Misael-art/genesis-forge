# Investigacao de novas licoes para curadoria — 2026-10-24

Owner: curador do workspace. Base: raiz do workspace. Pedido atual e de
investigacao; nenhuma skill, regra, ferramenta de producao, runtime ou ROM
foi modificada. O desenvolvimento M5 continua pausado por pedido do usuario.
A investigacao nao executou stage, commit, push, promotion ou alteracao de proposals locais.
A publicacao deste pacote foi autorizada depois, em pedido explicito de commit e PR.

## Resultado

Ha material novo aproveitavel, especialmente no MUGEN M5. As 39 licoes foram
adjudicadas individualmente: 7 candidatas prioritarias de metodo, 14 refinamentos
com escopo delimitado, 15 duplicatas de metodo existente/resultados locais,
2 contraexemplos com reparo do instrumento ainda pendente e 1 acao autorizada
local que nao deve virar regra geral. Isso nao corresponde a 39 novas skills.

`candidates.json` agrupa a investigacao em dez frentes com owner existente,
prova disponivel, menor delta, aceite e limites. Prioridades praticas:

1. Stack de boot e canary: a fonte tinha buffer automatico de 3072B, maior que
   os 2048B supervisor reservados no caso. O reparo local usa BSS com lifetime
   e upload CPU sincrono. Generalizar o metodo de auditoria/medicao; nunca os
   numeros ou a receita static sem verificar reentrancia. Canary e piso de uso
   observado, nao teto seguro; mapa pontual do heap nao prova toda sua vida.
2. Coletores de janela: labels completos, DMA fresco tambem nos frames normais,
   publicacao final e rejeicao de perdas/truncamento. Reparse do SRAM real
   confirmou 1200 labels e 21 eventos guardados, sem nova emulacao. O instrumento
   e especializado; adaptar seu contrato antes de mover parser ao core global.
3. Ownership assincrono e admissao: a regra atual de drain pode ficar mais
   concreta sobre pending/retry/completed, dono preservado, apresentacao durante
   drain e falha transacional. Limites de jobs/arena/bytes derivam do contrato
   real; 7200 nao e uma constante de hardware universal.
4. Identidade de paleta e namespace: RGB igual nao torna paleta local equivalente
   a corpo/ACT. Nomes gerados devem recusar colisao normalizada antes de qualquer
   publicacao em todos os entrypoints. Fontes/fixtures SFFv1 e SFFv2 conservam
   alcances diferentes e pacote final ainda precisa teste fora do checkout.

## Outras frentes

- SDK e metasprites: reserva maxima da definicao pode superar SAT do frame
  ativo; medir transientes de troca, partes, quatro flips e DMA no mesmo frame.
  ALL21 offline nao qualifica pack, allocator ou janela na ROM.
- Origem e escala: MUGEN e OpenBOR ja possuem metodo local que distingue
  framebuffer, canvas de empacotamento e celula. O OpenBOR tem contrato de
  transferencia de 22/10, embora seu memory bank operacional termine em 15/10.
  Seus 14 testes focais passaram. Nao transportar 5/6, FPS ou geometria entre
  engines; origem desconhecida nao ganha escala inventada e uma segunda
  conversao precisa ser impedida. Resolucao nominal sozinha nao decide aspecto.
- Gerador de C conhecido: binding deve resistir a comentarios/strings/splices,
  digraph/trigraph e sizeof; formato pinned nao e parser C universal. Revisoes
  e testemunhas estao preservadas; falta reexecutar esses casos antes do patch.
- Audio: F32LE nao e int16; variacao por canal/fronteira, incluindo DC estereo
  negativo. OpenBOR R3 tem estudo de duck ao longo da janela, nao escuta em ROM.
  Atividade digital, mix, loop, stop ACK e julgamento perceptivo sao eixos distintos.
- Ferramentas devem negar valores fisicamente impossiveis mesmo com checksum
  valido. O witness 8193 e util; ALCP2/R2 segue parcial, sem promocao do reparo.
- Wheel/ABI/runtime/fonte e suites precisam identidades separadas. A soma de
  runs de snapshots diferentes nao produz uma suite final inexistente.

## Deduplicacao e pontos que nao devem ser universalizados

A curadoria de 23/10 ja corrigiu agregacao de falhas/ausencias na CI e integrou
roster de regressoes; nao reabrir esse trabalho como descoberta nova. Comparacao
pareada, custo do observador, hash/source capsule, dois limites H40, input
observado e retry com ownership ja possuem owners e regras anteriores.

A proposta historica `mugen2sgdk_fidelity_matrix.*` ainda descreve SFFv1 no
commit de origem. Ela esta explicitamente marcada como proposta historica;
nao e prova de falta atual de SFFv2. Uma curadoria futura deve melhorar o
ponteiro para a matriz vigente sem reescrever o estado do commit antigo.

Pausar nao obriga promover ROM: m5_36 descreve uma escolha humana especifica.
A build_v008 e atual e parcial; seus 402 inputs e tres aliases de ROM foram
rehashados, nao rebuildados. Opt-ins posteriores nao pertencem a essa ROM.
Nao habilitar input nativo que regrediu, flicker para esconder overflow,
allocator/pack em staging ou limites locais por causa deste relatorio.

## Evidencia revalidada nesta investigacao

- MUGEN Learning Audit: 459 licoes/338 candidatas; zero warnings/missing.
- OpenBOR Learning Audit: 147 licoes/109 candidatas; conserva o warning
  `evidence_rom_hash_mismatch`. Esses totais incluem historico/duplicatas.
- 39 licoes M5: 52 vinculos em 32 arquivos unicos; todos os hashes conferem.
- Build_v008: 402/402 blobs da capsula conferem; ROM principal, arquivo
  build_v008 e candidata original possuem o mesmo SHA esperado.
- SWNW: self-check passou; ROM/SRAM de sessao preservada conferem e o parser
  releu 1200 frames91..1290, 21/21 eventos, lossless. Isso nao prova DMA fisico.
- 115 testes host focais passaram em quatro execucoes distintas: 42 contratos
  SAT/ID/paleta local, 58 SFFv2, 14 OpenBOR display/emissao e 1 overlay.
  Nao houve skip/falha nesses recortes, nem execucao da suite completa da engine.
- Conta de RAM e soma dos blocos do heap foram recalculadas; fonte atual do
  font workspace foi inspecionada. Watch 68000/ELF/repeticoes anteriores foram
  lidos e rehashados, sem nova execucao de target.

Reports originais: `out/curation/2026_10_24_learning_investigation/` no workspace.
O subconjunto publicado em [evidence/](evidence/) inclui XML, logs e verificacoes.
[evidence_manifest.json](evidence_manifest.json) liga cada copia ao SHA do original.
[publication_receipt.json](publication_receipt.json) delimita a publicacao.
Caminhos de ROM, capsulas e fontes nos reports identificam evidencia local; esses
artefatos nao sao distribuidos neste pacote. Hash confirma identidade, nao conclusao.

## Proximo ato de curadoria

Menor delta recomendado: enriquecer as referencias/skills dos quatro temas P1,
reusar testes existentes e ligar os negativos de instrumento ao roster de CI.
Depois tratar as frentes P2 em mudancas separadas, respeitando provas pendentes.
Nao criar outra arvore de skills, parser paralelo ou quota de genero.

Este e um parecer de investigacao com propostas `not_applied`. Nao qualifica
engine completa, arte AA/AAA, release, audio ou 60fps, nao retoma desenvolvimento
pausado e nao aplica patch canonico automaticamente.

## Publicacao

Branch documental isolada baseada em `main`, por pedido humano de commit e PR.
Este commit publica a investigacao e suas propostas ainda `not_applied`; nao
aplica as dez frentes aos skills nem altera motores, ROMs ou a pausa do M5.
Os 115 testes pertencem as quatro execucoes registradas da investigacao; na
publicacao foram revalidados arquivos, hashes, contagens e escopo do diff.
