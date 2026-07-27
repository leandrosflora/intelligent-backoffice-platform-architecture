# SLOs e alertas

Os SLOs do P5 estão em `observability/slos.yaml` e possuem status `BASELINE_EXECUTABLE`.

| SLO | Target inicial | Evidência |
|---|---:|---|
| Disponibilidade HTTP | 99,9% | ratio de respostas sem 5xx |
| Latência HTTP | p95 menor que 500 ms | histograma Prometheus |
| Disponibilidade do PDP | 99,95% | decisões sem resultado `unavailable` |
| Segurança de execução | zero efeito duplicado | idempotência e resultados de execução |
| Qualidade dos evals | 100% no dataset sintético v1 | relatório versionado de evals |

## Regras

- Targets são provisórios até existir baseline com carga representativa.
- Respostas 4xx esperadas não contam como indisponibilidade da plataforma.
- A ausência do PDP é erro operacional e mantém o comportamento fail-closed.
- Um resultado de execução ambíguo gera reconciliação; nunca retry cego.
- A violação de eval impede avanço automático do change set.

## Alertas

As regras Prometheus cobrem:

- aumento de 5xx;
- latência p95 acima do target;
- indisponibilidade do PDP;
- entrada em reconciliação;
- pico de conflito de idempotência.

Cada alerta referencia um runbook versionado no repositório.
