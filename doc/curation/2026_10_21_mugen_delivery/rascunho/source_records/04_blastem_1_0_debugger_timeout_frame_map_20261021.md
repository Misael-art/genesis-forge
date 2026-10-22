# Timeout do depurador nao e quadro perdido — 2026-10-21

## Aprendizado reutilizavel

- O coletor do BlastEm 1.0 marca `debugger_timeout` quando o PTY fecha antes do `poll` do processo, mesmo com `FORGE_SNAPSHOT_COMPLETE`, dumps e `window.png`. Subir o timeout nao corrige essa corrida. Uma nova tentativa precisa de uma folha nova. Nao reclassificar a folha antiga como `captured`.
- Antes da luta, o quadro de VDP do levantamento e o quadro do laco mais 55. Na luta, do quadro de levantamento 1252 ao 1512, o laco andou 260 vezes e o VDP andou 478 quadros. O atraso medido no fim da luta nao serve para as telas anteriores.
- O primeiro lote de telas usou o deslocamento 288, do fim da luta. Essas pastas ficam com o nome errado e nao entram na leitura. O quadro certo sai do marcador `sSurveyMark` (`46 53 56 31`) na work RAM daquela ROM.
- BlastEm 1.0 continua so diagnostico. Nao recuperar o Flatpak 0.6.2 e nao alterar o gate oficial por esta coleta. O audio deste levantamento e dummy.

## Resultado

Quadros com timeout no coletor e imagem presente: confronto de Bonus no VDP 969 e luta no VDP 1800. O menu no VDP 123 e os outros confrontos anteriores a luta foram `captured` nessa mesma ROM.

Recibo: `out/work_runs/mugenesis_frontend_survey_20261021_r1/reports/frontend_survey_observation.json`.

Limite: grau E1. A corrida do coletor nao mede 60 fps e nao promove a ROM.
