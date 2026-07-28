# Repositórios de implementação do produto

A plataforma é evoluída em três repositórios complementares. Este repositório permanece como fonte de arquitetura, contratos, policies e evidências; backend e frontend materializam o produto.

## Visão do ecossistema

| Repositório | Responsabilidade | Estado agregado |
|---|---|---|
| [intelligent-backoffice-platform-architecture](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture) | Arquitetura, ADRs, contratos, policies, diagramas, baseline FastAPI, evals e readiness | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` |
| [backoffice-platform-api](https://github.com/leandrosflora/backoffice-platform-api) | Backend .NET 9, PostgreSQL, OPA, JWT, eventing, workers, telemetria e deployment | `IMPLEMENTATION_STARTED` |
| [intelligent-backoffice-frontend](https://github.com/leandrosflora/intelligent-backoffice-frontend) | Console React para operar e testar a jornada do backend | `IMPLEMENTATION_STARTED` |

O estado agregado dos repositórios de produto permanece `IMPLEMENTATION_STARTED` porque ainda não há gate E2E cross-repo. Isso não impede que capacidades isoladas estejam `DEMONSTRATED_LOCAL`.

## Backend de produto

O `backoffice-platform-api` implementa um monólito modular em .NET 9.

### Capacidades materializadas

- casos, documentos, evidências, investigação e recomendação;
- aprovação humana com alçada e segregação de funções;
- execução idempotente, consulta e reconciliação;
- versionamento otimista com `If-Match`;
- persistência PostgreSQL e migrations EF Core;
- OPA externo com default deny, tenant, papéis e purpose binding;
- identidade por headers ou JWT EdDSA;
- outbox, inbox, Redpanda, workers, timers, DLQ e replay;
- endpoints operacionais para outbox, timers e dead letters;
- OpenTelemetry, métricas Prometheus, health e readiness;
- profiles Docker `runtime`, `distributed`, `observability` e `secure`;
- manifests Kubernetes com HPA, PDB e NetworkPolicies;
- testes de domínio, API, contratos, OPA e eventing;
- harness determinístico de evals.

[**Abrir a implementação detalhada do backend**](backend-product.md)

### Limites

- execução permanece mock;
- documentos usam metadados e referências sintéticas;
- sem integração corporativa ou efeito financeiro real;
- sem IAM corporativo, KMS ou mTLS;
- o empacotamento ainda reutiliza policies e observabilidade deste repositório por filesystem;
- sem E2E automatizado com o frontend.

## Frontend de produto

O `intelligent-backoffice-frontend` implementa um console operacional em React 19 e Vite.

### Capacidades materializadas

- criação, listagem, consulta e cancelamento de casos;
- jornada guiada pelo estado do backend;
- registro documental sintético e consulta de evidências;
- investigação, recomendação e aprovação;
- execução com sucesso, falha ou resultado ambíguo;
- reconciliação, consulta de execuções e timeline;
- modo guiado e modo manual de identidades;
- envio de tenant, papéis, alçada, correlation ID, `If-Match` e `Idempotency-Key`;
- console de chamadas HTTP, latência e Problem Details;
- Vite em desenvolvimento e Nginx em produção local;
- lint, testes unitários, build Vite, Compose e imagem Docker no pipeline.

[**Abrir a implementação detalhada do frontend**](frontend-console.md)

### Limites

- sem autenticação OIDC/JWT no navegador;
- documentos sem upload binário;
- IDs de recomendação e aprovação mantidos no `localStorage`;
- sem telemetria distribuída iniciada no browser;
- sem E2E automatizado cross-repo.

## Topologia local

```text
Navegador
   |
   v
React SPA / Vite ou Nginx
   |
   v
Backoffice Platform API (.NET 9)
   |             |                  |
   v             v                  v
PostgreSQL 16    OPA / Rego         Redpanda
                                       |
                                       v
                              Workers de eventing

API e workers → OTel Collector → Prometheus / Grafana / Jaeger
```

[**Abrir o runtime integrado do produto**](product-runtime.md)

## Estado de integração

| Gate | Estado |
|---|---|
| Contratos arquiteturais versionados | `CONTRACT_DEFINED` |
| Baseline executável deste repositório | `DEMONSTRATED_LOCAL` |
| Backend síncrono com PostgreSQL e OPA | `DEMONSTRATED_LOCAL` |
| Backend distribuído com broker e workers | `DEMONSTRATED_LOCAL` |
| Backend com observabilidade | `DEMONSTRATED_LOCAL` |
| Backend com JWT EdDSA local | `DEMONSTRATED_LOCAL` |
| Frontend isolado, build e testes | `DEMONSTRATED_LOCAL` |
| Frontend consumindo backend localmente | `DEMONSTRATED_LOCAL` manual |
| E2E browser-based cross-repo automatizado | Pendente |
| Integrações corporativas reais | Pendente |
| Production readiness | `NOT_PRODUCTION_READY` |

## Próximos gates

1. criar pipeline E2E para frontend, API, PostgreSQL e OPA;
2. publicar o OpenAPI gerado pelo backend e validar compatibilidade;
3. adicionar recuperação de recomendações e aprovações por caso;
4. desacoplar policies e configurações de observabilidade do checkout irmão;
5. incorporar upload documental e object storage reais;
6. integrar IAM corporativo e workload identity;
7. comprovar carga, backup, restore, DR e operação.

!!! warning "Classificação correta"
    Código executável e profiles locais comprovam implementação e demonstração controlada. Não comprovam escala, integração corporativa ou prontidão produtiva.
