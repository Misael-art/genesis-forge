# Novo host, instalacao e continuidade

Usar somente na instalacao/migracao de host. Fonte operacional completa e
aceites: `doc/HOST_BOOTSTRAP_AND_CONTINUITY.md`. Entradas canonicas:
`bootstrap_host.sh` / `bootstrap_host.py` e `host_transfer.py`, todos no wrapper.

- Host sem pwsh comeca por bash; consultar o plano antes de aplicar.
- Linux x86-64 Debian 12/13 ou Ubuntu 24.04 tem entrada apt automatizada.
  Outro host recebe diagnostico explicito; Windows mantem seu wrapper existente.
- Ativar `out/host_tools/activate.sh` em cada shell. SDK local ao workspace,
  venv/pwsh/JRE/caches em `out/host_tools`; Flatpak em escopo de usuario.
  Nao transferir venv, Wine prefix, PID, socket, DISPLAY ou sessoes vivas.
- Clonar Git nao recupera fonte nao commitada, input privado, capsula e review
  ignorados. Exportar selecao privada com inventario/hash; importar em diretorio
  novo. Nao publicar esse pacote no GitHub nem sobrescrever checkout/baseline.
- Preservar `.agent` local real; pontes sao recriadas pelo guard existente.
- Dependencias prontas nao qualificam ROM, audio, FPS, arte ou engine. Reabrir
  gates no novo host por hash e pelo seletor de build/captura correto.
- Comecar com um build e uma sessao de emulador. Expandir somente apos observar
  recursos. Sem limpeza automatica, updates globais, hooks ou novo indice.
- Pins de Flatpak indisponiveis ou diferentes bloqueiam. Atualizar exige revisar
  identidade e repetir aceitacao; nao trocar versao silenciosamente para verde.
