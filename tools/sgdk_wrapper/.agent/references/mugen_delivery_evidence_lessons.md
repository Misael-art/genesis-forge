# Curadoria MUGEN: evidencia de entrega e custo de render

Aplicar a ports, luta ou outros jogos quando houver grandes efeitos simultaneos,
telemetria de render ou modos parcialmente implementados. Refinamento dos owners
existentes, nao novo lifecycle. Adjudicacao/fontes:
`doc/curation/2026_10_21_mugen_delivery/decisions.json`.

## SAT: atribuir a mesma imagem antes de otimizar

Identificar ROM, modo H40/H32, camera, fase de render, frame apresentado e tick
logico. Mesmo tick de luta nao identifica a mesma SAT: a simulacao pode parar
ou atualizar menos vezes que o VDP. Validar que o owner map representa a SAT
capturada, com comparacao integral/CRC, ranges exclusivos e replay de
owner/slot/elemento. Capturar no ponto correto do renderer; nao usar um mapa
posterior ao VBlank para rotular automaticamente a tabela anterior. CRC identifica
bytes, nao autentica o instrumento; decoder e coleta precisam de validacao propria.

Para contrafactual sem mudar posicoes/poses, somar/subtrair as contribuicoes
na MESMA scanline, reconstruir integralmente os totais e medir os dois tetos:
contagem de sprites e soma de suas larguras de hardware. Maximos individuais
em linhas diferentes nao se somam. Pixels opacos/bbox e area da imagem nao sao
largura consumida pelos sprites SAT. Contagem de entidades nao mede esse custo.

Uma unica instancia pode exceder o teto de largura mesmo abaixo do teto de
contagem. Escolha independente do melhor slot por checkpoint e um limite
inferior otimista, nao prova de politica executavel ao longo da animacao.
Reducao minima observada em poucos checkpoints e condicao necessaria naquele
recorte, nunca budget suficiente da cena ou constante para outros assets.

Contrafactual rejeitado fecha a hipotese naquela carga. Se mudar decomposicao,
layout, posicao ou timing, deixa de valer a subtracao antiga: medir a nova ROM.
Flicker/HIDDEN pode retirar entradas da SAT sem liberar tiles residentes; nao
inferir reducao de VRAM/DMA. Medir frames ligados e apagados e a continuidade
perceptiva. Um frame apagado que cabe nao corrige o frame ligado que estoura.
Nenhuma dessas observacoes autoriza mascarar overflow com flicker ou suprimir
feedback essencial. Qualquer adaptacao requer escopo/decisao e gates proprios.

## Marcadores, coletores e status

Rotulo de debug pode ser atualizado antes de a SAT nova ser apresentada.
Conferir readback da tabela, fase e marcador; a legenda nao e prova do estado
fisico. Nao transportar offset de frame medido no final da luta para menus,
nem converter lacos de simulacao em VBlanks com uma constante global.

Sentinel de termino, screenshot ou dump presente nao anula `debugger_timeout`.
Preservar resultado e artefatos originais; eventual analise suplementar precisa
validar cada arquivo/hash/ROM/fase e declarar o claim limitado. Nova tentativa
usa novo destino. A causa de timeout exige prova do processo/coletor: sentinel
sozinho nao demonstra corrida de PTY nem a resolve aumentando espera.
Nao alterar versao de emulador ou gate de entrega por inferencia desse sintoma.

## Menu, treino e modos: provar comportamento

Menu legivel, item selecionado e tela de confronto provam esses estados.
Cota escrita na tela nao prova contagem de acertos; texto de Time Attack nao
prova cronometro, ranking ou conclusao; perfil de sparring nao prova sua IA.
Para cada opcao, testar mudanca de estado, efeito durante a luta, resultado,
reset, retorno e isolamento entre modos, no mesmo SHA de ROM.
Teste host do timer nao substitui o fluxo executado, audio ouvido ou cadencia.

Ao diagnosticar texto ausente/coberto, consultar o owner que cria os sprites,
retangulos de ocupacao e HUD de debug antes de mover linhas. Janela com
letterbox nao e framebuffer nativo: nao deduzir grade pelo retangulo nao preto.
Medir transformacao/viewport ou limitar a conclusao a observacao da janela.
Nova posicao exige captura nova; coordenadas do Mugenesis nao sao layout geral.

## ROM igual nao identifica retrospectivamente a fonte

Hash/tamanho iguais identificam o mesmo binario, nao provam quais arquivos,
flags, SDK ou gerador criaram uma ROM antiga. Arvores distintas podem gerar
bytes iguais, inclusive por arquivos nao compilados ou mudancas sem efeito.
Recibo contemporaneo/snapshot congelado do build atual qualifica sua propria
origem; nao pode reatribuir fonte a um build historico desconhecido.

Nao abrir `build_v` para representar fonte ainda nao buildada nem copiar ROM
preservada como se fosse o resultado novo. Versionar o artefato correto quando
houver novo binario e recibo. Atualizacao status-only conserva blockers
conhecidos; ausencia de report nao e zero blockers. Essa regra refina a
reconciliacao existente e nao altera scripts ou migra historico automaticamente.

## Alcance

Esta curadoria qualifica metodos documentais, nao ROM, arte, 60fps, audio,
compatibilidade MUGEN completa ou ganho de performance. Nao habilita flags,
nao instala runtime, nao muda defaults e nao promove candidatas locais.
