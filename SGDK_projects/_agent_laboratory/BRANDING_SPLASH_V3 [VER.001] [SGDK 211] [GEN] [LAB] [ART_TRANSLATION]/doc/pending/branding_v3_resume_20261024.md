# BRANDING-001 - confusoes de branding e retomada da Splash V3

- Status: **pendente / trabalho pausado por solicitacao humana**.
- Registro: 2026-10-24.
- Owner: laboratorio `BRANDING_SPLASH_V3`; direcao de cena/arte e curadoria na retomada.
- Pedido humano: registrar as varias confusoes sobre branding, fazer commit e PR
  e retomar em outro momento.
- Este registro conserva trabalho em desenvolvimento. Nao aprova a cena, musica,
  ferramentas compartilhadas, template ou migracao de consumidores.

## Confusoes a resolver

1. **Laboratorio, V2 e template misturados na comunicacao.** O README herdado
   apresentava o laboratorio como modelo canonico. O menu ainda utiliza assets
   e BGM V2. A intencao continua sendo uma unica splash V3 no template somente
   apos validacao completa; V2 ainda nao foi arquivada.
2. **Fonte atual, baseline e candidatas diferentes.** `out/rom.bin` e uma baseline
   antiga. O historico chama O de selecionada, enquanto o ultimo build e R.
   Flags opt-in mudam o executavel. Sempre identificar ROM, flags e escopo da
   prova; nao atribuir os resultados de Q a R sem uma nova verificacao.
3. **Sucesso tecnico confundido com qualidade percebida.** Compilacao, distancias
   entre particulas, CPU e scanline nao aprovam naturalidade, hierarquia visual
   ou excelencia de direcao. Feedback negativo humano permanece negativo mesmo
   quando a geometria passa nos instrumentos.
4. **Instrumentos e contratos divergentes.** A antiga sonda contou sprites
   ocultos; o contrato offline v004 tinha dois handles Y diferentes do C.
   A medida corrigida v005 e 22,09 px, em vez de 23,54 px. O pico historico
   de 22 sprites por linha nao deve ser tratado como permissao para ultrapassar
   o limite H40 de 20 sprites e 320 pixels por linha, nem transferido para outra
   ROM. Preservar resultados rejeitados e o contexto de cada medicao.
5. **Reforco de contorno implementado, mas sobrescrito pelo fade.** A escrita
   enfileirada das cores nao era a fonte usada por `PAL_fadeOut`. A candidata O
   passou a fornecer a paleta explicita ao fade. O defeito nao era perda de pixels
   do lettering. A leitura visual final ainda depende de aceite humano.
6. **Som tratado cedo demais como resolvido.** O usuario rejeitou monotonia,
   abafamento e falta de energia; pediu brilho cristalino sem som continuo.
   Depois decidiu manter o audio em desenvolvimento, para revisao futura.
   Nenhuma captura ou presenca de som constitui aprovacao musical.
7. **Escopos de evidencia misturados.** Cadencia emulada, amostras em dez boots,
   video, audio com inicio independente e diagnostico nativo nao sao uma unica
   prova continua nem o gate canonico completo. Artefatos locais em `out/` nao
   estao publicados neste PR.

## Feedback criativo que continua aberto

- Fagulhas devem parecer levadas pelo vento: dispersas, assincronas, curvas
  suaves, aceleracao/desaceleracao, variacao de altitude e micro-oscilacoes.
- Pedido mais recente: pelo menos tres velocidades e duas trajetorias variando
  de modo nao uniforme. Seis caminhos foram implementados, mas o aceite dessa
  ultima revisao nao foi recebido.
- Nascimento suave, pulsacao individual, rastro orientado, dissipacao e reducao
  de cobertura sao parte da direcao; nao basta variar coordenadas.
- SGDK deve conservar bordas legiveis quando o brilho azul escurece. O preto no
  ultimo frame e a saida intencional, nao deve ocultar o defeito anterior.
- A deficiencia do handoff/direcao de cena anterior e as rejeicoes de musica
  ficam registradas para aprendizado local. Nao promover essas tentativas como
  licao de sucesso nem editar uma skill canonica como se houvesse aceite.

## Checkpoint por executavel

| ROM | SHA-256 | O que o registro anterior sustenta |
| --- | --- | --- |
| Baseline, 393216 bytes | `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2` | Identidade local preservada; validacao antiga tem erros e drift |
| O, 524288 bytes | `04f24e1cd52f227c5e01547f2d30b9b915b45fde84a197873687243d5ef35c90` | Correcao do fade/contorno; F0 ainda consumia dois VBlanks |
| Q, 524288 bytes | `eba5b0451246dc84d620746ab79aadc311ac200eeccc705891cb173e6596b632` | Dois registros de 241 intervalos/241 VBlanks; 218 estados VRAM/CRAM iguais a O, incluindo os 216 visiveis, obtidos por lotes em dez boots |
| R, 524288 bytes | `8900504ca480cbddc7aa0c01351ff82c2638476eb5fce2ec1402e906a3d1ae7d` | Ultimo build; verificacao nativa do blackout: display desligado durante carga, CRAM preta antes do fade, paleta final correta e input desbloqueado |

Q troca a limpeza sincrona dos planos por lotes enfileirados de quatro linhas
por plano durante o preto. Contadores historicos: 6856 bytes maximos submetidos,
32 linhas por plano; fonte de zeros imutavel e retry sem avancar em rejeicao.
Essa fonte representa entradas de tilemap vazias, nao desenho de arte.

R acrescenta blackout durante o carregamento sincrono do menu herdado. O video
de Q revelou uma faixa magenta: a paleta de origem tinha `0x0E0E` no indice 0
e era publicada antes da correcao do backdrop. R monta o alvo em RAM e o revela
apos a carga. A carga do menu continua sincrona; nao declarar que toda DMA do
aplicativo foi convertida para fila ou que a transicao inteira e 60 fps.

A prova nativa de R e complementar. Ainda faltam nesta ROM: repeticao de cadencia,
varredura VDP completa, casos de handoff/replay, revisao de video e sincronismo AV.
O controle negativo do coletor de blackout contra Q tambem ficou pendente.
Nao usar o resultado tecnico pontual como aprovacao visual/sonora ou entrega.

## Ordem de retomada

1. Ler este registro, memoria, contratos, curadoria e o checkpoint JSON. Conferir
   identidades locais e a disponibilidade das evidencias; em clone novo, assumir
   os artefatos de `out/` ausentes ate recuperacao ou nova coleta.
2. Reconciliar docs que ainda descrevem O e flags do build padrao. Identificar
   uma candidata por SHA antes de executar ou comparar qualquer resultado.
3. Qualificar a rota de build/captura no host atual. Ferramentas compartilhadas
   nao incluidas neste PR devem ser integradas/revisadas separadamente. Novo
   build precisa de novo hash e nova evidencia; nao recertificar ROM antiga.
4. Mostrar a candidata identificada ao usuario e obter feedback sobre dispersao,
   energia, contorno e composicao. Trabalhar a direcao de cena a partir dele.
5. Completar os gates tecnicos da mesma candidata, com audio, input, teardown,
   budget e evidencia BlastEm coerentes; reconciliar validacao generica e status.
6. Revisitar a assinatura musical conforme o briefing ja registrado quando o
   usuario retomar essa etapa. O estado atual permanece em desenvolvimento.
7. Resolver explicitamente o uso de assets/BGM V2 no menu antes do arquivamento.
   Somente apos validacao completa e aceite humano, propor promocao do template
   e arquivo reversivel V2; migracoes de outros projetos continuam separadas.

## Conservacao e verificacao desta pausa

- Commit/PR de rascunho preservam somente este laboratorio. Runtime nao foi
  alterado, recompilado ou testado nesta rodada de 2026-10-24.
- Fontes, assets, contratos e snapshots uteis sao versionados; builds, videos,
  SRAM, dumps, executaveis host e espelhos temporarios ficam locais em `out/`
  ou nas pastas de rascunho ja existentes, sem remocao.
- `branding_v3_checkpoint_20261024.json` inventaria os arquivos versionados e
  as evidencias locais selecionadas por caminho, tamanho e SHA-256. A conferenca
  atual de hashes nao equivale a uma nova execucao/validacao.
- O auditor de layout do workspace encontrou `out.broken_20261022` em Mugenesis,
  fora deste owner; a pausa nao corrige ou incorpora esse trabalho alheio.
- O PR registra pendencia para retomada. Merge, arquivamento V2, promocao ao
  template e curadoria canonica continuam fora desta rodada.
