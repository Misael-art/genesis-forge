# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

## Retração — 2026-10-15

A nota anterior sobre o sweep de sete trajetórias (`9d34b114b86311e6b7924205d7317af7472f5624e2848ed214a328dc44272006`) foi retirada como sucesso artístico após o usuário rejeitar a ROM por monotonia e falta de energia. A medição geométrica continua válida como dado daquele WIP, mas não demonstra qualidade. Nenhum padrão de animação do sweep está qualificado como sucesso até revisão da nova captura.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |
| 2026-10-16 | `local_note` | Handoff Splash V3/menu | Prontidao de entrada/fade/DMA manteve o mutex ativo mesmo com contador visual zero; B chegou a ROM durante o bloqueio e foi ignorado, depois reiniciou a splash; START abriu a demo. | `out/evidence/splash_v3_stable_geometry_v005_20261016/native_handoff_01/handoff_observation.json`; ROM `7407e48ee36f0f060c41761cd84aa6f1e0742069abef38f6fcaf462adfaf335f`. | Oito casos locais; nao substitui QA de todos os estados, load failure ou gate canonico. |
| 2026-10-16 | `local_note` | Coreografia inteira deterministica | Gerar coordenadas com as funcoes C originais e conferir todos os 6.324 pares nos bytes da ROM reduziu o custo sem reduzir particulas ou alterar trajetorias. Com geometria 8x8 validada por guarda, expansao usa 60 VBlanks/60 updates e sweep 30/30; SAT igual em nove quadros. | `out/logs/splash_v3_motion_lut_compiled_equivalence_v005_20261016.json`; `out/logs/splash_v3_stable_geometry_sat_equivalence_20261016.json`; `out/reviews/splash_v3_handoff_motion_20261016/cpu_frame_budget_report.json`. | Caminhos deterministicos pequenos; paga 25.296 bytes de ROM. Convergencia ainda fora do deadline e qualidade artistica continua sem aceite humano. |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.

| 2026-10-16 | `local_note` | Observador SAT | Medir cadeia submetida com deltas count/width empacotados reduziu custo e removeu sprites ocultos. 15 cadeias igualam VRAM; 12 amostras de largura medidas conferem; cadencia repetiu 255/241. | `out/reviews/splash_v3_convergence_cost_20261016/review_summary.json`. | Scanner no cache submetido nao e readback hardware; dumps separados provam 15 instantes, nao todos os quadros nem qualidade. |

## 2026-10-16 — reducao de custo com fidelidade medida

- 114244 casos de posicao SGDK e327680 de atributos de mapa, mais dumps reais, permitiram guardar caminhos manuais e preparar dados durante o preto sem mudar pixels/coordenadas/reveals. Dois traces visiveis216/216 e todos216 estados SAT medidos. `out/reviews/splash_v3_visible_deadline_20261016/review_summary.json`.
- Exportar em beats tranquilos preservou150 medicoes e um snapshot final coerente em F239. Nao omitir observador nem confundir bytes da maior operacao com a soma da fila. O max observado aqui e5832 somados/5760 maior operacao. Limites: WIP local, primeiro F0 e QA final abertos; sem sucesso artistico ou promocao automatica.
