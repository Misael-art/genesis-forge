# Migracao de host — escopo e owner

Owner: curador do workspace. Base dos paths: raiz do workspace. Autorizacao:
pedido do usuario para registrar diagnostico, preparar instalacao/retomada,
commit, push e PR. Desenvolvimento de gameplay permanece pausado.

Escritas: novas ferramentas `tools/sgdk_wrapper/bootstrap_host*` e
`host_transfer.py`, catalogo/lock/testes associados, referencia de operacao,
este diretorio e acrescimo delimitado na memoria do workspace. Evidencia e
pacote privado: `out/curation/2026_10_24_host_migration/`.

O checkout compartilhado possui centenas de deltas de terceiros. Publicacao
sera isolada, com allowlist; nenhum runtime, ROM ou asset privado sera enviado
ao GitHub por esta tarefa. A transferencia privada tera inventario SHA-256,
verificacao de deriva durante a copia, rejeicao de links externos e importacao
em destino novo. Nao apaga caches, sessoes ou evidencias do host de origem.

Plataforma automatizada inicial: Linux x86-64, Debian 12/13 e Ubuntu 24.04
(Python >=3.11). Ferramentas do sistema via apt; SDK e ferramentas portaveis no
workspace; Flatpak no usuario. Outras plataformas falham explicitamente e
continuam usando os seletores existentes, sem alegacao de qualificacao.

Aceites: catalogo pinned, hashes de downloads, instalacao retomavel e com lock,
ambiente local ativavel, limites de recursos, diagnostico sem instalacao,
transferencia integre/negativos, handoff dos dois projetos e testes num destino
limpo. Instalacao real de sistema numa maquina virgem e QA de jogos sao gates
separados; nao vao ser simulados como aprovados neste host ja preparado.
