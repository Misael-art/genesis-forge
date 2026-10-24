# Entrega de preparacao do novo host

Ponto de entrada humano: [instalar e restaurar](../../HOST_BOOTSTRAP_AND_CONTINUITY.md).
Ponto de entrada do proximo agente: [diagnostico e prompt](handoff.md).
Selecao privada: [receita](transfer_recipe.json). Escopo autorizado: [plano](plan.md).

O wrapper agora prepara Linux x86-64 por plano/aplicacao explicitos, com pins,
hashes, instalacao local/retomavel, lock, venv, ativacao e limites de recursos.
A transferencia inclui fontes atuais nao commitadas, inputs autorizados,
capsulas e aprendizado; nao e um backup integral do workspace. Antigas arvores
de candidatos e fan-out de aliases temporarios continuam preservados na origem.
Nao copiar venv nem sessoes ativas. Nenhuma ROM, input ou asset privado entra
na PR de infraestrutura.

Verificacao executada:

- 36 testes host com negativos e roundtrips, sem instalacao de sistema;
- instalacao portavel real em staging separado e repeticao idempotente: SDK
  oficial 2.11, PowerShell 7.6.2, Temurin 21.0.11+10, RTK 1.0.1 e lock Python;
- sintaxe bash e skill do wrapper validadas;
- revisao independente em quatro rodadas: defeitos causais reparados, qualificacao
  global `needs_evidence`, sem usar esse parecer para alegar runtime;
- consultas reais ao Flatpak: BlastEm instalado 1.0, pin antigo indisponivel404,
  runtime 24.08 requerido pelo Wine ausente;
- mount real SD/FUSE nao admite publicacao atomica de diretorio sem sobrescrita;
  instalador detecta antes dos downloads. Destino de restore/instalacao: Linux
  nativo. Pacote TAR pode permanecer no SD.

Ainda pendente: primeira instalacao completa apt/Flatpak em host virgem,
vinculo da identidade efetiva do emulador no launcher/sealer e requalificacao
de captura. Nenhum teste deste lote prova gameplay, audio, 60fps, budget,
compatibilidade global MUGEN/OpenBOR ou engine completa.

Auditoria de layout manteve blocker historico `out.broken_20261022` do MUGEN;
nada foi movido/apagado para produzir verde. Commit/PR usam checkout isolado
e allowlist; branch/index compartilhados permanecem preservados.

Recibos de execucao e pacote privado ficam em
`out/curation/2026_10_24_host_migration/`. A PR inclui apenas evidencia pequena
de infraestrutura; o TAR privado deve ser transportado separadamente.
