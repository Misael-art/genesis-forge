# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Nenhum item aqui esta promovido.

Reconciliacao 2026-10-16: a medida fiel ao C e 22,09 px, no contrato v005, com 154 posicoes ativas conferidas contra as funcoes C. O valor de 23,54 px na linha historica abaixo descreve o contrato offline v004, que tinha dois handles Y divergentes da ROM. A candidata de skill deve exigir esse binding numerico antes de usar a medida como evidencia de runtime.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| 2026-10-15 | `failure_driven_workflow_candidate` | Aprimorar `cutscene-cinematic-direction` com um handoff de partículas que exige ciclo visual completo, ao menos três bandas de velocidade, duas trajetórias de vento não uniformes, separação mínima quantificada, rastro/flicker e contraste do contorno após o fade. | O v003 continuou visualmente aglutinado apesar das posições independentes; o handoff também não definiu um piso de contraste para o nome quando o campo escurece. | Feedback direto do usuário; contrato v004; ROM SHA `c06e20c46c7eb211f5300ed1919f38192cc9d76425605987d31b22f699f8cc1f`; distância mínima medida 23,54 px. A revisão humana da captura permanece pendente. | Uma única cena e uma métrica geométrica não provam aceitação estética ou generalização. Não promover nem editar a skill compartilhada com esta evidência isolada. | Curador de cena/arte deve revisar a captura v004 e o feedback humano; só reconsiderar promoção depois de aceitação e reprodução independente em outra cena. |


## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.

## Candidato local 2026-10-16 — paleta enfileirada e fade

Curador deve considerar para `cutscene-cinematic-direction`, `sgdk-runtime-coder` e dono de CRAM: especificar quem escreve a fonte do fade e em qual instante. Escrita enfileirada nao altera imediatamente a CRAM lida por PAL_fadeOut. Prova: `out/logs/splash_v3_final_palette_sram_proof_20261016.json`, ROM `04f24e1cd52f227c5e01547f2d30b9b915b45fde84a197873687243d5ef35c90`. Requer revisao humana e reproducao antes de generalizar; nenhum skill compartilhado foi alterado. O feedback de direcao e o aceite visual continuam abertos.
