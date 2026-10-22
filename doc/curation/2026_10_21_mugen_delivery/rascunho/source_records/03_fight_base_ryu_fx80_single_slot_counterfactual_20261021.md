# FX80 — um slot ainda nao cabe no H40 — 2026-10-21

## Aprendizado reutilizavel

- O mapa FXOM de 2026-10-16 ja atribui os cinco checkpoints. Nao reconstruir esse instrumento enquanto o SRAM e o parser continuarem validos.
- Os picos por slot nao se somam. A contraprova correta subtrai, linha a linha, so os sprites do slot omitido. Nesta captura a soma dos slots reconstruiu o FX80 e o FX80 mais o resto reconstruiu a cena, com zero divergencias.
- Limitar a uma ou duas instancias visiveis nao passa os cinco quadros. O melhor slot unico ainda estoura a largura: 16 px no quadro 414 e 24 px no 507. A contagem de sprites desse slot unico fica abaixo de 20.
- Mover o efeito para o topo da tela separa as linhas, mas tira o super de cima dos lutadores. Isso nao preserva o efeito. Um plano unico tambem nao reproduz as partes: os X gravados nao compartilham a mesma fase de 8 px.

## Resultado

Veredito de budget: `nao cabe`. Sem ROM nova, sem `build_v`, sem promocao e sem troca da ROM principal `1b66cd1d7d3117f7fec0e487e1d4a7473357b5fa0693c24d21cf333eada1c7a8`.

Recibo: `out/work_runs/fight_base_ryu_fx80_single_slot_counterfactual_20261021_r1/reports/fx80_single_slot_counterfactual.json`.

Proximo passo: direcao de arte no par 8060 existente. Cortar pelo menos 24 px de largura de sprite na instancia unica, nas linhas que ela divide com os lutadores, e medir de novo os quadros 321, 414, 507, 600 e 693.
