# Failure Patterns

Registre aqui falhas, falsos positivos, tentativas ruins e decisoes que nao devem ser repetidas sem nova evidencia.

| Data | Classificacao | Contexto | Falha observada | Causa provavel | Mitigacao | Evidencia |
|---|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que falhou] | [causa] | [como evitar] | [log/screenshot/hash] |
| 2026-10-16 | `local_note` | Otimizacao de sonda e visibilidade | Varredura linear da sonda e cache de visibilidade passaram em equivalencia, mas nao reduziram VBlanks do respectivo par. | A contagem de operacoes C nao quantifica o custo nem demonstra cruzamento do deadline 68000. | Rejeitar ambas, restaurar fonte exata, guardar ROM/trace e exigir evidencia nova antes de reabrir a hipotese. | `out/logs/splash_v3_linear_probe_rejection_20261016.json`; `out/logs/splash_v3_visibility_cache_rejection_20261016.json`. |
| 2026-10-15 | `local_note` | `branding_sequence_v3`, sweep F180-F209 | Usuário rejeitou o resultado ROM SHA `9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006` como monótono, sem a animação e energia combinadas. | O diretor de cena transformou o pedido em variação de posição, mas não em fases de vida, linguagem visual por partícula, rastro, flicker e dissipação; os oito frames eram alternados por índice global. | Traduzir cada partícula em origem/timing/trajetória + nascimento/ativo/fade, perfil de quadros e rastro; declarar limites de hardware e checks de leitura antes do build; revisar a cena viva com o usuário. | `doc/curation/splash_v3_wind_lifecycle_motion_contract_v002_20261015.json`; ROM rejeitada e medição antiga vinculadas no próprio contrato. |
| 2026-10-15 | `local_note` | `branding_sequence_v3`, sweep v003 e fade do wordmark | O usuário relatou que as partículas ainda ficavam aglutinadas e que o contorno do SGDK perdia definição quando o brilho azul escurecia. | As seis trajetórias iniciavam e terminavam em janelas próximas, compartilhavam um corredor visual e não havia medida de distância mínima entre centros; os três tons mais escuros do contorno permaneciam quase pretos durante a redução do fundo. | Variar início, duração e distância por partícula; exigir três bandas de velocidade, dois desvios de vento independentes e separação mínima medida; elevar somente a rampa azul do contorno no início do fade, preservando os pixels e a paleta de preenchimento. | ROM v004 `c06e20c46c7eb211f5300ed1919f38192cc9d76425605987d31b22f699f8cc1f`; `doc/curation/splash_v3_wind_dispersal_contract_v004_20261015.json`; `out/logs/splash_v3_wind_dispersal_scanline_v004_20261015.json`; captura suplementar BlastEm v004. |

## Regras

- 2026-10-16: o contrato v004 continha dois handles Y diferentes do C compilado. A medida de 23,54 px nao representava exatamente aquela ROM. Reconciliacao v005: 154 coordenadas conferidas com a referencia C, minimo 22,09 px. Exigir binding entre contrato numerico e C/tabela compilada antes de atribuir uma medicao offline ao runtime. Evidencia: `doc/curation/splash_v3_wind_dispersal_contract_v005_20261016.json` e `out/logs/splash_v3_wind_dispersal_scanline_v005_20261016.json`.
- 2026-10-16: a ajuda do BlastEm 1.0 lista `bindown`, mas o binario aceita `binddown` com argumento string. O roteiro inicial falhou em enviar input; foi preservado como coleta falha, nao como defeito da ROM. A segunda coleta confirmou B e START por `gInput` e pelos estados reais. Evidencia: `out/evidence/splash_v3_handoff_readiness_v001_20261016/native_cycle_02/handoff_observation.json`.

- Falha sem evidencia deve ser marcada como hipotese.
- Solucao nao comprovada nao vira recomendacao.
- Se a falha indicar risco canonico, classifique como `needs_human_review`.

| 2026-10-16 | `local_note` | Sonda de visibilidade | Comparar enum HIDDEN=1 com bitmask interno (oculto=0) conta sprites inexistentes na SAT. Corrigir semantica e conferir contra VRAM antes de aceitar budget; nao retrair indiscriminadamente picos ativos. | `out/reviews/splash_v3_convergence_cost_20261016/review_summary.json` e controle negativo de largura. | Apenas observador local; sem promocao canonica. |
| 2026-10-16 | `local_note` | Otimizacao sem ganho | Setter menor em C aumentou funcao alem do limiar de inline e piorou 255 para 276. FORCE_INLINE recuperou 255, sem ganho; duas variantes rejeitadas, fonte restaurada por hash. | `out/reviews/splash_v3_convergence_cost_20261016/cpu_frame_budget_report.json`; snapshots em `rascunho/manual_tile_path_20261016/`. | Equivalencia funcional de 7680 casos nao prova velocidade. |

## 2026-10-16 — ownership da paleta e observacao

- Falha comprovada: lift de contorno via DMA_QUEUE_COPY seguido por PAL_fadeOut leu CRAM anterior e sobrescreveu a cor. O controle em F210 tinha17-19=[0,0,0]; fonte explicita corrigida esta no readback. Rever ownership/preparo de paleta, alem de adjetivos de direcao. `out/reviews/splash_v3_visible_deadline_20261016/review_summary.json`.
- Screenshot preto de debugger nao foi aceito como visual. Script longo parou com28 dumps; a coleta por lotes preserva as sessoes e limita comandos, sem transformar lotes em continuidade temporal. Tentativa P sem ganho foi retirada.
