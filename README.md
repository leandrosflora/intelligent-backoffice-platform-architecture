# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Vertical Slice](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml)
[![P5 Observability and Evals](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml)
[![P6 Eventing](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para automação inteligente de backoffice com agentes, processamento documental, workflows, human-in-the-loop, policies, auditoria e integração governada com sistemas corporativos.

## Case aplicado

O primeiro case é uma jornada bancária de contestação:

1. abertura e triagem;
2. recebimento e validação documental;
3. investigação;
4. recomendação explicável;
5. aprovação humana conforme alçada;
6. execução governada e idempotente;
7. reconciliação, auditoria e encerramento.

## Evolução

| Fase | Estado | Conteúdo |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Arquitetura funcional, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries, deployment e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas, catálogo e policies |
| P4 | Concluído | Vertical slice executável e OPA em runtime |
| P5 | Concluído | Evals, OpenTelemetry, métricas, SLOs, alertas e runbooks |
| P6 | Baseline executável | Redpanda/Kafka, outbox, inbox, workers, timers, retries, DLQ e replay controlado |
| P7 | Próximo | Identidade de workload, supply chain, HA, DR e production readiness |

## P6 — Workflow distribuído

O P6 adiciona:

- transactional outbox no mesmo commit do estado e da timeline;
- publisher separado com claim, retry e recuperação de locks;
- Redpanda compatível com Kafka;
- consumo at least once com inbox idempotente;
- worker de workflow e projeção;
- timers duráveis;
- retry exponencial e dead letter durável;
- tópico de DLQ;
- replay com novo `eventId`, `replayOf`, justificativa e auditoria;
- policy OPA para inspeção operacional, timers e replay;
- pipeline E2E que comprova expiração por timer e recuperação de evento com falha.

## Executar o runtime mínimo

```bash
docker compose --profile runtime up --build
```

- API: `http://localhost:8080`
- Swagger: `http://localhost:8080/docs`
- OPA: `http://localhost:8181`

## Executar com observabilidade

```bash
OTEL_TRACING_ENABLED=true docker compose --profile observability up --build
```

- API: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin` / `admin`)
- Jaeger: `http://localhost:16686`

## Executar a baseline distribuída

```bash
docker compose --profile distributed up --build
```

- API distribuída: `http://localhost:8081`
- Swagger: `http://localhost:8081/docs`
- Kafka externo: `localhost:19092`
- OPA: `http://localhost:8181`

Executar a prova E2E:

```bash
python scripts/run_p6_distributed_e2e.py
```

Para remover containers e volumes:

```bash
docker compose --profile distributed down -v
```

## Validação completa

```bash
python scripts/validate_structure.py
python scripts/validate_contracts.py
python scripts/validate_observability.py
python scripts/validate_eventing.py
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
mkdocs build --strict
docker compose --profile distributed config
```

## Princípio de leitura

- **atual:** capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em CI ou no ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

O P6 continua sendo uma baseline local. SQLite, Redpanda single-node, replication factor um, identidades por headers e ausência de retenção/ACL corporativa não representam produção.
