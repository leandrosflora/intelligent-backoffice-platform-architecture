# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Vertical Slice](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml)
[![P5 Observability and Evals](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml)
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
| P5 | Baseline executável | Evals, OpenTelemetry, Prometheus, Grafana, Jaeger, SLOs, alertas e runbooks |
| P6 | Planejado | Event backbone, outbox, workers e workflows distribuídos |

## P5 — Evals e operação

O P5 adiciona:

- métricas Prometheus de HTTP, policy, workflow, execução, idempotência e inteligência;
- spans OpenTelemetry para requests, decisões de policy e operações de domínio;
- OpenTelemetry Collector e Jaeger;
- Prometheus com recording rules e alertas;
- dashboard Grafana provisionado;
- cinco SLOs iniciais com owner e runbook;
- dataset sintético com 14 casos de eval;
- gates de groundedness e abstention;
- pipeline E2E que comprova métricas e traces.

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

Para remover containers e volumes:

```bash
docker compose --profile observability down -v
```

## Executar evals

```bash
cd samples/vertical-slice
python -m pip install -r requirements-dev.txt
cd ../..
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
```

## Validação completa

```bash
python scripts/validate_structure.py
python scripts/validate_contracts.py
python scripts/validate_observability.py
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
mkdocs build --strict
docker compose --profile observability config
```

## Princípio de leitura

- **atual:** capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em CI ou no ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

O P5 continua sendo uma baseline local. Não utiliza dados reais, OCR real, LLM real, integração bancária produtiva, retenção corporativa de telemetria ou operação 24x7.
