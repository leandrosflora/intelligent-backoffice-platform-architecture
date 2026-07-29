# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Vertical Slice](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml)
[![Observability and Evals](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml)
[![Eventing](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml)
[![Production Readiness](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p7-production-readiness.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p7-production-readiness.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para modernizar processos de backoffice regulados, documentais e de longa duração com **workflow persistente, IA com autonomia limitada, human-in-the-loop, policy enforcement, eventing, observabilidade e trilha de auditoria**.

[Documentação](https://leandrosflora.github.io/intelligent-backoffice-platform-architecture/) ·
[Como ler](docs/guide/how-to-read.md) ·
[Walkthrough executável](docs/tutorials/dispute-walkthrough.md) ·
[Estado atual](docs/architecture/implementation-status.md) ·
[ADRs](docs/decisions/index.md)

> **Princípio central:** a IA investiga e recomenda; o workflow controla o processo; policies determinam o que pode ser feito; pessoas aprovam decisões sensíveis; serviços de domínio executam operações nos sistemas de registro.

## O problema

Processos de backoffice costumam atravessar documentos, regras operacionais, múltiplos sistemas, investigação, aprovação por alçada e execução financeira. Quando cada etapa vive em uma ferramenta ou fila diferente, surgem:

- alto tempo de ciclo e retrabalho;
- decisões inconsistentes e pouco explicáveis;
- automações frágeis, sem idempotência ou reconciliação;
- perda de evidências entre etapas;
- risco de um agente executar ações além da sua autoridade.

Esta arquitetura organiza a jornada como um processo **governado, observável, auditável e evolutivo**, sem transferir o controle do negócio para o modelo de IA.

## O que este repositório entrega

| Dimensão | Entrega |
| --- | --- |
| Arquitetura | Contexto de negócio, capacidades, domínios, lifecycle, C4, trust boundaries, sequências e deployments |
| Decisões | ADRs com contexto, trade-offs, alternativas e condições de revisão |
| Contratos | OpenAPI, AsyncAPI, JSON Schemas, eventos e catálogo de policies |
| Baseline executável | Vertical slice FastAPI com persistência, OPA, aprovação humana, execução mock e reconciliação |
| Processamento assíncrono | Outbox, inbox, workers, timers, DLQ, replay e Redpanda |
| Qualidade de IA | Evals versionados com gates de grounding e abstention |
| Operação | OpenTelemetry, Prometheus, Grafana, Jaeger, SLOs, alertas e runbooks |
| Segurança e supply chain | JWT EdDSA local, SBOM, proveniência, backup criptografado e manifests Kubernetes alvo |
| Governança | Vocabulário de maturidade, matriz atual × alvo e production-readiness gates |

## Ecossistema de implementação

A solução está organizada em três repositórios complementares:

| Repositório | Responsabilidade | Tecnologia principal | Estado agregado |
| --- | --- | --- | --- |
| **[intelligent-backoffice-platform-architecture](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture)** | Arquitetura, contratos, policies, baseline, evals e readiness | Python, FastAPI, OPA, Redpanda, OpenTelemetry | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` |
| **[backoffice-platform-api](https://github.com/leandrosflora/backoffice-platform-api)** | Backend de produto, domínio, APIs, workers e operação | .NET 9, PostgreSQL, OPA, Kafka-compatible | `IMPLEMENTATION_STARTED` |
| **[intelligent-backoffice-frontend](https://github.com/leandrosflora/intelligent-backoffice-frontend)** | Console operacional da jornada | React 19, TypeScript, Vite, Nginx | `IMPLEMENTATION_STARTED` |

Backend e frontend já são executáveis isoladamente e a integração entre frontend, API, PostgreSQL e OPA já possui um gate E2E automatizado com navegador real ([`Cross-repository E2E`](https://github.com/leandrosflora/intelligent-backoffice-frontend/actions/workflows/e2e.yml), executado a cada PR do frontend): a jornada principal até `EXECUTED` e o caminho de execução ambígua até a reconciliação são exercitados pela UI real, atravessando o proxy Nginx, a API .NET, o OPA e o PostgreSQL. Essa capacidade específica de integração está `VALIDATED_INTEGRATION`; o ecossistema como um todo permanece `NOT_PRODUCTION_READY` — faltam integrações reais, IAM corporativo, DR e operação 24x7.

Consulte o [mapa dos repositórios](docs/implementation/product-repositories.md) e o [runtime integrado](docs/implementation/product-runtime.md).

## Arquitetura em uma visão

[![C4 — containers atuais](docs/assets/diagrams/c4-container-current.png)](docs/assets/diagrams/c4-container-current.svg)

[Abrir o diagrama em SVG](docs/assets/diagrams/c4-container-current.svg)

Os limites de responsabilidade são intencionais:

1. o **workflow** é a autoridade sobre estado, timers, retries e transições;
2. agentes produzem **análise e recomendação**, não aprovação ou execução;
3. o **OPA** aplica `default deny`, purpose binding, alçada e segregação de funções;
4. mutações sensíveis exigem versão esperada, identidade, correlation ID e idempotency key;
5. resultados ambíguos entram em **reconciliação explícita**;
6. decisões, aprovações, tool calls, eventos e efeitos geram evidências auditáveis.

## Case demonstrado

O primeiro vertical slice implementa uma jornada bancária de contestação:

```text
Abertura
  → validação documental
  → investigação
  → recomendação explicável
  → aprovação humana por alçada
  → execução governada e idempotente
  → reconciliação, auditoria e encerramento
```

O mesmo padrão pode ser aplicado a onboarding, KYC, sinistros, crédito, cadastro, cobrança, compliance e operações documentais.

## Quick start — baseline executável

### Pré-requisitos

- Docker com Compose;
- Python 3.12 ou compatível para o walkthrough e as validações;
- portas `8080`, `8081`, `8181` e `19092` disponíveis, conforme o profile.

### 1. Subir o runtime mínimo

```bash
git clone https://github.com/leandrosflora/intelligent-backoffice-platform-architecture.git
cd intelligent-backoffice-platform-architecture
docker compose --profile runtime up -d --build
curl http://localhost:8080/health
```

A API FastAPI fica em `http://localhost:8080` e sua interface OpenAPI em `http://localhost:8080/docs`.

Para encerrar:

```bash
docker compose --profile runtime down -v
```

### 2. Executar a jornada distribuída

```bash
docker compose --profile distributed up -d --build
python scripts/run_dispute_walkthrough.py
```

O walkthrough valida:

- jornada principal até `EXECUTED`;
- resultado ambíguo seguido de reconciliação;
- negações de policy e segregação de funções;
- controle otimista e idempotência;
- outbox, publicação, consumo e deduplicação;
- timeline, métricas e evidências.

Artifacts gerados:

```text
artifacts/walkthrough/dispute-walkthrough.jsonl
artifacts/walkthrough/dispute-walkthrough-summary.json
```

Para encerrar:

```bash
docker compose --profile distributed down -v
```

Detalhes e diagnóstico estão no [walkthrough executável](docs/tutorials/dispute-walkthrough.md).

## Executar backend e frontend de produto

Mantenha os repositórios como diretórios irmãos:

```text
workspace/
├── intelligent-backoffice-platform-architecture/
├── backoffice-platform-api/
└── intelligent-backoffice-frontend/
```

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

| Componente | Endereço |
| --- | --- |
| API | `http://localhost:8080` |
| Frontend | `http://localhost:3000` |
| OPA | `http://localhost:8181` |

Profiles adicionais do backend:

| Profile | Objetivo |
| --- | --- |
| `distributed` | Redpanda, outbox, workers, timers, DLQ e replay |
| `observability` | OpenTelemetry, Prometheus, Grafana e Jaeger |
| `secure` | Identidade local com JWT EdDSA |

Veja o [runbook completo](docs/implementation/runbook.md) para portas, verificações de saúde, reset de dados e diagnóstico.

## Estado real da solução

| Capacidade | Estado | Evidência ou limite |
| --- | --- | --- |
| Arquitetura, contratos e policies | `CONTRACT_DEFINED` | Artefatos versionados e validados pelo CI |
| Baseline FastAPI | `DEMONSTRATED_LOCAL` | Runtime e testes com dados e integrações sintéticos |
| Backend .NET | `IMPLEMENTATION_STARTED` | Capacidades isoladas executáveis, sem gate integrado completo |
| Frontend React | `IMPLEMENTATION_STARTED` | Build, testes e integração manual demonstrados |
| E2E cross-repo no navegador | `VALIDATED_INTEGRATION` | [`Cross-repository E2E`](https://github.com/leandrosflora/intelligent-backoffice-frontend/actions/workflows/e2e.yml) verde a cada PR: jornada principal até `EXECUTED` e execução ambígua até reconciliação, pela UI real |
| Produção | **`NOT_PRODUCTION_READY`** | Faltam integrações reais, IAM corporativo, DR, operação 24x7 e aprovação formal |

Os estados significam:

- `TARGET_DEFINED`: responsabilidade ou topologia alvo, sem implementação confirmada;
- `CONTRACT_DEFINED`: contrato versionado, sem integração comprovada;
- `IMPLEMENTATION_STARTED`: código existe, mas os gates ainda são incompletos;
- `DEMONSTRATED_LOCAL`: capacidade executada localmente ou no CI com dependências sintéticas;
- `VALIDATED_INTEGRATION`: componentes de produto validados ponta a ponta;
- `PASSED_PRODUCTION`: operação real formalmente aprovada, com owner e evidências atuais.

O estado canônico e os critérios de promoção estão na [matriz atual × alvo](docs/architecture/implementation-status.md).

## Como navegar

| Se você é... | Comece por |
| --- | --- |
| Executivo ou gestor | [Contexto de negócio](docs/context/business-context.md), [outcome card](docs/functional/outcome-card.md) e [production readiness](docs/governance/production-readiness.md) |
| Arquiteto | [Estado de implementação](docs/architecture/implementation-status.md), [arquitetura técnica](docs/architecture/index.md) e [ADRs](docs/decisions/index.md) |
| Desenvolvedor | [Walkthrough](docs/tutorials/dispute-walkthrough.md), [contratos](docs/contracts/index.md) e [runbook](docs/implementation/runbook.md) |
| Segurança | [Trust boundaries](docs/architecture/trust-boundaries.md), [policies](docs/contracts/policies.md) e [supply chain](docs/security/supply-chain.md) |
| SRE ou operações | [Observabilidade](docs/operations/observability.md), [SLOs](docs/operations/slos.md) e [runbooks](docs/operations/index.md) |
| Auditoria ou compliance | [Lifecycle](docs/functional/case-lifecycle.md), [papéis](docs/functional/roles-and-responsibilities.md) e [rastreabilidade](docs/functional/traceability-matrix.md) |

## Validação

Principais gates locais:

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

Os workflows do GitHub Actions executam os gates de qualidade, vertical slice, evals, observabilidade, eventing, production readiness e publicação da documentação.

## Próximo marco

A integração do produto já está comprovada nos pontos que motivaram esta seção:

1. ✅ frontend, API, PostgreSQL e OPA sobem por um único comando (`docker compose -f e2e/docker-compose.yml up`), documentado no [README do frontend](https://github.com/leandrosflora/intelligent-backoffice-frontend#e2e-cross-repo);
2. ✅ a jornada principal até `EXECUTED` e a reconciliação são executadas no navegador real, automatizadas no workflow [`Cross-repository E2E`](https://github.com/leandrosflora/intelligent-backoffice-frontend/actions/workflows/e2e.yml);
3. parcial — negações de policy, versionamento otimista e idempotência foram validadas manualmente (mudança `validate-frontend-backend-integration`) e são cobertas pelos testes de integração do backend, mas ainda não têm um cenário equivalente automatizado no navegador;
4. ✅ a OpenAPI implementada é comparada com os contratos arquiteturais em CI (`Backoffice.Contracts.Tests`, backend);
5. parcial — o correlation ID já atravessa frontend e API (`X-Correlation-Id`) e o backend já instrumenta OpenTelemetry (API e workers), mas a propagação ainda não foi observada ponta a ponta dentro do próprio ambiente de E2E (o coletor OTel não está conectado a essa stack);
6. parcial — o relatório do Playwright é publicado como artifact do GitHub Actions em toda execução (já vinculado a commit/run), mas ainda não existe um resumo único e legível equivalente ao `run_dispute_walkthrough.py` da baseline.

Os itens 3, 5 e 6 são o próximo trabalho relevante — não mais adicionar diagramas nem reconstruir o que já existe.

Consulte o [roadmap](docs/roadmap.md) e os [production-readiness gates](docs/governance/production-readiness.md).
