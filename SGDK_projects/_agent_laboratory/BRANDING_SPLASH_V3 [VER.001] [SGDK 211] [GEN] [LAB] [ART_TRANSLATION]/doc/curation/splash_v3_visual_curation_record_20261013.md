# Curadoria visual e sonora — Splash V3 — registro inicial 2026-10-13, atualização 2026-10-14

## Estado e decisao do usuario

Splash V3 esta **em desenvolvimento** e deve ser revista futuramente para aprimoramento. O usuario autorizou continuar a parte visual e registrar os criterios de curadoria. Esta autorizacao cobre placeholders e preview isolado no laboratorio; nao aprova a qualidade visual ou musical final, o model sheet, a ROM de producao, a promocao ao template ou o arquivamento da FORJA V2.

A ROM canonica V2, o template e os projetos consumidores permanecem intactos. A decisao e registrada em `doc/curation/splash_v3_user_development_decision_20261013.md` e `doc/branding_v3_development_contract.json`.

## Atualizacao visual — 2026-10-14

- A inspeção identificou RGB magenta no índice transparente dos PNGs. O viewer de imagens mostra esse RGB em áreas transparentes; a captura da ROM anterior tem faixas magenta externas à viewport, então não atribuo esses pixels à arte sem nova captura nativa.
- A primeira tentativa de gravar RGB preto em todos os índices zero tornou a ROM preta em BlastEm (`437c38299181107647efae737c84eaf9db37302cbd44784d3f144b36240998e3`). Essa variante foi preservada em `out/revisions/splash_v3_palette_zero_black_all_20261014/` e rejeitada como regressão.
- O builder agora mantém a chave magenta que o ResComp usa nos wordmarks e no sprite. Só o índice zero da placa BG_B grava preto válido para a cor de fundo do VDP; o self-check exige esse papel e valida todas as cores visíveis na grade 9-bit. O conceito-fonte nao foi alterado.
- A nova variante ainda exige build e observação de ROM antes de se concluir se a correção é apropriada. Ela continua placeholder; não aprova arte, lettering, model sheet ou música.

## Brief vinculante

- Assinatura curta, positiva, heroica e confiante, com energia de aventura e acabamento premium.
- Movimento musical articulado: motivo curto e memoravel, pausas audiveis, lead separado de stabs e brilho cristalino breve. Ataques devem ter funcao; evitar cama continua, som abafado/monofonico, timbres que parecem instancias iguais, brilho constante, reverb longo e resolucao sombria.
- A direcao visual deve apoiar a mesma energia: inicio limpo, expansao azul, convergencia legivel, revelacao de SGDK, FORGE subordinado, acento cristalino direcional e saida clara.
- Referencias Capcom/Konami sao apenas emocionais, sem copiar melodias, logos ou timbres identificaveis. A agressividade SNK nao e alvo.
- Sem glow difuso como substituto de animacao, ruido cristalino que esconda as letras, flicker ou fanfarra agressiva.

## Historico de escuta a preservar

1. A primeira composicao tocava, mas soava abafada e monofonica; as camadas pareciam variacoes do mesmo timbre.
2. Uma versao posterior melhorou, mas a qualidade musical ainda foi considerada baixa; o usuario pediu mais cristalino.
3. A seguinte foi rejeitada por soar continua e monotona, sem o animo e a energia combinados.
4. V012 segue como referencia musical positiva. V013 e V014 foram rejeitadas. V015 pode ser usada no desenvolvimento, sem aprovacao musical final.
5. A proxima escuta deve ocorrer na ROM visual completa, por pelo menos dois ciclos, registrando energia, articulacao, separacao timbrica, brilho cristalino e resolucao.

Historico detalhado: `doc/curation/splash_v3_curator_record_20261012.md`.

## Direcao visual provisoria

Composicao V003: fundo marinho escuro; cristais eletricos azuis/cianos nas bordas; campo negativo limpo atras do lockup; SGDK dominante; FORGE menor; sweep breve. A direcao e provisoria e autoriza WIP no laboratorio.

| Asset WIP em `res/` | Dimensao | Tiles unicos | Cores visiveis | SHA-256 |
|---|---:|---:|---:|---|
| `branding_v3/splash_backdrop_v3_320x224.png` | 320x224 | 610 raw / 604 ResComp H/V | 15 | `8473a522c83a29ec521b93ef5c1289c9ff505ccb0268ee39793b317fb0430042` |
| `branding_v3/splash_sgdk_wordmark_v3_224x48.png` | 224x48 | 117 raw / 114 ResComp H/V | 13 | `63a80aeebc52b0bdf6c01ab540a9ff1a61649360d93f561b3fa54613c4ffb460` |
| `branding_v3/splash_forge_wordmark_v3_192x32.png` | 192x32 | 83 raw / 82 ResComp H/V | 13 | `2e79dc8b25f6e22dc3ccf9b30a1810108948f4ed407384b5632caea99bc70f5c` |
| `sprites/splash_particle_v3_8x8_strip.png` | 64x8, 8 quadros | 8 raw / 8 ResComp H/V | 9 | `3937b6d905eedccfff3204f251235e72e001412b1406a343bcc83f6fef3724ea` |

Os quatro arquivos passam grid 8x8, index 0 transparente e cores no grid 9-bit. A soma bruta de tiles unicos dos quatro PNGs e 818; apos H/V dedup do ResComp, o payload visual e 808 tiles (25.856 bytes 4bpp). `audit_tile_residency.py` mediu pico de 808/1740 tiles de arte disponiveis (46,4%); isso nao fecha planos, fontes, SAT, outras reservas ou o budget total da cena. O fundo ainda usa 604 tiles runtime, muito acima do alvo curatorial de vocabulario 20-40; reautoria/reducao continua como revisao futura. Todas as fontes de referencia e hashes estao em `data/source_art/branding_v3/premium_source_manifest.json` e `doc/asset_provenance_manifest.json`; status permanece `placeholder`.

O contrato `doc/contracts/visual_source_of_truth_branding_splash_v3.json` trava a direcao apenas para desenvolvimento. O scan de linhagem passou sem referencias derivadas proibidas, mas isso nao aprova fonte autoral, pixel art final ou model sheet. O model sheet continua proposta em `doc/curation/splash_v3_visual_model_sheet_proposal_20261013.json`.

## Coreografia e geometria medida

- NTSC H40, viewport 320x224, duracao 240 quadros.
- F0-23: tela preta e preload incremental em chamadas de ate 180 tiles; o envelope VBlank completo ainda nao foi medido.
- F24-83: 64 particulas 8x8 com nascimentos escalonados; expansao radial de raio ate 88 px e contracao parcial. Cue de energia F24, musica a partir de F60.
- F84-119: convergencia para uma grade uniforme dentro da placa SGDK; fade-in da placa completa durante 36 quadros. Nao existe placa de contorno separada nem ancora por glifo.
- F120-149: hold da paleta completa SGDK; cue de lock F118.
- F150-179: FORGE aparece embaixo por fade de 12 quadros.
- F180-209: sweep de sete particulas 8x8 reutilizadas; y=76,84,92,100,108,116,124; x parte de -16 e avanca 10 pixels/quadro. Cue em F178.
- F210-239: fade das 64 cores CRAM; cue tail F210.
- F240+: o preview para o audio, limpa BG_A, escreve `A: REPLAY SPLASH V3` e espera A. A captura utilizavel desse prompt ainda falta.

A medicao local cobre 990 entradas e usa o simulador v1.2.0; os self-checks do simulador e do runner passaram. Perfil selecionado: 64x8x8, maximo 17 sprites/136 pixels por scanline, 64 links, pior quadro 108. Isso usa 85% do limite de contagem H40; a folga existe, mas a densidade deve continuar legivel. O sweep 7x8x8 mede 1 sprite/8 pixels por linha. Os perfis de 80x8x8 e de 48/64/80 em 16x16 excedem limites. Report atual: `out/logs/splash_v3_scanline_visual_runtime_20261013.json`.

Esse report e local ao laboratorio e so cobre geometria de sprites. O gate global segue bloqueado por `project_source_mirror_stale` em 20 espelhos ativos de `runtime_probe` em 11 projetos. Nao foram sobrescritas copias externas. Sem claim de budget total de VRAM, tile residency, DMA, CPU, DAC ou FPS sustentado.

## Build e observacao em emulador

- ROM de preview: `out/rom.bin`, 262.144 bytes, SHA-256 `3478ae036d80d8df8fc99259ab6e1175c27ceeb9b33bf4f5ec4c724f8010cfd0`.
- Build SGDK 2.11 via Linux/Wine bridge; SDK content SHA-256 `cf931069f351fa3fa74d66685f7ea5d4532218e64424651e415ab2df373f9ca7`; flag `SPLASH_V3_VISUAL_PREVIEW`.
- BlastEm local pinned 1.0.0 mostrou quadros selecionados. `out/logs/splash_v3_visual_preview_report_20261013.json` tem status `preview_observed_unsealed`, nao `testado_em_emulador`.
- Capturas limpas derivadas do viewport: `out/blastem_splash_v3_visual_preview_20261013/splash_v3_visual_viewport_320x224.png` e `splash_v3_convergence_viewport_320x224.png`. Os PNGs originais de janela continuam preservados. As faixas magenta externas nas linhas 0-17 e 466-479 foram removidas apenas dos derivados de apresentacao.
- A captura de janela inclui apenas instantes. Varias tentativas posteriores devolveram preto pelo caminho X e foram excluidas. Nao ha video completo, captura canonica Flatpak, SRAM ou `visual_vdp_dump.bin`. 59.9 fps no titulo e valor instantaneo, nao medida sustentada.

## Observacoes curatoriais do WIP

- O lockup e legivel no frame selecionado; SGDK domina e FORGE funciona como segunda linha.
- Os vetores nas bordas enquadram o centro escuro. Revisar densidade dos cantos inferiores e quantidade de brilhos para evitar moldura excessivamente carregada.
- No quadro de convergencia, particulas brilhantes cruzam o SGDK. Julgar leitura ao longo do movimento, nao apenas no frame final.
- O sweep precisa de captura em movimento para avaliar direcao, duracao e se preserva as letras.
- O fim precisa mostrar claramente o prompt de replay; uma tela preta sem instrucao nao e uma finalizacao aceitavel para a previa de curadoria.
- Reavaliar a textura do fundo, a autoria do lettering e o tile budget antes de converter placeholders em pixels finais.

## Checklist para a revisao futura

1. Assistir pelo menos dois ciclos completos na ROM exata e conferir reveal, convergencia, sweep, fade e replay.
2. Rever a imagem a 1x/320x224 e em escala maior sem interpolation; medir hierarquia, luma, bordas, cristais e ruido nos cantos.
3. Aprovar rota de lettering, model sheet e fonte autoral antes de pixels finais; registrar hashes e proveniencia.
4. Ouvir dois ciclos completos e registrar retorno humano de energia, pausas, motivo, camadas, acentos cristalinos e resolucao.
5. Medir tile residency/VRAM, envelope VBlank/DMA, CPU, ownership DAC e 60fps sustentados com audio na cena pesada.
6. Usar captura canonica BlastEm ligada ao hash final, screenshot, SRAM e VDP dump conforme contrato; repetir apos qualquer rebuild.
7. Manter a ROM canonica V2, FORJA V2 e template intactos ate todos os gates e aprovacao final especifica do usuario.
