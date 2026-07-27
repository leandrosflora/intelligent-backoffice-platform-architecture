# C4 — Containers implementados

Esta visão representa o estado executável introduzido pelo P4.

![Containers implementados](../assets/diagrams/c4-container-current.svg)

## Baseline implementada

| Container | Responsabilidade |
|---|---|
| Intelligent Backoffice API | modular monolith com workflow e módulos do primeiro case |
| PostgreSQL | aggregate, versão, idempotência, timeline e outbox |
| OPA | autorização e obrigações em runtime |
| Quality Pipeline | build, contracts, policies e E2E |
| MkDocs | documentação publicada |

## Limites

O diagrama não apresenta como implementados:

- Kafka ou Redpanda;
- object storage;
- LLM ou modelo multimodal;
- Core bancário;
- OpenTelemetry, Prometheus, Jaeger ou Grafana;
- identidade corporativa.

Esses elementos permanecem na arquitetura-alvo.

**Fonte PlantUML:** `C4/c4-container-current.puml`.
