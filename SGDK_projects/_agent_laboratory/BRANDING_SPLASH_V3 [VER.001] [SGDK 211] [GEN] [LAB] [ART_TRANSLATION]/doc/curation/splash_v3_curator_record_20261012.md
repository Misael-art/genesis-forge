# Registro de curadoria — Splash V3

Data: 2026-10-12  
Escopo: decisao de desenvolvimento da musica V015 e continuidade da direcao visual.

## Decisao atual

V015 esta aceita pelo usuario para desenvolvimento. A composicao pode seguir para integracao e refinamento; nao recebeu aprovacao musical final. A revisao auditiva deve ocorrer novamente depois que a cena visual V3 estiver integrada, com o hash da ROM completa e dois ciclos consecutivos.

## Historico de feedback musical do usuario

1. A primeira candidata foi descrita como monofonica e abafada, com camadas que pareciam instancias do mesmo timbre. Registrar como percepcao de pouca separacao e cor timbrica; nao inferir pedido por audio estereo.
2. O usuario declarou que a qualidade musical ainda estava baixa; aquela versao nao foi aprovada.
3. Em seguida, disse que uma revisao estava melhor e pediu um som mais cristalino. Esse retorno valoriza brilho, mas nao aprovou a composicao final.
4. Depois rejeitou uma linha sonora continua e monotona, sem a animacao e energia combinadas. A rejeicao de V013/V014 continua vinculante.
5. V012 permanece a referencia positiva. V015 foi aceita para desenvolvimento e deve voltar a curadoria apos a integracao visual.

## Criterios musicais para a proxima revisao

- Abertura positiva, heroica, confiante e aventureira, com ataque imediato e duracao curta.
- Motivo curto e reconhecivel, com movimento ascendente e resolucao maior firme.
- Ritmo animado por frases articuladas, ataques curtos, pausas audiveis e resposta; evitar nota ou textura sustentada que transforme a assinatura em um tom continuo.
- Brilho cristalino em acentos breves e agudos, sem encobrir a melodia nem soar como camada constante.
- Separacao perceptiva entre lead FM, stabs de baixo/harmonia e acentos cristalinos; releases curtos e espaco real para os cues PCM.
- Na revisao integrada, julgar identidade melodica, energia, articulacao, nitidez, equilibrio com os efeitos, impacto da resolucao e emenda em dois ciclos.

## Estado visual observado

- O storyboard V3 define sete estados em 240 quadros: silencio, energia azul, convergencia/contorno SGDK, preenchimento, entrada de FORGE, passagem de faixa luminosa e fade/teardown.
- A ROM vista durante a revisao de V015 e um monitor de diagnostico de audio; ela nao apresenta a cena visual final.
- O diagnostico identificou 16 assets ativos no `.res`, todos tecnicamente adequados, mas sao recursos da identidade antiga/introdutoria e nao comprovam a arte V3.
- Existem dois previews de lettering em `rascunho/visual_lab/`; ambos estao marcados como controles de laboratorio. Nao sao fontes finais, assets VDP promovidos nem aprovacao de model sheet.
- O conceito V3 deve manter palco escuro com energia azul/ciano cristalina convergindo para SGDK, seguida de FORGE e uma faixa com direcao legivel. A imagem deve ter contraste suficiente para 320x224 e nao pode depender de glow difuso.
- A rota de origem do lettering e a aprovacao do model sheet permanecem pendentes. Nenhum asset visual V3 foi promovido ao `.res` nesta atualizacao.

## Pendencias para o curador

- A guarda global de medicao continua bloqueada: o report lista 30/30 self-checks aprovados, mas tambem 20 espelhos ativos desatualizados e `blocking=true`. Uma tentativa exploratoria do simulador percorreu 990 entradas, foi marcada invalida e nao pode orientar densidade, arte ou budget. Reexecutar somente quando a guarda global estiver liberada.

- Depois da integracao visual, fazer revisao auditiva de V015 na ROM exata e registrar a decisao como aprovada, ajustar ou rejeitada.
- Conferir se a energia visual e a musica crescem em conjunto; se a cena pedir mais brilho/ataque, corrigir o mapa de cues antes de alterar notas sem evidencia.
- Validar o encaixe do mark-lock na pausa musical, a passagem da faixa sem mascara sonora e o final junto ao fade.
- Manter separados status de desenvolvimento, aprovacao estetica, validade tecnica, budget DAC, FPS sustentado e gate canonico de BlastEm.

## Limites desta decisao

V015 permanece nao canonica. A ROM V2 vigente, FORJA V2 e template nao foram alterados. A decisao nao encerra validacao de audio, cena, memoria, performance ou promocao.
