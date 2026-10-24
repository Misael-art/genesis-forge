# Handoff para outro host — MUGEN, OpenBOR e wrapper

Owner: curador do workspace. Base de todos os paths: raiz do workspace.
Data: 2026-10-24. Esta tarefa prepara ambiente e continuidade; nao implementa
gameplay nem transforma a pausa anterior em aprovacao de engine completa.

## Diagnostico que o proximo agente deve entender

1. A arvore compartilhada tem centenas de deltas e fontes nao commitadas. HEAD
   `99395ee0` e a branch `feat/mugenesis-impact-fx-v2` nao descrevem sozinhos o
   estado atual. PRs de curadoria 23/24 documentam escopos especificos, sem
   publicar automaticamente toda a producao M5/OpenBOR. Nao usar `git add -A`,
   reset/clean forcado nem upload publico do pacote privado de transferencia.
2. Havia preparo de ferramentas consultivas (`pwsh`, uv, Graphify), mas faltava
   uma entrada unica para host sem instalacao previa e uma transferencia
   verificavel do working tree. Agora ha instalador e ferramenta de pacote;
   o runbook principal e `doc/HOST_BOOTSTRAP_AND_CONTINUITY.md`.
3. O SDK canonico e `sdk/sgdk-2.11`. O SDK local contem deltas historicos e
   mismatch conhecido de compilador/biblioteca LTO. Linux usa staging separado
   e biblioteca reconstruida sem LTO, pelo wrapper; Windows deve satisfazer
   seu seletor proprio. Nunca corrigir SDK sobrescrevendo a origem congelada.
4. O mount SD registrou EIO em arvores antigas, inclusive Git e
   `out.broken_20261022`. Isso nao e bug de combate nem motivo para criar mais
   arvores desconectadas. Preservar origem; destino novo; hash e parent claros.
   Nao apagar a prova nem chamar higiene de aprovada porque o erro sumiu.
5. Ha estados auxiliares e caminhos antigos absolutos em evidencias/scripts.
   Preservar recibo historico; recalcular paths de execucao no destino. Scripts
   antigos nao devem ser disparados cegamente, nem um report de outro host
   deve fechar o gate atual. O fallback `SGDK_templates/base-elite` nao existe
   neste checkout; o template do wrapper `tools/sgdk_wrapper/modelo/` existe.
6. Pads virtuais e displays privados resolvem a separacao operacional somente
   no escopo aceito. Preflight P1/P2 deve observar a ROM: BlastEm pode trocar
   portas na primeira atividade do segundo pad. ACK recebido nao e gameplay.
   F32LE/48k stereo com atividade nao prova escuta, mix ou sincronismo.
7. **Novo blocker de identidade**: a instalacao consultada agora e BlastEm
   Flatpak **1.0**, commit
   `855ff0ece6f336f5150e6cff5cd126e2fa48a825d711ed35ce74f25b58184469`,
   disponivel no remoto. O antigo commit 0.6.2 do catalogo Linux retorna 404.
   `session_coordinator.py` ainda le a identidade antiga ao selar, sem fixar a
   identidade do emulador no inicio da sessao. Antes de novos claims de captura,
   vincular ref/commit/binario efetivamente lancados, verificar persistencia da
   identidade e requalificar a rota. Nao reescrever selos historicos para parecer
   que usaram a versao nova. O novo bootstrap instala a identidade observada e
   reporta `capture_identity_gate=blocked_legacy_catalog_identity_drift`.
8. Wine app commit `3fd85461...` esta instalado, mas seu runtime
   `org.freedesktop.Platform/x86_64/24.08` **nao esta instalado** neste host.
   Portanto `flatpak info` do app sozinho nao prova capacidade de executar.
   O bootstrap verifica/instala runtime tambem para app preexistente e executa
   probe Wine; a reparacao real por apt/Flatpak aqui nao foi executada.
9. O mount SD e FUSE e recusou `renameat2(RENAME_NOREPLACE)` de diretorio com
   EINVAL. Publicacao de arquivo por hardlink passou. Guardar o TAR no SD e
   valido; **restaurar/instalar em filesystem Linux nativo no host novo**.
   O instalador agora sonda isso antes dos downloads. Nao relaxar o no-clobber
   para contornar o filesystem, nem sobrescrever diretorio vazio concorrente.

Foi exportado backup privado do app BlastEm instalado (sem runtime):
`out/curation/2026_10_24_host_migration/blastem_1_0_observed.flatpak`,
SHA `e4d88d1940938b61959b73dbbc9700d4b6e27c2da1074f69ae9a8be476efbcce`.
Esse bundle nao qualifica ROM nem e substituto dos runtimes/dependencias.
`host_diagnosis.json` no mesmo owner preserva os resultados de consulta.
O relato de instalacao portavel bem-sucedida nao e prova da cadeia Wine nem de
captura completa. A requalificacao acima precede qualquer entrega no destino.

## Estado MUGEN para SGDK

Owner engine: `tools/mugen2sgdk_forge`. Owner consumidor P:
`SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]`.
Consumidor independente R:
`SGDK_projects/_agent_laboratory/MUGEN_REUSE_PROBE [VER.001] [SGDK 211] [GEN] [LAB] [FIGHTING]`.

Ler primeiro `P/doc/engine_handoff_m5.md`, `P/doc/engine_current_state.json`,
`P/doc/10-memory-bank.md` e o backlog/checkpoint em
`P/out/reviews/engine_resilience_m5_20261024/` (P e alias so neste documento).

ROM canonica atual **build_v008**, 3.538.944 bytes, SHA-256:
`ff909dbf499b23bbc06c7951e4bdde698834a4eb2ac66ff9a1e7ec3575b533b9`.
E parcial; nao release, engine completa nem prova de 60fps. `out/rom.bin`,
acervo v008 e candidata original foram vinculados; fonte exata e a capsula
`frozen_normal_font_r17/manifest.json`, tree
`84350f683f8bec98a9832b7d90a5731555eed64aa99705a1317872ea14e204fa`,
402 entradas (blobs deduplicados). O checkout contem opt-ins posteriores,
desligados por padrao. Nao atribuir esses deltas a v008.

O reparo do overlay removeu buffer automatico de 3072B contra stack supervisor
2048B, usando BSS, main-only, upload CPU sincrono, sem mudar bitmap/fallback.
Watch APLIB confirmou dano anterior a sentinela. Canary e piso observado,
nao teto seguro. Numero/localizacao de buffers deste caso nao vira receita
universal; revisar lifetime, reentrancia, IRQ e heap antes de generalizar.

BGFX tem admissao finita e teardown assincrono. Quando `MG_fightEnd()==FALSE`,
preservar owner, apresentar/drenar SPR/queue/VBlank e tentar novamente antes
de liberar cena/audio. O teste no R nao autoriza sobrescrever runtime custom P.

Backlog: **69 IDs**, 53 aceites abertos, 11 aceites host e 5 implementacoes
delimitadas. Converter 0.3.6, runtime 0.5.0 e ABI 1 sao identidades separadas.
Wheel final com os ultimos modulos ainda exige instalacao fora do checkout,
conversao/receita real, upgrade de R e suite final por hash.

Prioridades apos pedido de retomada de gameplay:

1. **Bonus/DRAWGAME (F01/F02/M4V03)**: corrigir resultado terminal e ownership
   do HUD. Reproduzir sucesso/falha/timeout, legibilidade, revanche, retorno e
   botoes mantidos em mesma ROM com input observado.
2. **Pack/allocator**: normalizar a base W/E do envelope antes de integrar.
   ALL21 offline e 108 bitmaps/12 C checks nao provam runtime. Medir transientes,
   reserva maxima de definicao, ordem, VRAM e janela inteira de 1200 frames com
   DMA fresco/SAT. H40 exige ao mesmo tempo 20 links/320px e total 80 SAT;
   SGDK limita 16 cortes por AnimationFrame. Nao usar flicker para esconder erro.
3. **ALCP2**: terminar falhas 1–7/tardias, commits por palavra, witnesses resealed,
   startup/handoff de audio e revisao antes de qualificar no R/SDK/BlastEm.
4. **R19**: terminar dois traces humanos byte shared/custom; equivalencia antes
   de build. Provar remocao de helpers no ELF, ativacao e ganho repetido com
   audio. R18 regrediu e segue OFF. Controle diagnostico ~52,05 updates/s nao
   e 60fps, nem cadencia da v008. Nao reutilizar hipoteses rejeitadas sem causa.
5. **Paleta/namespace**: C10/F09/M4V01 e guarda ROSTER tem reparos host, mas
   assets antigos da v008 nao foram regenerados. Validar traje/espelho/revanche/
   troca de lado/retorno pelo pacote final. RGB igual nao unifica paleta local.
6. Continuar todos os IDs de semantica, containers/arquivos/controllers/triggers,
   modos e reuso, sem declarar parser universal por amostra. Charged release
   64–255 segue sem capacidade; strict rejeitando >63 e protecao, nao implementacao.

SWNW2 precisa labels 91..1290, sem perdas e DMA fresco por frame. O reparse
historico registrou 21 eventos; pior scanline frame174 (384px) e pico DMA
frame170 sao pontos diferentes. Instrumentacao pesada nao mede produto.
Suite congelada pre-font: 1007 coletados/1005 pass/2 skips; deltas posteriores
sao runs distintos. Suite final continua pendente. Nao somar runs para verde.

Sete eixos v008: build e boot BlastEm observados, gameplay parcial, validation
global limpo ausente, 60fps nao provados, audio apenas atividade digital,
memoria atualizada. Mastering com checks globais abertos; freshness tinha
2 stale/3 required missing. Higiene interrompida nao e aprovada. Nao rebuildar
ou atualizar timestamps para esconder drift.

## Estado OpenBOR para SGDK

Owner engine: `tools/openbor2sgdk_forge`. Consumidor O:
`SGDK_projects/OpenBOR_Demo [VER.001] [SGDK 211] [GEN] [GAME] [BEAT_EM_UP]`.
Baseline ativa:
`60526807ce963ee2d9022600f7266715851911ebf7df29ed0c98af08aed8e1ad`.
Ler `O/doc/10-memory-bank.md`, `O/doc/active_iteration.json`,
`O/doc/openbor/curation_followup_20261015.md` e
`O/doc/openbor/display_fit_transfer_20261022.json`.

O motor importa PAK32/64, inspeciona perfil, converte imagens/IR e emite dados
C deterministicos; isso nao conecta automaticamente o consumidor SGDK nem
implementa streaming runtime/semantica de scripts arbitrarios. No perfil GAL
TOWN1, 8/26 comandos estavam adaptados e 18 recusados explicitamente. Sete
perfis declarados nao sao sete jogos equivalentes implementados.

TEXT tem candidata; ITEM (linha58) precisa owner/semantica, permanece fail-closed.
O readback VRAM de 65536B no frame147 nao prova mascara: input rejeitado e ROM
ainda no menu. Qualificar rota de input, observar a fase e so depois reconciliar
VRAM/DMA/scanline. Nenhuma evidencia antiga de captura inteira vale como fase
correta. Manter baseline e candidata separadas e ligada ao seu hash.

Combate, ponte/queda/morte/retorno tiveram evidencias em segmentos distintos;
nao repetir indefinidamente so esse smoke nem alegar fase completa por ele.
Fila de spawn, itens, outros inimigos, magias, mecanicas e reuso devem evoluir
por matriz fonte->IR->consumidor->prova, com criterios finitos por etapa.

Audio R3 tem duck estatico na janela, nao audicao em ROM. Tom controle 440Hz
nao tinha ROM/PCM: tentativas morreram por runtime D-Bus/espaco antes do app.
No host novo, testar controle antes de atribuir falha ao jogo. Display-fit de
22/10 mediu origem e decidiu **nao aplicar escala**. Nao copiar 5/6 do MUGEN
nem aplicar 320/480 e 224/272 automaticamente ao OpenBOR. Cell80x96 e canvas
nao sao resolucao nominal/interpretação de aspecto equivalentes.

Audit do aprendizado: 147 licoes/109 candidatas com warning
`evidence_rom_hash_mismatch`. Preservar essa ressalva. Nao promover revisao
historica a evidencia nova no novo host.

## Curadoria e disciplina de desenvolvimento

39 licoes M5 foram adjudicadas: 7 prioritarias, 14 refinamentos delimitados,
15 duplicatas/resultados locais, 2 contraexemplos com instrumento por revisar
e 1 decisao humana local de pausa/promocao. Todas not_applied. Catalogo e
provas no lote `doc/curation/2026_10_24_learning_investigation/` (PR24).

Generalizar metodo, nao constantes do caso: stack/canary, janela completa,
admissao/teardown, paleta/namespace, reserva SDK/transientes, origem de display,
gerador C pinned, audio por formato, invariantes fisicas e pacote/snapshot.
Mega Drive e base tecnica mensuravel; nao substituir dificuldade por suposto
limite. Medir degrau seguinte, justificar composicao e preservar legibilidade.

Cada incremento precisa pergunta, owner, baseline/hash, aceite finito e proxima
acao causal. Um produtor por path. Paralelizar auditorias e implementacoes
isoladas somente com leases/dependencias; coordenador integra/revalida e mantem
memoria/changelog. Review nao substitui teste, nem se aprova a propria entrega.
Registrar licao quando superar obstaculo; candidato universal so apos dedupe,
negativos, reproducao e autorizacao. Nao criar novas arvores para evitar causa.

## Prompt de retomada para entregar ao novo agente

> Assuma responsabilidade senior pelo workspace restaurado. Leia AGENTS,
> `doc/HOST_BOOTSTRAP_AND_CONTINUITY.md` e este handoff; depois leia os documentos
> operacionais do projeto escolhido. Confira recibo da transferencia e fontes
> congeladas; nao suponha que HEAD ou fonte atual reproduza a ROM canonica.
> Prepare o host pela entrada do wrapper, ative seu ambiente e registre o
> resultado real. Instalacao, build, emulacao, jogabilidade, audio, performance
> e budget sao aceites separados. Antes de gameplay, confirme que o usuario
> retomou esse projeto; a pausa anterior nao e removida por migracao de host.
> No MUGEN, comece pela matriz M5 e Bonus, depois frentes pack/allocator/R19 e
> wheel/reuso conforme dependencias; no OpenBOR, qualifique input e fase TEXT,
> conecte capacidades da engine ao consumidor e continue a matriz de comandos.
> Preserve baseline e flags experimentais. Para cada item: reproduza, defina
> aceite, implemente a menor correcao causal, execute negativos/regressoes,
> gere preview rastreavel, obtenha review focado e consuma o feedback antes de
> avancar. Nao repetir smoke sem remover blocker. Use subagentes independentes
> quando houver ramos longos seguros, limites do host e leases separados.
> Mantenha fontes, inputs, reports e alternativas nos destinos canonicos;
> preserve hashes e parent dos ramos. Atualize memoria/changelog e capture
> aprendizado local por superacao. Relate lacunas com precisao e continue nos
> itens independentes; nao declare engine completa/AA/60fps sem as respectivas
> provas e nao reduza escopo para encerrar o backlog.
