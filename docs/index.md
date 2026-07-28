# Intelligent Backoffice Platform Architecture

Arquitetura de referência executável para processos de backoffice regulados, documentais e de longa duração. A solução combina workflow persistente, capacidades inteligentes, aprovação humana, policies, evidências e execução governada sem transferir decisões sensíveis para agentes.

[![Contexto atual do ecossistema](assets/diagrams/c4-context-current.png)](assets/diagrams/c4-context-current.svg)

[**Abrir diagrama de contexto atual em SVG**](assets/diagrams/c4-context-current.svg)

## Ecossistema atual

| Trilha | Repositório | Estado agregado | Implementação atual |
|---|---|---|---|
| Arquitetura e baseline | `intelligent-backoffice-platform-architecture` | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` | FastAPI, contracts-as-code, OPA, eventing, observabilidade, evals e readiness |
| Backend de produto | `backoffice-platform-api` | `IMPLEMENTATION_STARTED` | .NET 9, PostgreSQL, OPA, JWT, workers, Redpanda, telemetria e Kubernetes |
| Frontend de produto | `intelligent-backoffice-frontend` | `IMPLEMENTATION_STARTED` | React 19, jornada operacional, modos de identidade, testes e Nginx |

O backend e o frontend já são componentes executáveis. A integração conjunta ainda precisa de um gate E2E browser-based cross-repo para avançar a `VALIDATED_INTEGRATION`.

- [Mapa dos repositórios](implementation/product-repositories.md)
- [Backend de produto](implementation/backend-product.md)
- [Frontend operacional](implementation/frontend-console.md)
- [Runtime integrado](implementation/product-runtime.md)

## Problema que a arquitetura resolve

Processos de backoffice atravessam documentos, múltiplos sistemas, regras operacionais, investigação, aprovação por alçada e execução financeira. Quando essas etapas ficam fragmentadas, aumentam tempo de ciclo, retrabalho, inconsistência e risco de perda de evidências.

A plataforma organiza a jornada como um processo governado, observável e auditável.

## Princípios arquiteturais

1. **O workflow controla o processo.** Estado, timers, retries, compensações e transições não pertencem ao agente.
2. **A IA investiga e recomenda.** Agentes não aprovam nem executam operações mutáveis.
3. **Policies falham fechadas.** Alçada, segregação, finalidade e autorização são verificadas antes da ação.
4. **Toda decisão produz evidência.** Eventos, versões, tool calls, aprovações e resultados permanecem rastreáveis.
5. **Baseline e produto são separados.** A baseline demonstra padrões; os repositórios de produto materializam a evolução.

Os trade-offs estão registrados nos [Architecture Decision Records](decisions/index.md).

## O que funciona na baseline

| Capacidade | Baseline executável | Limite declarado |
|---|---|---|
| Jornada de contestação | FastAPI com lifecycle persistido e walkthrough automatizado | Dados e integrações sintéticos |
| Aprovação e execução | Aprovação humana, OPA, execução mock idempotente e reconciliação | Sem efeito financeiro real |
| Processamento assíncrono | Outbox, inbox, workers, timers, DLQ e replay | SQLite e broker single-node |
| Observabilidade | Métricas, traces, dashboards, SLOs e alertas | Ambiente local sem operação 24x7 |
| Identidade e supply chain | JWT EdDSA local, SBOM e proveniência | Sem IAM, KMS e admission corporativos |
| Resiliência | Backup criptografado, restore e critérios de DR | Sem exercício regional real |

## O que já existe no produto

| Componente | Implementação |
|---|---|
| Backend .NET | Casos, documentos, investigação, recomendação, aprovação, execução, reconciliação, PostgreSQL e OPA |
| Identidade | Headers para desenvolvimento e JWT EdDSA no profile seguro |
| Eventing | Outbox, Redpanda, workers, timers, DLQ e replay |
| Operações | Endpoints de outbox, timers, dead letters e replay |
| Observabilidade | OpenTelemetry, métricas Prometheus, health, readiness, Grafana e Jaeger |
| Deployment | Docker profiles e manifests Kubernetes com HPA, PDB e NetworkPolicies |
| Frontend React | Jornada guiada, identidades, evidências, execuções, timeline e console HTTP |

!!! danger "Status de produção"
    O estado oficial permanece **`NOT_PRODUCTION_READY`**. Componentes executáveis não equivalem a integração validada ou implantação corporativa aprovada.

## Executar a baseline

```bash
docker compose --profile runtime up --build
```

Walkthrough distribuído:

```bash
docker compose --profile distributed up -d --build
python scripts/run_dispute_walkthrough.py
```

[**Abrir o walkthrough executável**](tutorials/dispute-walkthrough.md)

## Executar o produto

Mantenha os três repositórios como diretórios irmãos.

Backend síncrono:

```bash
cd backoffice-platform-api
docker compose --profile runtime up -d --build
```

Frontend:

```bash
cd intelligent-backoffice-frontend
BACKEND_URL=http://host.docker.internal:8080 docker compose up -d --build
```

A API fica em `http://localhost:8080` e o frontend em `http://localhost:3000`.

[**Abrir o runbook do produto**](implementation/product-runtime.md)

## Como interpretar as visões

| Visão | Pergunta respondida |
|---|---|
| [Repositórios de produto](implementation/product-repositories.md) | Como arquitetura, backend e frontend se relacionam? |
| [Backend de produto](implementation/backend-product.md) | O que foi implementado na API, workers, segurança e operação? |
| [Frontend operacional](implementation/frontend-console.md) | Quais jornadas e controles a interface cobre? |
| [Runtime integrado](implementation/product-runtime.md) | Como executar os componentes e quais profiles existem? |
| [Estado de implementação](architecture/implementation-status.md) | O que está contratado, demonstrado, integrado ou pendente? |
| [Containers atuais](architecture/c4-container-current.md) | Quais containers existem hoje no produto e na baseline? |
| [Production readiness](governance/production-readiness.md) | Quais gates impedem a classificação como produção? |

## Próximos pontos de entrada

- [Como ler esta arquitetura](guide/how-to-read.md)
- [Contexto de negócio](context/business-context.md)
- [Arquitetura funcional](functional/index.md)
- [Arquitetura técnica](architecture/index.md)
- [Decisões arquiteturais](decisions/index.md)
- [Contratos executáveis](contracts/index.md)
- [Implementação](implementation/index.md)
- [Roadmap e histórico](roadmap.md)
