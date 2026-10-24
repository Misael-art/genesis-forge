# Instalacao e retomada em outro host

Owner: wrapper do workspace. Base dos paths dos comandos: raiz do workspace.
Guia de diagnostico/estado dos jogos e prompt de continuidade:
`doc/curation/2026_10_24_host_migration/handoff.md`.

## Caminho curto no novo Linux

Instalacao automatizada inicial: Linux x86-64, Debian 12/13 ou Ubuntu 24.04,
conta normal com sudo, internet e sessao de usuario D-Bus funcional. Instalar
e restaurar em filesystem Linux nativo (por exemplo ext4), com rename atomico
sem sobrescrita. O SD/FUSE atual recusou essa operacao; pode guardar o TAR,
mas nao e destino qualificado de instalacao/restauracao. O bootstrap sonda essa
capacidade antes dos downloads e falha explicitamente se faltar. A rota
completa precisa de 8 GiB livres **antes** de baixar runtimes Flatpak e fazer
staging do SDK. Reserve tambem espaco para a transferencia e sua extracao.
Outras distribuicoes podem provisionar os pacotes manualmente e passar
`--skip-system-packages`; isso nao qualifica a plataforma. Windows/macOS/ARM
nao possuem instalador novo qualificado nesta entrega. Nao escolher sistema
ou migrar o host inteiro automaticamente.

O repositorio pode ser obtido pela interface do GitHub como ZIP se ainda nao
houver Git instalado. Para recuperar **estes projetos no estado local atual**,
primeiro restaure o pacote privado descrito abaixo. Clonar `main` sozinho nao
recupera os deltas de M5, OpenBOR nem todas as ferramentas nao commitadas.

```bash
bash tools/sgdk_wrapper/bootstrap_host.sh
bash tools/sgdk_wrapper/bootstrap_host.sh --apply
source out/host_tools/activate.sh
rtk proxy pwsh -NoProfile -File tools/sgdk_wrapper/assert_agent_environment.ps1 -NoInstallMissing
```

Primeiro comando apenas diagnostica e produz plano/report. `--apply` instala
pacotes autenticados pelo apt, SDK 2.11 oficial, pwsh/JRE/RTK por SHA-256,
dependencias Python por lock com hashes, Flatpak Wine/BlastEm em escopo do
usuario, compila pads virtuais e chama o guard existente. Instala tambem o
BlastEm de diagnostico lado a lado via catalogo existente; ele nao substitui
a rota de entrega. O report fica em `out/logs/host_bootstrap_report.json`;
logs de cada passo em `out/host_tools/bootstrap_logs/`.

Comandos devem rodar como usuario desenvolvedor; sudo serve apenas ao apt.
Nenhum pip global, alteracao de perfil de shell, hook ou MCP global e instalado.
Java e PowerShell estao no workspace. As excecoes de escopo sao os pacotes apt
e os aplicativos/runtimes Flatpak no usuario. Codex/IDE e autenticação das
contas sao configuracoes pessoais, nao sao transportadas nem provisionadas.

Sem sudo ou apenas para preparar ferramentas portaveis:

```bash
bash tools/sgdk_wrapper/bootstrap_host.sh --apply --skip-system-packages --profile portable
source out/host_tools/activate.sh
```

Essa rota requer Python >=3.11 com venv e 7z ja instalados, e 2 GiB livres.
O status e `portable_only_system_and_emulator_pending`; nao significa cadeia
completa. No novo host, a primeira instalacao apt/Flatpak e primeiro boot real
sao aceites pendentes, mesmo que os testes portaveis deste host tenham passado.

## Identidade e manutencao

Pins de arquivos: `tools/sgdk_wrapper/bootstrap_host.json`. Dependencias Python:
`host_python_requirements.in` e `host_python_requirements.lock`. A mudanca
de versao e deliberada: resolver lock em revisao (`uv pip compile --universal
--python-version 3.11 --generate-hashes --no-annotate`), testar instalacao limpa
e repetir os probes. Nunca remover hashes para contornar incompatibilidade.

O SDK instalado originalmente neste host tem deltas locais e a biblioteca
GCC/LTO conhecida; ele pode ir no pacote privado para preservar a origem.
O instalador reconhece SDK preexistente como unmanaged, valida arquivos
obrigatorios e **nao o substitui**. O seletor de rota continua obrigatorio.
SDK novo oficial recebe recibo com hashes de todos os arquivos e e rechecado
na repeticao. Alteracao local ou instalacao parcial bloqueiam; investigar
em vez de apagar. SDK modificado nao e reparado por cima de fonte historica.

O novo pin BlastEm corresponde ao **1.0 instalado e observado em 24/10**.
O catalogo legado de captura ainda descreve 0.6.2 e aquele commit retorna 404.
O report do bootstrap sinaliza `capture_identity_gate` bloqueado: falta ligar
a identidade real do emulador ao inicio/fim da sessao e requalificar capturas.
Isso nao e resolvido renomeando evidencias anteriores. O backup privado do app
atual, sem runtime, acompanha a receita; os hashes estao no handoff.

Flatpaks existentes com outro commit bloqueiam antes de downgrade. Ref/commit
antigos indisponiveis tambem bloqueiam. Os pacotes apt e runtimes transitivos
do Flatpak seguem seus repositorios autenticados: nao se alega imagem de SO
bit a bit reproduzivel. Nao executar update global para consertar um projeto.

App Flatpak instalado sem seu runtime nao e um host pronto. O bootstrap
consulta o runtime de cada app, instala o que faltar e testa `wine --version`.
Isso trata a ausencia 24.08 encontrada neste host, sem alegar que um probe de
versao confirma build ou emulacao. Nao copiamos o prefixo Wine entre hosts.

O lock do workspace admite um instalador por vez; builds continuam serializados
pelo lock existente do Wine bridge. Comecar com `MAKEFLAGS=-j1`, um emulador e
um produtor; reviews independentes podem ser paralelos com leases separados.
O policy report orienta agentes, nao impoe quota global de RAM/CPU ao sistema.
Medir RAM, espaco do `/run/user/<uid>`, disco, carga e duracao antes de ampliar.

## Transferencia privada

O pacote contem fontes atuais selecionadas, inclusive arquivos ignorados/nao
commitados, inputs privados, assets autorizados, documentos e provas escolhidas.
Nunca anexa `.git`, venv/caches, sessoes vivas, sockets, `.env`, chaves PEM/KEY
ou estado de IDE. `.agent` local real e preservada; pontes sao recriadas.
Filtros de nomes nao substituem revisao do inventario por quem possui os dados.
O pacote nao e criptografado; guardar/transmitir por canal privado apropriado.

Receita desta migracao: `doc/curation/2026_10_24_host_migration/transfer_recipe.json`.
Ela nao e um backup integral dos outros jogos ou de todo o historico do host.
Para outros projetos, criar selecao explicita com `--include` e manter owner.

```bash
rtk proxy python3 tools/sgdk_wrapper/host_transfer.py plan \
  --recipe doc/curation/2026_10_24_host_migration/transfer_recipe.json \
  --output out/curation/2026_10_24_host_migration/transfer_inventory.json
rtk proxy python3 tools/sgdk_wrapper/host_transfer.py create \
  --recipe doc/curation/2026_10_24_host_migration/transfer_recipe.json \
  --output out/curation/2026_10_24_host_migration/forge_private_transfer.tar
```

Copiar o TAR e seu recibo `.tar.json` para o novo host. A publicacao e atomica
sem sobrescrever destino e recusa fonte que mude durante a copia. Arquivos
grandes permanecem streaming; catalogo e metadados tem limites explicitos.
Nao executar limpeza no host original depois de copiar: preservar ate a
restauracao, as provas e o primeiro build no destino terem sido conferidos.

No destino, com Python >=3.11 (se necessario instalar `python3` pelo gerenciador
do SO), usar o `host_transfer.py` e `bootstrap_host.py` desta PR ou de uma copia
confiavel. Substituir `<sha_do_recibo>` pelo hash do recibo transportado:

```bash
python3 tools/sgdk_wrapper/host_transfer.py verify \
  --archive /caminho/forge_private_transfer.tar --sha256 <sha_do_recibo>
python3 tools/sgdk_wrapper/host_transfer.py restore \
  --archive /caminho/forge_private_transfer.tar --sha256 <sha_do_recibo> \
  --destination /caminho/novo_workspace
```

O parent deve existir; destino deve ser novo. Todos os hashes/tamanhos/paths
sao conferidos antes da publicacao. Links/special files e membros nao
declarados sao recusados; nenhum `extractall` e usado no pacote de usuario.
O recibo restaurado esta em `out/logs/host_transfer_restore_report.json`.
Identidade dos bytes nao significa que o jogo foi revalidado no novo host.

O pacote nao leva historico Git. Preservar o repositorio original e manter uma
clone separada do remoto para revisao/publicacao. O workspace restaurado pode
ser usado para builds; nao executar reset/clean/checkout forcado para liga-lo
ao remoto. A integracao futura precisa reconciliar sua arvore privada com a
branch de origem e seus deltas, por allowlist, num checkout isolado.

## Antes de voltar ao gameplay

1. Ler AGENTS, memoria/GDD/TDD do owner e handoff deste lote. Resolver qualquer
   include absoluto de politica pessoal (`/home/.../.codex/RTK.md`) conforme o
   novo host; nao criar falsa home antiga. RTK instalado pelo wrapper pode ser
   usado com `rtk proxy`; o arquivo pessoal nao e dependencia do build.
2. Instalar/ativar; validar guard, contexto, higiene e learning por owner. Falha
   no host nao autoriza editar C/assets para contornar executor.
3. Executar os seletores de build/captura com paths reais do destino. Nao copiar
   antigos reports de ambiente para promover o novo host.
4. Revalidar pads P1/P2 no display privado. ACK/SDL nao substituem efeitos da ROM.
   Input real do usuario e teste perceptivo precisam seu aceite proprio.
5. Primeiro reproduzir uma fonte congelada num output candidato, sem substituir
   `out/rom.bin`. Conferir bytes/flags/toolchain antes de atribuir diferenca ao C.
6. Build apenas promove `buildado`; BlastEm/audio/60fps/budget sao outros eixos.
   Registrar aprendizado novo localmente e enviar proposta canonica deduplicada.

Fontes de distribuicao: [SGDK 2.11](https://github.com/Stephane-D/SGDK/releases/tag/v2.11),
[PowerShell](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.2),
[Temurin](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.11%2B10),
[RTK](https://github.com/rtk-ai/rtk/releases/tag/v1.0.1).
