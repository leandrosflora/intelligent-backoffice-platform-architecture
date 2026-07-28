# Implementação

A plataforma possui três artefatos complementares:

1. a **baseline arquitetural executável** deste repositório;
2. o **backend de produto** em .NET 9;
3. o **frontend operacional** em React 19.

[**Abrir o mapa dos repositórios de produto**](product-repositories.md)

## Estado resumido

| Trilha | Estado agregado | Capacidades já demonstradas |
|---|---|---|
| Arquitetura e baseline | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` | Contratos, policies, FastAPI, eventing, observabilidade, evals e readiness |
| Backend de produto | `IMPLEMENTATION_STARTED` | Jornada .NET, PostgreSQL, OPA, JWT EdDSA, eventing, workers, métricas e profiles Docker |
| Frontend de produto | `IMPLEMENTATION_STARTED` | Jornada React, modos de identidade, diagnóstico HTTP, build, testes e imagem Nginx |
| Integração cross-repo | Pendente | Execução manual é possível, mas não existe gate E2E automatizado |

!!! danger "Status de produção"
    O status oficial permanece **`NOT_PRODUCTION_READY`**. A existência de componentes executáveis não comprova integração corporativa, operação 24x7 ou aprovação para produção.

## Implementação de referência

Este repositório contém um vertical slice FastAPI que demonstra a jornada principal e os controles arquiteturais com dados sintéticos e integrações mock.

### Escopo demonstrado

- Case API e workflow persistido;
- document intelligence e investigação sintéticas;
- recomendação e abstention;
- aprovação humana;
- execução governada mock e reconciliação;
- OPA em runtime;
- idempotência e versionamento otimista;
- timeline auditável;
- outbox, inbox, workers, timers, DLQ e replay;
- OpenTelemetry, Prometheus, Grafana e Jaeger;
- JWT EdDSA local;
- evals, backup, restore, SBOM e proveniência.

A baseline continua sendo a fonte de contratos, policies, decisões e critérios de readiness.

## Backend de produto

O [`backoffice-platform-api`](backend-product.md) absorveu uma parte relevante da baseline:

- monólito modular .NET 9;
- EF Core e PostgreSQL;
- enforcement por OPA externo;
- identidade por headers ou JWT EdDSA;
- outbox, Redpanda, workers, timers, DLQ e replay;
- endpoints operacionais;
- métricas, traces, health e readiness;
- manifests Kubernetes;
- testes de domínio, API, contratos, OPA e eventing;
- harness determinístico de evals.

O gateway de execução e o armazenamento documental ainda são mocks de desenvolvimento.

[**Abrir a implementação do backend**](backend-product.md)

## Frontend de produto

O [`intelligent-backoffice-frontend`](frontend-console.md) oferece:

- jornada guiada pelo estado da API;
- criação e consulta de casos;
- documentos, evidências, investigação e recomendação;
- aprovação, execução e reconciliação;
- identidades guiadas ou manuais;
- tratamento de Problem Details, correlation ID e conflito de versão;
- Vite para desenvolvimento e Nginx para empacotamento;
- lint, testes, build e imagem Docker.

[**Abrir a implementação do frontend**](frontend-console.md)

## Runtime local do produto

O backend já possui profiles `runtime`, `distributed`, `observability` e `secure`. O frontend é iniciado em Compose separado e aponta `/api` para a porta publicada pela API.

[**Abrir o runtime integrado**](product-runtime.md)

## Próximo gate

A integração avança para `VALIDATED_INTEGRATION` somente quando um pipeline reproduzível:

1. sobe frontend, API, PostgreSQL e OPA;
2. executa a jornada principal no navegador;
3. valida negações de policy e concorrência;
4. cobre resultado ambíguo e reconciliação;
5. coleta métricas, traces e artifacts;
6. vincula as evidências ao commit avaliado.
