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

As decisões e trade-offs que sustentam esse princípio estão registrados nos [Architecture Decision Records](docs/decisions/index.md).

## Ecossistema de implementação

A solução começa a sair da baseline arquitetural e a se materializar em repositórios de produto separados.

| Repositório | Papel | Estado |
|---|---|---|
| [intelligent-backoffice-platform-architecture](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture) | Arquitetura, contratos, policies, baseline FastAPI, evals e readiness | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` |
| [backoffice-platform-api](https://github.com/leandrosflora/backoffice-platform-api) | Backend de produto em .NET 9, PostgreSQL e OPA | `IMPLEMENTATION_STARTED` |
| [intelligent-backoffice-frontend](https://github.com/leandrosflora/intelligent-backoffice-frontend) | Console React para consumir e testar a API | `IMPLEMENTATION_STARTED` |

Frontend e backend possuem código inicial, mas ainda não existe gate E2E cross-repo automatizado. O estado de integração de produto ainda não é `VALIDATED_INTEGRATION`.

[**Abrir o mapa dos repositórios de produto**](docs/implementation/product-repositories.md)

## Case aplicado

O primeiro case demonstra uma jornada bancária de contestação:

1. abertura e triagem;
2. recebimento e validação documental;
3. investigação;
4. recomendação explicável;
5. aprovação humana conforme alçada;
6. execução governada e idempotente;
7. reconciliação, auditoria e encerramento.

## O que a baseline demonstra

- vertical slice FastAPI com lifecycle persistido;
- OPA em runtime com `default deny`, alçada e purpose binding;
- aprovação humana, execução mock idempotente e reconciliação rastreável;
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

## O que começou a ser implementado no produto

- backend ASP.NET Core com casos, documentos, evidências, investigação, recomendação, aprovação, execução e reconciliação;
- persistência PostgreSQL e enforcement por OPA externo;
- frontend React com jornada guiada, identidades da baseline, timeline, evidências e console HTTP;
- reverse proxy Nginx e pipeline de qualidade do frontend.

## Arquitetura atual

[![C4 contexto atual](docs/assets/diagrams/c4-context-current.png)](docs/assets/diagrams/c4-context-current.svg)

A documentação separa cinco conceitos:

- **contrato definido:** API, evento, schema ou policy versionada;
- **implementação iniciada:** código existe em um repositório de produto, sem E2E integrado comprovado;
- **baseline demonstrada:** controle executado localmente ou no CI;
- **integração validada:** componentes de produto executados ponta a ponta com evidência;
- **produção:** integração real, operação e governança aprovadas.

Consulte a [matriz atual × alvo](docs/architecture/implementation-status.md) para os gaps de cada capacidade.

## Executar a baseline deste repositório

Runtime mínimo:

```bash
docker compose --profile runtime up --build
```

Observabilidade:

```bash
OTEL_TRACING_ENABLED=true docker compose --profile observability up --build
```

Workflow distribuído e walkthrough completo:

```bash
docker compose --profile distributed up -d --build
python scripts/run_dispute_walkthrough.py
```

Profile com identidade assinada:

```bash
python scripts/generate_dev_identity.py --force
docker compose --profile secure up --build
python scripts/run_p7_secure_e2e.py
```

## Executar os repositórios de produto

Backend:

```bash
cd backoffice-platform-api
docker compose --profile runtime up -d postgres
dotnet run --project src/Backoffice.Api
```

Frontend:

```bash
cd intelligent-backoffice-frontend/intelligent-backoffice-frontend
npm ci
npm run dev
```

A API utiliza `http://localhost:5260`; o frontend de desenvolvimento utiliza `http://localhost:5173`. Operações governadas dependem de um PDP OPA compatível.

## Documentação

- [Documentação publicada](https://leandrosflora.github.io/intelligent-backoffice-platform-architecture/)
- [Mapa dos repositórios de produto](docs/implementation/product-repositories.md)
- [Walkthrough executável](docs/tutorials/dispute-walkthrough.md)
- [Como ler esta arquitetura](docs/guide/how-to-read.md)
- [Contexto de negócio](docs/context/business-context.md)
- [Estado de implementação](docs/architecture/implementation-status.md)
- [Arquitetura técnica](docs/architecture/index.md)
- [Architecture Decision Records](docs/decisions/index.md)
- [Contratos executáveis](docs/contracts/index.md)
- [Implementação de referência](docs/implementation/index.md)
- [Production readiness](docs/governance/production-readiness.md)
- [Roadmap e histórico](docs/roadmap.md)

## Production readiness

O status oficial permanece **`NOT_PRODUCTION_READY`**. Código em frontend e backend não substitui integração E2E, identidade corporativa, sistemas de registro, observabilidade operacional, DR real e operação 24x7.

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
