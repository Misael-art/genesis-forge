# Curadoria operacional — host portavel — 2026-10-24

Autorizacao: usuario pediu registrar diagnostico, preparar instalacao em host
sem ferramentas, handoff, commit e PR. Sem retomada de gameplay nesta frente.

- Adicionados bootstrap bash/Python, catalogo de downloads/pins, lock Python
  com hashes e ativacao local. Sistema via apt em hosts declarados; ferramentas
  portaveis/venv/caches no workspace; Flatpak no usuario, com runtime/probe.
- Adicionada transferencia privada por selecao explicita, fontes nao commitadas,
  hashes durante copia e restauracao em destino novo. Skills locais reais
  preservadas; venv, estados vivos e credenciais conhecidas sao excluidos.
- Entry point da skill wrapper aponta para referencia de migracao. Nenhuma
  segunda arvore de skills e criada, nem .agent local sobrescrita.
- Revisao independente encontrou e conduziu reparos de filtragem, preservacao
  local, publicacao concorrente e manifesto grande; os testes incluem negativos.
- Registrados drift real BlastEm 1.0 versus catalogo legado 0.6.2, commit antigo
  indisponivel, runtime Wine ausente e restricao real do mount SD/FUSE.
- Instalacao portavel e repeticao foram executadas em staging nativo. Apt,
  Flatpak, build de jogo, captura, audio e performance permanecem outros aceites.

Fontes/provas e proximos passos:
`doc/curation/2026_10_24_host_migration/` e
`doc/HOST_BOOTSTRAP_AND_CONTINUITY.md`. Licoes M5 not_applied continuam candidatas;
este lote nao as promove implicitamente nem altera o runtime das engines.
