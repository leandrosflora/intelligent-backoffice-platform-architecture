# Observabilidade

## Stack local

O profile `observability` adiciona:

| Componente | Responsabilidade | URL local |
|---|---|---|
| Prometheus | coleta e avaliação de métricas | `http://localhost:9090` |
| Grafana | dashboard operacional | `http://localhost:3000` |
| OpenTelemetry Collector | recepção e roteamento de traces | `localhost:4317` / `4318` |
| Jaeger | consulta de traces | `http://localhost:16686` |

O Grafana local utiliza `admin` / `admin`. Essa credencial existe somente na baseline de desenvolvimento.

## Executar

```bash
OTEL_TRACING_ENABLED=true docker compose --profile observability up --build
```

## Telemetria exposta

A API publica `/metrics` com séries de baixa cardinalidade:

- `backoffice_http_requests_total`;
- `backoffice_http_request_duration_seconds`;
- `backoffice_policy_decisions_total`;
- `backoffice_policy_decision_duration_seconds`;
- `backoffice_workflow_transitions_total`;
- `backoffice_executions_total`;
- `backoffice_reconciliations_total`;
- `backoffice_idempotency_total`;
- `backoffice_intelligence_outcomes_total`.

IDs de caso, tenant, documento, usuário e correlação não são labels Prometheus. A correlação é propagada em spans, não em dimensões de métrica.

## Traces

A API cria spans para requisições HTTP, decisões de policy e operações de domínio. O Collector adiciona o atributo `architecture.baseline=executable-reference` e envia os traces ao Jaeger.

A baseline não envia conteúdo integral de documentos, rationale sensível ou payloads financeiros aos traces.
