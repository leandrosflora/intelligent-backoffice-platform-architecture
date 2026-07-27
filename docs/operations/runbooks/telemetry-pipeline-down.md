# Runbook — pipeline de telemetria indisponível

## Trigger

Collector, Prometheus, Grafana ou Jaeger indisponível.

## Diagnóstico

1. Verifique os containers do profile `observability`.
2. Consulte logs do OpenTelemetry Collector para falha de exportação.
3. Valide o target `vertical-slice` no Prometheus.
4. Confirme provisionamento dos datasources do Grafana.
5. Verifique se a API iniciou com `TRACING_ENABLED=true`.

## Mitigação

- restaure a cadeia Collector → Jaeger;
- restaure a coleta Prometheus sem reiniciar o workflow de negócio;
- preserve métricas locais até a recuperação;
- não inclua dados sensíveis adicionais para facilitar diagnóstico.
