# Auditoria de erros, performance e divergencia de worktree — 2026-10-21

Status: observacao read-only, sem build, sem emulador, sem promocao canonica.
Autor: Claude (Opus 5.5), sessao de auditoria pedida pelo usuario.

## 1. Divergencias que fazem o agente "nao localizar" o estado

1. **`out/` nao lista (EIO).** `ls out` retorna `Erro de entrada/saida` no host Linux
   (`/dev/mmcblk0p1`, fuseblk/ntfs-3g). Arquivos por nome direto abrem (`out/rom.bin` ok),
   mas `out/rom.out`, `out/symbol.txt` nao existem. Qualquer agente que faca `ls`/`find`/glob
   em `out/` falha e conclui que "nao ha build". Causa provavel: indice de diretorio NTFS
   corrompido -> rodar `chkdsk /f` no Windows (ntfsfix nao repara indice). Nao corrigido aqui.
2. **`out/rom.bin` nao e build do source atual.** mtime 2026-09-26, SHA
   `1b66cd1d...a7c8` = a "ROM principal preservada" do memory bank. O source tem
   31 arquivos modificados (+7713/-2042) e ~15 novos (menu_chrome, scene_title, scene_options,
   session_rules, diagnostic_sram_layout, mgres_*.rs...) com mtime ate 2026-10-21.
   A ROM principal e intencionalmente congelada; as ROMs atuais vivem em
   `out/work_runs/*` (inacessivel pelo item 1). Regra: nunca medir `out/rom.bin` como
   se representasse o worktree.
3. **Nada do trabalho desde 26/09 esta commitado neste projeto:** 63 `M` + 260 `??`
   (maior parte doc/agent_learning, doc/build_routes, doc/mugen). HEAD `0d88ec3e` em
   `feat/mugenesis-impact-fx-v2`. Ha mais 4 worktrees do mesmo commit
   (`Mugenesis_Menu_Worktree_20261002` e 3 em /tmp marcados prunable) — frentes paralelas
   (menu/screenpack, coverage, ryu tile, PR21/22) que tocam os mesmos arquivos.
4. **Otimizacao pronta mas desligada:** `MG_ANIM_PREFIX_TIME` existe em `src/mg/mg_vm.c`
   e nas tabelas geradas de Ken/Ryu (`anim_time_starts`), mas nao e definido em
   `inc/mg_config.h` nem no build. O memory bank diz "presente"; ninguem mede se esta ativo.

## 2. Oportunidades de performance (rota conservada: 57,552 fps, meta 60)

| # | Local | Achado | Ganho esperado |
|---|-------|--------|----------------|
| P1 | `inc/mg_config.h` | Ligar `MG_ANIM_PREFIX_TIME` (tabelas ja geradas). Censo host: 321 chamadas/8.330 iteracoes em 1.200 ticks de `elem_start` linear. | O(n)->O(1) em AnimElemTime; medir no BlastEm (PC sampler) antes de promover. |
| P2 | `src/mg/mg_vm.c:94` | `% loop_len` em s32 -> `__modsi3` (libgcc, centenas de ciclos) em todo `AnimElemNo(ahead)` que passa do total. Cachear `anim_loop_base` por anim (ou tabela gerada) e usar subtracao quando `t-total < loop_len`. | Pequeno, mas no caminho do trigger. |
| P3 | `src/mg/mg_vm.c:fx_div` | Duas divisoes 32/32 (software, ~700 ciclos cada) por `MG_OP_DIV`. Quando `ub < 0x10000` usar `divu.w` (u32/u16). | Medio, depende da frequencia de `/` nas expressoes. |
| P4 | `src/mg/mg_fight.c:frames_collide` | `world_box` do defensor e recalculado para cada caixa do atacante (i*j). Pre-computar as caixas clsn2 uma vez por chamada (n<=~4). | Pequeno. |
| P5 | H40 / FX80 | Gargalo real documentado: 5/5 checkpoints >320 px com 8060 ativo, noFX cabe. Nao e CPU, e SAT/linha. Ja ha rota em `doc/active_iteration.json`. | — |

HUD (`fight_hud.c`) ja e cacheado por valor/tile; nao e alvo.
`MG_findAnim/MG_findState` ja sao busca binaria.

## 3. Possiveis erros

- **E1 (plausivel)** `src/mg/mg_fight.c:1619-1628` projetil x projetil: depois de
  `p1->active = 0` o laco interno continua, entao um projetil do P1 anula *todos* os do P2
  sobrepostos. Falta `break`; e MUGEN usa `ProjPriority` (decrementa, so anula no empate).
- **E2** `out/` com EIO e risco de perda de evidencias de `out/work_runs` (hashes citados
  no ledger podem ficar irrecuperaveis). Backup antes de qualquer reparo.

## 4. Aprendizados para curadoria

- Antes de diagnosticar, testar `ls out` — EIO aqui nao e "sem build".
- `out/rom.bin` = ROM principal congelada; o worktree diverge por desenho. Ler
  `doc/active_iteration.json` (iteration 30) para saber qual ROM diagnostica e a atual.
- Otimizacao condicionada a `#ifdef` precisa de um gate que verifique se o define
  chega na build — senao vira "presente" no memory bank e inativa na ROM.
- Varias frentes no mesmo commit base sem commits intermediarios: harmonizar exige
  primeiro um commit/branch por frente; hoje nao ha como atribuir cada diff a uma frente.

## 5. Execucao (mesma data, segunda rodada)

### Harmonizacao
- **Causa raiz de "nada commitado desde 29/09":** `.git/index.lock` de 0 bytes, mtime
  2026-10-07 10:08. Todo `git add`/`commit` de qualquer agente falhava; o trabalho de
  todas as frentes ficou so no worktree. Removido (sem processo git escrevendo).
- **Segundo diretorio corrompido:** `.git/objects/52` da EIO como `out/`. Blob com hash
  `52...` nao entra no repositorio. Afetado agora: 
  `doc/agent_learning/fight_base_tileset_dma_same_frame_pairs_20261009.md`.
- Commits sem edicao de conteudo:
  - `53f7cd03` tools/mugen2sgdk_forge (51 M + 92 novos, entre eles os geradores
    `anim_timing`, `native_*`, `condition_cache`, `boolean_expr`, que nao tinham historico).
  - `7a62b4c9` codigo do jogo (62 arquivos).
  - `59165fbf` docs de texto (149 .md + 106 .json).
- Deixados fora de proposito: `doc/agent_learning/evidence/` (audio.raw de 26-31 MB,
  capturas), zips (ate 148 MB), `rascunho/`, `out/`, `res/mgres_*.rs` (intermediario
  do rescomp com pixels de terceiros, ja coberto pelo espirito do .gitignore).
- Fora do escopo Mugenesis e intocado: 38 delecoes em `.agents/skills/` (ponte de skills),
  mudancas em `tools/sgdk_wrapper/.agent/`, outros projetos. Precisam de dono.
- Worktrees em /tmp marcados prunable nao foram removidos (podem ter trabalho).

### Melhorias implementadas
| Item | Arquivos | Prova |
|------|----------|-------|
| P1 `MG_ANIM_PREFIX_TIME` ligado | `inc/mg_config.h` | tabela = varredura em 1435/1435 elementos (Ken 309, Ryu 1126); simbolos no ELF da candidata |
| P2 `elem_at` sem `%` no caso comum | `runtime/mg_vm.c` + `src/mg/mg_vm.c` | semantica identica (`over` em [0, loop_len) sem divisao) |
| E1 anulacao de projetil para no primeiro par | `runtime/mg_fight.c` + `src/mg/mg_fight.c` | revisao de codigo; nao ha teste dedicado |

- Build: `rascunho/harmonize_20261021/base` -> `43a29c82...11f6` (= ROM r3 do changelog,
  build reprodutivel); `cand` -> `439cf349...05e6`; 169 warnings nos dois.
- Host: 61 pass / 6 fail / 1 skip; as 6 falhas existem na base (digest de estado no
  teste `native_condition_cache...`), entao nao sao regressao desta mudanca, mas o
  digest esta quebrado e ninguem estava vendo.
- `test_anim_prefix_time.py` nao roda: fixture em `test_native_hitdef.py:33` nao acha
  tabela no gerado atual. Quebra anterior.

### Nao feito (precisa de medicao antes)
- P3 `fx_div` com `divu.w` e P4 caixas pre-computadas em `frames_collide`: ganho
  depende de frequencia; medir com PC sampler (nao runtime_probe) antes.
- Ganho real em fps de P1/P2: sem BlastEm nesta rodada.
- E1 ainda nao implementa `ProjPriority` do MUGEN.

### Aprendizados para curadoria
1. Antes de concluir "ninguem commitou", olhar `.git/index.lock` e a data dele.
2. EIO em diretorio NTFS no Linux e por pasta: testar subpastas antes de desistir;
   `.git/objects/xx` pode estar no mesmo estado e quebra `git add` de forma aleatoria
   (depende do hash do arquivo).
3. Build do Mugenesis com `out/` danificado: copiar src/inc/res/*.bat para
   `rascunho/<run>/` e rodar o wine bridge com `--project-root` no clone. O wrapper
   recusa `--output-dir` fora de `out/profiling|tests/<run>`.
4. Hash identico ao de uma ROM ja registrada prova que o snapshot e o estado daquela ROM.
5. Separar o WIP alheio das proprias edicoes: backup pre-edicao, restaurar, commitar o
   WIP, conferir que nada mudou (`cmp`) e reaplicar.
