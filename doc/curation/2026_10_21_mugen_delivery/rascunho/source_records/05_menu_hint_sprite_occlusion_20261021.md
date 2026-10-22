# Lutadores do menu cobrem o texto de ajuda — 2026-10-21

## Aprendizado reutilizavel

- O titulo chama `MG_fightInit` e a saida chama `MG_fightEnd`. A troca de cena zera os sprites. Os lutadores da foto do menu nascem no proprio menu: `SCENE_menuEnter` inicia Ken e Ryu e `SCENE_menuUpdate` desenha os dois uma vez.
- Na janela do menu, o titulo, a lista de modos ate OPTIONS e os nomes dos lutadores no confronto foram lidos. As linhas `A/START: CONFIRMAR` e `B: VOLTAR AO TITULO` ficam atras dos pes. No confronto, `RELLOGIO DO DESAFIO` e o texto de acertos do Bonus, na linha 14, ficam parcialmente cobertos.
- As linhas 25 a 27 continuam na faixa dos pes. A linha 26 pertence ao HUD de debug. Nao sao zona livre medida.
- A faixa vazia acima de `MUGENESIS` (linha 2) e o lugar operacional das instrucoes: linhas 0 e 1, e as linhas extras de selecao e confronto nas linhas 3 e 4. Sem uma ROM nova, o deslocamento nao esta provado. Texto coberto nao e texto ausente.

## Resultado

Foto: `out/evidence/mugenesis_frontend_survey_20261021_r1/native_diag_menu_main_f123/window.png`.

A imagem e janela letterbox 640x480, nao um framebuffer 320x224 em dobro. A leitura vale pelo que a foto mostra, nao por uma grade de tiles projetada na caixa de pixels nao pretos.

Recibo: `out/work_runs/mugenesis_frontend_survey_20261021_r1/reports/frontend_survey_observation.json`.

Limite: observacao visual suplementar da ROM `a93bf7f7fe34c90e50e176e0ec294868134438afc0b9cc44929c1fd7df49658a`. Nao e correcao medida.

## Medicao posterior

A ROM `35cc8179debe67c52d8f6e59a5ffd35e23ce9f5ee8e3661977f9ff54b65d9a02` mostrou selecao, relogio e `8 ACERTOS EM 30S` na faixa superior. A linha 0 do menu principal nao permaneceu. A ROM `36c459c63192d381396e2f91d9a9535b5fa61d09e488955c13311c23fb7ec7e1` mostrou `A/START: CONFIRMAR` sob o titulo e `PERFIL: PARADO` com `ESPECIAL NORMAL` no treino. Deslocamento do marcador nessa ROM: 56. BlastEm 1.0, audio dummy, sem gate.
