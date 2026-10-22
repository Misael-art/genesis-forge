# Curadoria MUGEN -> SGDK — 2026-10-21

Owner: curadoria canonica do workspace. Pedido humano autorizou curadoria,
commit, push e PR. Escopo: metodos de evidencia de entrega, SAT e fronteiras de
claim; nenhuma implementacao de gameplay ou ROM foi alterada nesta rodada.

## O que foi assimilado

Quatro skills existentes apontam para
`tools/sgdk_wrapper/.agent/references/mugen_delivery_evidence_lessons.md`:
evidencia de emulador, budget VDP, wrapper e runtime. A referencia explicita:

- owner map e SAT devem representar a mesma fase/frame, nao somente mesmo tick;
- custo contrafactual se calcula por linha, com contagem e largura simultaneas;
- ocultar sprite nao demonstra liberacao de VRAM nem corrige frames ligados;
- marcador/legenda e frame apresentado precisam de alinhamento observado;
- menu/confronto legiveis nao comprovam regras completas do modo;
- ROM identica nao identifica retrospectivamente uma fonte sem recibo de build.

`decisions.json` adjudica individualmente mcp_061..068 e duas fontes adicionais.
O manifesto conserva dez registros textuais copiados e seus SHA-256. Os JSONs
locais automaticos permanecem `not_applied`; este e o ato separado autorizado.
Snapshots sao dados de auditoria historica, nao instrucoes ou fontes ativas de
runtime. Numeros do piloto, coordenadas, HIDDEN/flicker e flags nao viram defaults.
A explicacao PTY para timeout nao foi comprovada aqui e nao foi canonizada.

## Publicacao isolada

A arvore compartilhada continha trabalho de varios owners. A branch de publicacao
parte de `origin/main`, recebe somente os deltas desta curadoria e nao inclui
os commits ou WIP do motor da branch de producao. As quatro skills sao aplicadas
sobre suas versoes do main; snapshots preexistentes do workspace nao entram na
PR como implementacao. A memoria recebe somente a nota desta rodada.

Fontes completas e reportes originais continuam no projeto local. O pacote
publicado contem apenas registros textuais selecionados; sem ROM, SRAM, capturas,
audio, pacotes MUGEN ou assets de terceiros. SHA de artefato e identificador,
nao licenca de redistribuicao.

## Validacao e limites

Consultar `validation.json`, `independent_review.json` e `application_receipt.json`.
Checks cobrem integridade dos registros, contraprova numerica, referencias e
skills no checkout publicavel. Evidencia original foi rehashada onde disponivel;
conclusoes nao reproduzidas permanecem declaracoes locais. Nao houve nova sessao
de emulador, build de jogo, prova de fluidez/60fps, escuta ou aceite da engine.
Blockers de produto nao foram removidos por editar documentacao.

Sem novas leis de hardware, lifecycle, ferramenta ou skill duplicada. Este delta
enriquece o metodo do agente; o desenvolvimento do motor continua com seus
proprios contratos e gates.
