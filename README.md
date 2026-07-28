# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Vertical Slice](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml)
[![Observability and Evals](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml)
[![Eventing](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml)
[![Production Readiness](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p7-production-readiness.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p7-production-readiness.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para automação inteligente de backoffice com agentes, processamento documental, workflows persistentes, human-in-the-loop, policies, auditoria e integração governada com sistemas corporativos.

## Princípio central

> A IA produz análise e recomendação. O workflow controla o processo. Policies determinam o que pode ser feito. Pessoas aprovam decisões sensíveis. Serviços de domínio executam operações em sistemas de registro.

As decisões e trade-offs estão registrados nos [Architecture Decision Records](docs/decisions/index.md).

## Ecossistema de implementação

| Repositório | Papel | Estado agregado |
|---|---|---|
| [intelligent-backoffice-platform-architecture](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture) | Arquitetura, contratos, policies, baseline FastAPI, evals e readiness | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` |
| [backoffice-platform-api](https://github.com/leandrosflora/backoffice-platform-api) | Backend .NET 9, PostgreSQL, OPA, JWT, eventing, workers e observabilidade | `IMPLEMENTATION_STARTED` |
| [intelligent-backoffice-frontend](https://github.com/leandrosflora/intelligent-backoffice-frontend) | Console React para operar e testar a API | `IMPLEMENTATION_STARTED` |

Backend e frontend já são componentes executáveis. A integração conjunta permanece sem gate E2E browser-based cross-repo, portanto o ecossistema ainda não é `VALIDATED_INTEGRATION`.

- [Mapa dos repositórios](docs/implementation/product-repositories.md)
- [Backend de produto](docs/implementation/backend-product.md)
- [Frontend operacional](docs/implementation/frontend-console.md)
- [Runtime integrado](docs/implementation/product-runtime.md)

## Case aplicado

O primeiro case demonstra uma jornada bancária de contestação:

1. abertura e triagem;
2. recebimento e validação documental;
3. investigação;
4. recomendação explicável;
5. aprovação humana conforme alçada;
6. execução governada e idempotente;
7. reconciliação, auditoria e encerramento.

## Baseline arquitetural

Este repositório demonstra:

- vertical slice FastAPI com lifecycle persistido;
- OPA em runtime com `default deny`, alçada e purpose binding;
- aprovação humana, execução mock idempotente e reconciliação;
- OpenAPI, AsyncAPI, JSON Schemas e catálogo de policies;
- outbox, inbox, workers, timers, DLQ e replay;
- evals versionados com gates de abstention e grounding;
- métricas, traces, dashboards, SLOs, alertas e runbooks;
- JWT EdDSA local para identidade humana e de workload;
- backup criptografado, restore, SBOM e proveniência;
- manifests Kubernetes alvo com HA e controles de rede;
- matriz explícita de production readiness;
- ADRs versionados e validados pelo CI;
- walkthrough end-to-end com artifacts JSONL e JSON.

## Backend de produto implementado

O `backoffice-platform-api` já possui:

- monólito modular ASP.NET Core / .NET 9;
- casos, documentos, evidências, investigação e recomendação;
- aprovação humana, execução idempotente e reconciliação;
- PostgreSQL com migrations EF Core;
- OPA externo e policy enforcement fail-closed;
- identidade por headers ou JWT EdDSA;
- outbox, Redpanda, workers, timers, DLQ e replay;
- endpoints operacionais;
- OpenTelemetry, Prometheus, Grafana e Jaeger;
- health e readiness;
- profiles Docker `runtime`, `distributed`, `observability` e `secure`;
- manifests Kubernetes com HPA, PDB e NetworkPolicies;
- testes de API, domínio, contratos, OPA, Kafka e evals.

## Frontend de produto implementado

O `intelligent-backoffice-frontend` já possui:

- jornada guiada pelo estado retornado pela API;
- criação, listagem e consulta de casos;
- documentos, evidências, investigação e recomendação;
- aprovação humana, execução e reconciliação;
- modos guiado e manual de identidade;
- tratamento de Problem Details, correlation ID e conflito de versão;
- console HTTP local;
- Vite para desenvolvimento e Nginx para empacotamento;
- lint, testes, build e imagem Docker.

## Arquitetura atual

[![C4 containers atuais](docs/assets/diagrams/c4-container-current.png)](docs/assets/diagrams/c4-container-current.svg)

A documentação distingue:

- `CONTRACT_DEFINED` — contrato versionado;
- `IMPLEMENTATION_STARTED` — código existente sem todos os gates;
- `DEMONSTRATED_LOCAL` — capacidade executada localmente ou no CI com dependências sintéticas;
- `VALIDATED_INTEGRATION` — componentes de produto validados ponta a ponta;
- `PASSED_PRODUCTION` — operação produtiva aprovada.

Consulte a [matriz atual × alvo](docs/architecture/implementation-status.md).

## Executar a baseline

Runtime mínimo:

```bash
docker compose --profile runtime up --build
```

Workflow distribuído e walkthrough:

```bash
docker compose --profile distributed up -d --build
python scripts/run_dispute_walkthrough.py
```

## Executar o produto

Mantenha os três repositórios como diretórios irmãos.

Backend:

```bash
cd backoffice-platform-api
docker compose --profile runtime up -d --build
```

Frontend:

```bash
cd intelligent-backoffice-frontend
BACKEND_URL=http://host.docker.internal:8080 docker compose up -d --build
```

A API fica em `http://localhost:8080`; o frontend em `http://localhost:3000`.

Para eventing:

```bash
cd backoffice-platform-api
docker compose --profile distributed up -d --build
```

Para observabilidade:

```bash
cd backoffice-platform-api
docker compose --profile observability up -d --build
```

Consulte o [runbook do runtime integrado](docs/implementation/product-runtime.md).

## Documentação

- [Documentação publicada](https://leandrosflora.github.io/intelligent-backoffice-platform-architecture/)
- [Repositórios de produto](docs/implementation/product-repositories.md)
- [Backend de produto](docs/implementation/backend-product.md)
- [Frontend operacional](docs/implementation/frontend-console.md)
- [Runtime integrado](docs/implementation/product-runtime.md)
- [Walkthrough executável](docs/tutorials/dispute-walkthrough.md)
- [Estado de implementação](docs/architecture/implementation-status.md)
- [Arquitetura técnica](docs/architecture/index.md)
- [Architecture Decision Records](docs/decisions/index.md)
- [Contratos executáveis](docs/contracts/index.md)
- [Production readiness](docs/governance/production-readiness.md)

## Production readiness

O status oficial permanece **`NOT_PRODUCTION_READY`**. Código e profiles locais não substituem integração E2E, identidade corporativa, sistemas de registro, observabilidade operacional, DR real e operação 24x7.

## Validação completa

```bash
python scripts/validate_structure.py
python scripts/validate_adrs.py
python scripts/validate_contracts.py
python scripts/validate_observability.py
python scripts/validate_eventing.py
python scripts/validate_p7.py
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
mkdocs build --strict
docker compose --profile secure config
```
