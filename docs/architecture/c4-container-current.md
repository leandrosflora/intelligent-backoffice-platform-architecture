# C4 — Containers atuais

O nível de containers atual separa:

1. a **implementação de produto**, formada pelo frontend React, backend .NET e seus serviços de suporte;
2. a **baseline executável de arquitetura**, mantida neste repositório para demonstrar padrões, contratos e controles.

[![C4 containers atuais](../assets/diagrams/c4-container-current.png)](../assets/diagrams/c4-container-current.svg)

[**Abrir diagrama em SVG**](../assets/diagrams/c4-container-current.svg)

## Implementação atual do produto

| Container | Tecnologia | Responsabilidade | Estado |
|---|---|---|---|
| Intelligent Backoffice Frontend | React 19 / Vite | Jornada de casos, documentos, evidências, investigação, aprovação, execução e reconciliação | `DEMONSTRATED_LOCAL` como componente |
| Frontend Reverse Proxy | Nginx | Serve a SPA e encaminha `/api` ao backend | `DEMONSTRATED_LOCAL` como componente |
| Backoffice Platform API | .NET 9 / ASP.NET Core | Lifecycle, policies, identidade, versionamento, execução, reconciliação e endpoints operacionais | `DEMONSTRATED_LOCAL` em profiles locais |
| Backoffice Database | PostgreSQL 16 | Persistência de agregados, auditoria, outbox, inbox, timers e dead letters | `DEMONSTRATED_LOCAL` |
| Policy Decision Point | OPA / Rego | Default deny, tenant, papéis, purpose, alçada, segregação e obrigações | `DEMONSTRATED_LOCAL` |
| Product Event Backbone | Redpanda / Kafka API | Transporte dos eventos da outbox e da DLQ | `DEMONSTRATED_LOCAL` no profile distribuído |
| Outbox Dispatcher | .NET Worker | Publica eventos persistidos no broker | `DEMONSTRATED_LOCAL` |
| Workflow Consumer | .NET Worker | Consome eventos, aplica inbox/idempotência e avança o workflow | `DEMONSTRATED_LOCAL` |
| Timer Worker | .NET Worker | Dispara timers persistentes e publica eventos | `DEMONSTRATED_LOCAL` |
| Product Observability Stack | OTel / Prometheus / Grafana / Jaeger | Métricas e traces da API e dos workers | `DEMONSTRATED_LOCAL` no profile observável |

### Fluxo atual

- o navegador executa a SPA React;
- Vite ou Nginx encaminha `/api` para a API .NET;
- a API persiste estado no PostgreSQL;
- operações governadas consultam o OPA por HTTP;
- a mesma transação de negócio grava outbox e timers;
- workers publicam e consomem eventos por Redpanda;
- falhas podem ser encaminhadas para DLQ e submetidas a replay governado;
- API e workers exportam métricas e traces no profile de observabilidade;
- o gateway de execução e o armazenamento documental permanecem mocks.

## Profiles do backend

| Profile | Topologia |
|---|---|
| `runtime` | PostgreSQL + OPA + API |
| `distributed` | PostgreSQL + OPA + API + Redpanda + workers |
| `observability` | PostgreSQL + OPA + API + Collector + Prometheus + Grafana + Jaeger |
| `secure` | PostgreSQL + OPA + API com JWT EdDSA |

O frontend é executado por Compose separado e aponta para a porta publicada pela API.

## Baseline executável de arquitetura

| Container | Responsabilidade |
|---|---|
| Reference Runtime | Profiles FastAPI para runtime, identidade assinada, eventing e observabilidade |
| Reference State Stores | SQLite para estado, outbox, inbox, timers e dead letters |
| Reference Event Backbone | Redpanda single-node para demonstração de eventos |
| Reference Observability Stack | OpenTelemetry, Prometheus, Grafana e Jaeger |
| Architecture Evidence Toolchain | E2E, evals, contratos, policies, diagramas, backup, SBOM, proveniência e readiness |

A baseline permanece `DEMONSTRATED_LOCAL`. Ela não é uma dependência de runtime da API .NET, embora o Compose do backend ainda reutilize policies e arquivos de observabilidade deste repositório.

## Gaps de integração

- não existe Compose único para frontend e backend;
- não existe E2E browser-based cross-repo automatizado;
- recomendações e aprovações ainda não possuem recuperação por caso;
- identidade corporativa e sessão web ainda não foram incorporadas;
- execução e documentos ainda usam integrações mock;
- telemetria não começa no navegador;
- não há carga, DR ou operação multi-instância comprovados.

!!! warning "Limite arquitetural"
    Componentes `DEMONSTRATED_LOCAL` não equivalem a uma integração `VALIDATED_INTEGRATION`. A promoção exige execução conjunta, contratos compatíveis, evidências reproduzíveis e critérios operacionais aprovados.

Consulte:

- [backend de produto](../implementation/backend-product.md);
- [frontend operacional](../implementation/frontend-console.md);
- [runtime integrado](../implementation/product-runtime.md);
- [matriz de implementação atual × alvo](implementation-status.md).

**Fonte PlantUML:** `C4/c4-container-current.puml`.
