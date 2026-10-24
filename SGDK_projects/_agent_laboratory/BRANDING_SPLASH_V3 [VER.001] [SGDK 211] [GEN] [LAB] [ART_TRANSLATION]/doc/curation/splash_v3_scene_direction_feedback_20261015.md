# Registro de feedback de direção de cena — 2026-10-15

## Reconciliacao de evidencia — 2026-10-16

O contrato v004 tinha dois controles verticais distintos do C compilado. O valor de 23,54 px citado abaixo e historico daquele contrato offline, e nao deve ser atribuido como medida exata da ROM. A coreografia C nao foi alterada por esta reconciliacao. O contrato v005 confere 154 posicoes ativas com as funcoes C e mede 22,09 px de separacao minima, ainda acima do piso de 20 px. A versao opt-in com tabelas conserva todos os 6.324 pares de coordenadas, verificados diretamente no binario. Referencias: `doc/curation/splash_v3_wind_dispersal_contract_v005_20261016.json`, `out/logs/splash_v3_wind_dispersal_scanline_v005_20261016.json` e `out/logs/splash_v3_motion_lut_compiled_equivalence_20261016.json`. Aceitacao estetica continua pendente.

## Novo feedback sobre dispersão e silhueta

- O usuário avaliou o v003 como ainda aglutinado: pediu partículas mais dispersas, ao menos três velocidades alternadas e duas trajetórias com mudanças de posição não uniformes.
- Também apontou que, quando o brilho azul escurece, o contorno do SGDK se mistura ao fundo e passa a parecer degradado.
- A deficiência continua no handoff de direção: faltavam um critério numérico de separação entre partículas e um critério para preservar o contorno durante o fade. A mesma falha deve alimentar a curadoria local do skill, sem alterar a árvore compartilhada.
- Resposta v004: três bandas horizontais medidas (5,83–6,15; 8,19; 12,09–14,38 px/quadro), ruído cruzado de amplitude 2 px em `spark_2` e `spark_4` com fases/períodos próprios, e elevação das três cores azuis do contorno em PAL1 no frame 210. Os assets e seus pixels não foram alterados.
- Medição de 30 quadros: distância mínima entre centros 23,54 px em F192; zero pares abaixo de 16 px; máximo de 2 sprites/16 pixels por scanline H40 e até 12 links. Isto cobre só a geometria do sweep.
- A ROM v004 foi observada no BlastEm. Vídeo e contatos permanecem suplementares; a aceitação visual humana ainda está pendente. Registro de runtime: `out/evidence/splash_v3_wind_dispersal_preview_v004_20261015/local_blastem_x11/wind_dispersal_runtime_review_v004.json`.

## Rejeição da passagem anterior

O usuário rejeitou o sweep de fagulhas da ROM `9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006`. Feedback direto: “o resultado não ficou como esperado; o diretor de cena não mostrou competência para levar cada item da cena com excelência”. A passagem foi descrita como um movimento contínuo e monótono, sem a proposta de animação e energia combinada. O arquivo permanece preservado apenas como evidência rejeitada.

## Direção pedida para a nova animação

- Seis fagulhas devem parecer leves, carregadas por correntes de ar; evitar linha rígida e gravidade dominante.
- Cada partícula parte de coordenada e quadro próprios e percorre arco ou curva S. A velocidade deve variar com easing, acelerando na rajada e desacelerando perto de mudanças de direção e no resfriamento.
- Turbulência deve ser determinística, lenta e de baixa amplitude; não pode virar tremor ou ruído que esconda SGDK/FORGE.
- Nascimento gradual em 3-5 quadros, fase ativa brilhante e dissipação progressiva. Ao morrer, a partícula desacelera e reduz sua cobertura de pixels.
- A cauda acompanha a direção local do movimento. Algumas partículas recebem flicker individual entre cerca de 80% e 100% do brilho de base, fora de uma pulsação sincronizada.
- O brilho de borda deve ser visível, mas respeitar o VDP: paleta indexada e quadros de bloom simulam halo; sem alpha blending, Gaussian blur ou escala de hardware.

## Deficiência identificada no handoff do skill

O primeiro handoff de `cutscene-cinematic-direction` para implementação reduziu “fagulhas levadas pelo vento” a velocidades e posições diferentes. Não especificou a vida visual por instância, a sequência de quadros para nascer/brilhar/apagar, o owner do rastro, o flicker parcial, a redução de escala aparente nem critérios de aprovação da cena viva. O resultado tinha métrica geométrica válida, mas falhou no objetivo estético observado pelo usuário.

Mitigação local: contrato por instância cobrindo trajetória, easing, ruído, birth/active/fade, quadros concretos, rastro, flicker, limitação de glow e checks de legibilidade; handoff ao analista VDP para medir cada frame; captura em emulador antes de pedir aprovação. A revisão da skill é somente candidata para curadoria humana, depende de aceitação desta nova versão e reprodução em outra cena. Nenhum arquivo de skill compartilhada foi editado.

## Implementação e estado

- Contrato de movimento: `doc/curation/splash_v3_wind_lifecycle_motion_contract_v002_20261015.json`.
- Código: seis curvas Bézier Q8 com easing, ruído discreto de até 1px, sem termo de gravidade, quadro inicial de quatro passos, fase ativa, flicker assíncrono em algumas fagulhas, seis núcleos e até seis rastros orientados pela tangente, seguidos por dissipação em cobertura menor.
- Medição geométrica local: 30 quadros F180-F209; pico de 10 sprites/80 pixels em F202-F204, máximo de 12 links visíveis e nenhum excedente H40. Report: `out/logs/splash_v3_wind_lifecycle_scanline_v002_20261015.json`.
- Build isolado observado no BlastEm: ROM SHA-256 `558fee0aabbee64ea98582a47fd9284866c649f02f2add179b6d0085a9e151ae`, 524288 bytes. O vídeo de 5,53 s e o contato de quadros registram a progressão da cena e a passagem das fagulhas: `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/wind_lifecycle_runtime_review_v003.mp4` e `out/evidence/splash_v3_wind_lifecycle_preview_v003_20261015/runtime_contact_sheet.png`.
- A captura confirma execução e movimento visível; não é frame-marked ROM-side e não mede FPS sustentado, qualidade de áudio, budget VDP total ou aceitação estética. A avaliação humana continua pendente. Splash V3 permanece em desenvolvimento, sem promoção do template e sem arquivamento da FORJA V2.
