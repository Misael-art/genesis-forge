# FX80 owner map com SAT exato — 2026-10-16

## Aprendizado reutilizavel

- Para atribuir SAT por instancia, grave o owner map antes de `SPR_update`, usando o SAT e o timestamp que o FXVD capturou na mesma passagem de `APP_update`. Um mapa depois do VBlank pode estar um frame de cena adiante; no caso deste run, o checkpoint 600/tick 328 tinha CRC SAT diferente, embora o tick de luta continuasse igual. A igualdade de fight tick sozinha nao prova que as entradas SAT sao a mesma imagem.
- Mantenha o gate estrito: frame/tick do FXOM devem casar com FXTI/FXVD, a CRC de todos os 80 registros SAT deve casar, os ranges por Sprite devem ser unicos e o replay de slot/owner/elemento deve casar com o trace FX80. Nao afrouxe esses checks para absorver uma captura atrasada.
- BlastEm 1.0 continua sendo somente a rota diagnostica. Neste build, o transcript chegou a `FORGE_SNAPSHOT_COMPLETE 1200` e salvou SRAM ligada ao hash exato do ROM, mas o wrapper terminou como `blocked: debugger_timeout`; isso permite analisar esta captura como dado suplementar depois de validar hashes e parser, sem promover o status do emulador nem mudar o gate oficial. Nao recuperar 0.6.2.
- Os picos individuais por slot nao sao somaveis: os maximos podem ocorrer em linhas diferentes. Use os contadores por linha do mapa, confira que FX80 + nao-FX80 reconstrua cada linha e so depois reporte o pico total.

## Resultado vinculado

Run diagnostico `out/work_runs/fight_base_ryu_fx80_owner_map_20261016_r1/`; ROM `out/profiling/fight_base_ryu_fx80_owner_map_20261016_r1_attempt03/rom.bin`, SHA-256 `285d853d4be05f19db48203830cb06fa0b83a49828e59d574d045e16c6acd5bd`. O snapshot de build terminou `unchanged`, com 368 entradas e source-tree SHA-256 `02e61e537f95cf17059e898d87ca1b664ff8f2d7504125eb387349f437ccc99a`.

O parser validou cinco FXOM contra FXTI/FXVD: CRC SAT em 5/5, ranges unicos, owner/slot/elemento iguais ao trace e reconstrução por linha completa. Todos os FX80 observados tinham owner id 1. Medidas abaixo: entrada SAT FX80 por slot; pico individual `sprites/pixels-de-largura` por scanline; e pico total da cena.

| frame/tick | instancias / slots | SAT por slot | pico por slot | pico FX80 agregado | pico total da cena |
|---|---|---|---|---|---|
| 321/322 | 3 / 0,1,2 | 0:14; 1:8; 2:8 | 0:6/160; 1:3/80; 2:3/80 | 12/288 | 21/520 |
| 414/324 | 3 / 0,1,2 | 0:18; 1:14; 2:14 | 0:5/160; 1:6/160; 2:6/160 | 15/448 | 24/632 |
| 507/326 | 3 / 0,1,2 | 0:18; 1:18; 2:18 | 0:8/216; 1:5/160; 2:5/160 | 16/480 | 22/640 |
| 600/328 | 3 / 0,1,2 | 0:6; 1:18; 2:18 | 0:4/104; 1:8/216; 2:8/216 | 14/424 | 21/608 |
| 693/330 | 2 / 1,2 | 1:6; 2:6 | 1:4/104; 2:4/104 | 7/184 | 14/376 |

Os pares de pico sao sprites por scanline/pixels de largura acumulados na mesma scanline, nao area de pixels. O total da cena passou 320 px em 5/5 e 20 sprites em 4/5; o chain SAT chegou a 78/80 entradas, sem exceder o limite da tabela. No ultimo checkpoint, 14 sprites ficaram abaixo do limite de contagem, mas 376 px ainda excederam o limite de largura.

## Limites e proximo passo

Instrumentacao e ROM existem apenas no clone temporario. Nenhum codigo de produto, PNG, `.res`, ROM principal, gate oficial ou promocao foi alterado. Os dois PNGs FX compartilhados de Ryu/Ken continuam iguais. Esta medicao nao aprova direcao visual, cadencia sustentada, audio ou release. O proximo passo e apresentar uma proposta tecnica limitada ao par FX existente e aos cinco checkpoints H40 para a revisao de direcao humana, mantendo a decisao de promocao separada.

Evidencia: parser `out/evidence/fight_base_ryu_fx80_owner_map_20261016_r1/frame1200_attempt03/measurement_parse/fx80_owner_map_capture_parse_report.json` SHA-256 `fc46812eef1a19a16064b0b48e17e9a33f1e4dc0e57fb126318250d071c0d2cb`; SRAM SHA-256 `5c325be13c1cd9362f7271a8a606b39ca534e40ab8b0ab452bd583aeb1e80ecb`; BlastEm native report `out/evidence/fight_base_ryu_fx80_owner_map_20261016_r1/frame1200_attempt03/native_diagnostic_report.json` SHA-256 `e5d10096166d1a7158424fe9ff42a587251b9451b34f7e926d18ef258e655a17` (`blocked/debugger_timeout`, sentinel e SRAM presentes).
