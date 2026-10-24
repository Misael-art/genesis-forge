# 17 - Audio Design - Splash V3

## 1. Objetivo

Criar uma assinatura sonora original de 2 a 4 segundos: ataque imediato, energia positiva, movimento, brilho digital e resolução maior. As referências de Capcom, Konami e SNK descrevem características amplas; nenhuma melodia, logo, gravação ou patch reconhecível é copiado.

## 2. Histórico de escuta

- V010: rejeitada pelo usuário por baixa qualidade musical.
- V011: supersedida porque glints PSG se sobrepunham a cues PCM.
- V012: recebeu retorno positivo ("ficou bem melhor") e permanece arquivada como referência.
- V013 e V014: rejeitadas pelo usuário por soarem contínuas e monótonas, sem a energia e a animação combinadas.
- V015: aceita pelo usuário para desenvolvimento. Isso autoriza integrar e aprimorar a composição, mas não aprova sua qualidade musical final. A revisão auditiva detalhada fica para depois da integração visual.

## 3. Composição V015

- Centro tonal: C maior; compasso 6/8; 120 BPM; duas barras; 180 quadros NTSC / 3 segundos.
- Motivo: C5-G5-E5-F5 | D5-G5-B5-C6. A chamada ataca nos quadros de score 0/8/16 e 42; a resposta ascendente entra em 72/81/90/102. Os gates do brass somam 52/180 quadros, com releases FM mais rápidos para separar cada ataque.
- O baixo marca quatro pulsos curtos C3/F2/G2/C3 nos quadros 0/42/72/102. A harmonia dá stabs E4/A4/B3/E4 sincronizados; não há pad ou voz grave contínua.
- Brilho cristalino: pings FM aditivos E6/G6/C7 nos quadros 26/88/106, com 3-4 quadros cada. PSG fica silencioso.
- A música começa no quadro de cena 60, depois do cue de subida. Todas as notas FM terminam até o quadro 174. O quadro 174 deixa quatro quadros antes do sweep.

### Candidata corrente V016/VGM4

- Revisao stereo sobre a chamada-resposta C maior de V015: 6/8 a 120 BPM, duas barras, 180 quadros NTSC. O brass central permanece nos dois lados para mono TV; pulsos de baixo ficam a esquerda e stabs/acentos cristalinos a direita.
- O arranjo preserva ataques curtos, pausas e tres pings FM cristalinos breves; PSG segue silencioso. As vozes estao paneadas, nao avaliadas por escuta humana.
- Score: `data/source_audio/splash_v3_sonic_logo_score_v4.json`, SHA-256 `ec6af8706af37e249a648473e1e741622fd33a7d254d9cbd079748d13c57cfcf`. VGM: `res/music/splash_v3_sonic_logo_v4.vgm`, SHA-256 `fc9bacd1888d50634077c655c45068fbf07ee2e279a4a4bdcf85fda6f77af7d3`.
- Trecho integrado de 3,2 s para primeira escuta humana: `out/audio/reviews/v007_current_v16_audio_review_20261014/splash_v3_v016_blastem_review_3p2s.wav` (SHA-256 `d2952652d3cbd61ebca49281ac75fadcb56015aee7489b3e8071fc216c273287`) e MP3 de conveniencia no mesmo diretorio (SHA-256 `2437994de7b4350cbc1737ce5181218136f561cb6b3540e55e20cf2b6844eab0`).
- Prévia de duas passagens: `out/audio/reviews/v008_v016_two_cycle_20261014/splash_v3_v016_two_cycle_stereo.wav` (stereo) e `splash_v3_v016_two_cycle_mono_fold.wav` (mono), manifesto `out/audio/reviews/v008_v016_two_cycle_20261014/splash_v3_v016_two_cycle_review.json`. O ciclo de 3 s capturado foi repetido uma vez; isso prepara a escuta da emenda, mas não substitui uma captura direta de dois ciclos na ROM atual.
- Captura direta de duas passagens: ROM isolada de preview `out/profiling/splash_v3_v016_rom_two_cycle_capture_20261015/rom.bin`, SHA-256 `35af30bb5b0cfe52fb527858b9cd164ed496ee46f144e2396fd151841fb16e71`; BlastEm Flatpak 1.0.0 em Xvfb privado. A tela ligada ao mesmo hash registra os dois conjuntos de cues e `MUSIC 358/358 DROP:0`. WAV stereo e mono de 8 s derivados dos primeiros 8 s de `audio.raw` estao em `out/audio/reviews/v009_v016_two_cycle_rom_capture_20261015/`; manifesto ao lado declara hashes e processamento. É evidência direta para audição da candidata V016/VGM4; a sessão não foi selada, a ROM é uma build isolada (não `out/rom.bin` V017), e o segundo recapture após ajuste visual da tela falhou no diálogo GTK antes de gerar nova evidência. Isso não altera o áudio reproduzido nem aprova a música.
- Limite da previa: o corte vem da captura BlastEm da ROM V012 visual preview (SHA-256 `234f73abc68e94d9175fe2b4714bb5cd7d531904113f150bcd9c49751ff55eb7`), feita entre 1,0 e 4,2 s. Snapshot e ROM V017 compartilham hashes do VGM4, cues PCM e `audio.c`, mas nao sao o mesmo binario. Portanto, a previa ajuda a avaliar articulacao e timbre integrado, mas nao comprova captura da ROM atual, dois ciclos, emenda de loop, budget DAC, desempenho sustentado ou aprovacao musical.
- O sidecar `splash_v3_v016_blastem_review_3p2s.provenance.json` conserva hashes, processamento e limite de claim. O manifesto `doc/sfx_bank_manifest.json` agora aponta `mus_splash_v3` para VGM4 com hash verificado; status permanece `lab`. V012 continua referencia positiva; V013/V014 permanecem rejeitadas. A escuta deve julgar se a sensacao anterior de som continuo/monotono foi resolvida.
- Revisao requerida: dois ciclos integrados, energia/animacao, articulacao e respiro, presenca do brass, separacao timbrica em stereo e mono fold-down, brilho cristalino pontual, resolucao, fadiga, emenda e equilibrio com cues PCM.

## 4. Mapa de eventos

| Quadro da cena | Evento | Relação musical | Canal |
|---:|---|---|---|
| 0-23 | silêncio | Contraste inicial | nenhum |
| 24-59 | subida de energia | Revelação digital antes da música | PCM CH2 |
| 60 | início da música | Ataque em C maior, 6/8 | FM |
| 118-129 | trava da marca | A pausa musical deixa o cue PCM sozinho | PCM CH3 |
| 132 | resposta | D5-G5-B5-C6 ascendente após o cue | FM |
| 174 | liberação final | Quatro quadros de respiro antes do sweep | nenhum |
| 178-203 | sweep | PCM sem notas musicais concorrentes | PCM CH2 |
| 210-233 | cauda | PCM conclui a resolução | PCM CH3 |
| 240 | saída | Parar XGM2 e PCM antes do menu | owner da cena |

Os quadros do score são relativos ao início musical no quadro 60. O stream VGM tem 180 quadros; as notas autorais acabam no quadro de score 114 e o restante mantém espaço para os cues sincronizados.

## 5. Ownership

- branding_v3_audio_director é o único owner de start, cues, stop e teardown.
- branding_v3_audio_architecture_card.json declara posse de FM, PSG, DAC e fallbacks.
- PCM usa XGM2_playPCMEx nos canais CH2/CH3. CH1 fica reservado ao driver.
- No Exit, parar PCM, silenciar PSG, parar XGM2 e limpar timers antes de o menu adquirir áudio.
- Se PCM falhar, usar apenas o fallback PSG curto e nomeado do evento.

## 6. QA e promoção

Conversao XGM2, estrutura do loop, auditoria de proveniencia e build sao gates tecnicos. Eles nao aprovam qualidade musical. V016/VGM4 esta integrada ao preview V017 como candidata WIP; o WAV direto de duas passagens foi disponibilizado para escuta humana, cuja aprovacao continua pendente. O fechamento exige revisão do som na ROM identificada por SHA-256, budget DAC, audio/performance estaveis e o gate canonico de BlastEm.
