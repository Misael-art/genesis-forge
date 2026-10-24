# Splash V3 - laboratorio em desenvolvimento

**Pausado por solicitacao humana em 2026-10-24.** Este diretorio preserva o
trabalho experimental de branding da SGDK Forge. Nao e o template canonico.

## Pendencia e retomada

- [BRANDING-001: confusoes de branding e trabalho pendente](doc/pending/branding_v3_resume_20261024.md).
- [Identidades, flags e inventario do checkpoint](doc/pending/branding_v3_checkpoint_20261024.json).
- [Memoria operacional](doc/10-memory-bank.md) e [changelog](doc/changelog/changelog.md).

O checkpoint conserva codigo, headers, recursos, fontes autorais, contratos,
historico local de direcao e ferramentas de diagnostico. Arte e musica continuam
em desenvolvimento. Nenhuma medicao tecnica substitui o aceite humano.

## Identidade dos builds

| Papel | SHA-256 da ROM | Situacao |
| --- | --- | --- |
| Baseline local `out/rom.bin` | `5d47ef1636c6c63cabc235c86f1ec7601c8cecab431ee1532e5ef7a6ded93cf2` | Preservada; nao contem automaticamente as candidatas |
| Candidata Q, limpeza enfileirada | `eba5b0451246dc84d620746ab79aadc311ac200eeccc705891cb173e6596b632` | Cadencia e amostras de VDP observadas nesta ROM |
| Candidata R, blackout do menu | `8900504ca480cbddc7aa0c01351ff82c2638476eb5fce2ec1402e906a3d1ae7d` | Ultimo build; verificacao de blackout, validacao integral pendente |

As ROMs, videos, SRAM e dumps ficam localmente em `out/`, fora deste checkpoint
Git. O inventario registra os caminhos e hashes disponiveis na data da pausa;
um clone do PR nao contem esses arquivos nem reproduz automaticamente as provas.

## Build futuro

Usar o wrapper central de `tools/sgdk_wrapper/` e o SDK 2.11 deste workspace.
Consultar primeiro o roteiro de retomada e as flags exatas da candidata R no
checkpoint. O build padrao nao ativa todas as opcoes experimentais. O diagnostico
nativo depende de ferramentas compartilhadas que ainda nao existem na base deste
PR; essas dependencias estao declaradas no inventario.

## Limites desta preservacao

O menu ainda usa arte e BGM da V2. As copias V1/V2 presentes neste laboratorio
sao dependencias e historico; nao significam escolha de direcao ou arquivamento.
Template, FORJA V2 e projetos consumidores continuam sem promocao ou migracao
por esta tarefa. O README anteriormente herdado do modelo foi substituido para
parar de apresentar este laboratorio como base oficial.
