# Deployment local

O deployment local proposto para o futuro vertical slice usa Docker Compose e dados exclusivamente sintéticos.

![Deployment local](../assets/diagrams/c4-deployment-local.svg)

## Zonas

| Zona | Conteúdo |
|---|---|
| Application | APIs, workflow, agents, document intelligence, approval, execution e OPA |
| Data and messaging | PostgreSQL, Kafka/Redpanda e object storage |
| Observability | OpenTelemetry, Prometheus, Jaeger e Grafana |
| External mocks | Core, notificações, modelo e malware scanner |

Esse desenho orienta o P5. O P2 não cria os containers executáveis.

**Fonte PlantUML:** `C4/c4-deployment-local.puml`.
