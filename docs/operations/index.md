# Operações

O P5 transforma os requisitos operacionais em uma baseline executável e versionada.

## Artefatos

- [Observabilidade](observability.md): métricas, traces, dashboard e stack local;
- [SLOs e alertas](slos.md): indicadores, targets e regras Prometheus;
- [Evals](../evaluation/index.md): dataset, thresholds e quality gates;
- runbooks de erro HTTP, PDP, reconciliação, workflow, telemetria e regressão de eval.

## Princípios

- correlação ponta a ponta sem usar identificadores sensíveis como labels;
- fail-closed quando o PDP está indisponível;
- métricas de baixa cardinalidade;
- traces sem documento integral ou payload financeiro;
- alertas vinculados a owner, SLO e runbook;
- evals executados antes de promover capacidades inteligentes.

## Limites

A stack local demonstra instrumentação e resposta operacional. Ela não substitui observabilidade gerenciada, retenção corporativa, plantão, capacidade, testes de carga ou operação 24x7.
