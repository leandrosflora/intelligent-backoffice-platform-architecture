# Backend de produto — `backoffice-platform-api`

O repositório [`backoffice-platform-api`](https://github.com/leandrosflora/backoffice-platform-api) materializa a plataforma como um monólito modular em .NET 9, com persistência PostgreSQL, autorização externa via OPA, identidade em dois modos, eventing, workers e telemetria.

## Classificação atual

| Dimensão | Estado | Leitura correta |
|---|---|---|
| Implementação do componente backend | `IMPLEMENTATION_STARTED` | O código cobre a jornada e controles operacionais relevantes |
| Capacidades executáveis isoladamente | `DEMONSTRATED_LOCAL` | Profiles Docker e testes exercitam API, PostgreSQL, OPA, Kafka e workers com dados sintéticos |
| Integração com o frontend | `IMPLEMENTATION_STARTED` | Existe consumo HTTP documentado, mas não há gate E2E cross-repo automatizado |
| Produção | `NOT_PRODUCTION_READY` | Não há IAM corporativo, sistemas de registro reais, operação 24x7 ou aprovação formal |

## Estrutura da solução

| Projeto | Responsabilidade |
|---|---|
| `Backoffice.Api` | Endpoints HTTP, Problem Details, identidade, health checks e exposição de métricas |
| `Backoffice.Application` | Casos de uso, policy enforcement, auditabilidade, eventing e contratos de aplicação |
| `Backoffice.Domain` | Aggregates, estados, regras, timeline, outbox, timers e dead letters |
| `Backoffice.Infrastructure` | EF Core/PostgreSQL, OPA, JWT EdDSA, Kafka e OpenTelemetry |
| `Backoffice.Workers` | Dispatcher de outbox, consumer de workflow e disparo de timers |
| `Backoffice.Evals` | Harness determinístico de avaliação com thresholds versionados |

## Jornada implementada

O backend implementa a jornada de contestação sem delegar o controle de processo ao agente:

1. criação, listagem, consulta e cancelamento de casos;
2. registro e consulta de documentos e evidências;
3. investigação determinística;
4. recomendação grounded;
5. aprovação humana com alçada e segregação de funções;
6. execução governada e idempotente;
7. tratamento de sucesso, falha ou resultado ambíguo;
8. reconciliação explícita;
9. consulta de execuções e timeline.

As mutações utilizam versionamento otimista por `If-Match`. Operações sensíveis usam `Idempotency-Key`, correlation ID, tenant, identidade, papéis, finalidade e decisão do PDP.

## Policy enforcement

A API consulta um PDP OPA externo por HTTP. O input de autorização inclui:

- sujeito humano ou workload;
- tenant;
- papéis;
- ação;
- tipo e estado do recurso;
- finalidade da operação;
- correlation ID;
- contexto adicional e obrigações.

O modelo mantém `default deny`, least privilege, purpose binding, segregação de funções e alçada. Indisponibilidade ou negação do PDP impede a operação protegida.

## Identidade

O backend possui dois modos configuráveis:

| Modo | Uso | Estado |
|---|---|---|
| `headers` | Desenvolvimento e integração com o console React | Implementado para baseline local |
| `jwt` | Tokens EdDSA assinados, issuer, audience e TTL máximo | Implementado no profile `secure` |

O modo JWT comprova validação criptográfica local. Ele não substitui federação corporativa, rotação, revogação, KMS, mTLS ou workload identity gerenciada.

## Eventing e operação assíncrona

O profile distribuído incorpora:

- outbox persistente;
- publicação Kafka-compatible em Redpanda;
- consumer de workflow;
- timers persistentes;
- dead-letter queue;
- replay governado;
- registro de inbox e auditoria de replay.

A superfície operacional expõe endpoints para:

```text
POST /v1/operations/cases/{caseId}/timers
GET  /v1/operations/outbox
GET  /v1/operations/dead-letters
GET  /v1/operations/timers
POST /v1/operations/dead-letters/{deadLetterId}/replay
```

## Observabilidade

A aplicação possui:

- instrumentação OpenTelemetry;
- métricas HTTP e métricas de domínio;
- gauges de outbox, dead letters e timers;
- endpoint Prometheus;
- liveness em `/health`;
- readiness com verificação do PostgreSQL em `/health/ready`;
- profile com Collector, Prometheus, Grafana e Jaeger.

A telemetria demonstra a instrumentação. Ainda faltam retenção corporativa, dashboards operacionais aprovados, integração frontend-backend, alertas com owner e processo de on-call.

## Profiles Docker Compose

| Profile | Componentes principais | Objetivo |
|---|---|---|
| `runtime` | PostgreSQL, OPA e API | Jornada síncrona governada |
| `distributed` | PostgreSQL, OPA, API, Redpanda e três workers | Eventing, timers, DLQ e replay |
| `observability` | PostgreSQL, OPA, API, OTel Collector, Prometheus, Grafana e Jaeger | Métricas, traces e dashboards |
| `secure` | PostgreSQL, OPA e API em modo JWT EdDSA | Identidade assinada local |

O Compose reutiliza policies e artefatos de observabilidade do repositório de arquitetura, que deve estar disponível como diretório irmão.

## Kubernetes

O repositório já contém uma baseline de deployment com:

- namespace e service account;
- ConfigMap;
- Deployments da API e workers;
- Services;
- liveness e readiness probes;
- HPA;
- PodDisruptionBudget;
- NetworkPolicies;
- Kustomize.

Esses manifests expressam a topologia alvo de plataforma, mas não comprovam cluster real, secrets manager, ingress, persistência gerenciada, autoscaling validado ou operação de produção.

## Qualidade e contratos

O workflow de CI está definido para executar:

```text
restore → build → testes → evals determinísticos → validação Prometheus
```

Os testes incluem integração HTTP, domínio, contratos, autorização com OPA real e eventing com broker Kafka-compatible. Há testes para OpenAPI, AsyncAPI e JSON Schemas.

!!! note "Evidência de CI"
    A existência do workflow e dos testes é evidência de automação implementada. A promoção de estado deve usar runs verdes associados ao commit ou release avaliado.

## Limites atuais

- gateway de execução permanece mock;
- documentos são metadados e storage references sintéticos;
- não há integração financeira ou sistema de registro real;
- não há IAM corporativo, KMS ou mTLS;
- o frontend não está incluído no mesmo gate E2E;
- policies e observabilidade ainda são montadas a partir do repositório de arquitetura;
- não há evidência de carga, chaos, DR regional ou operação 24x7.

## Próximos gates

1. criar E2E automatizado com frontend, API, PostgreSQL e OPA;
2. publicar e comparar o OpenAPI do backend com os contratos arquiteturais;
3. eliminar dependências de filesystem entre repositórios no empacotamento;
4. integrar object storage, malware scanning e upload documental real;
5. substituir o gateway mock por adapters governados;
6. incorporar IAM corporativo e workload identity;
7. comprovar observabilidade, capacidade, backup, restore e DR em ambiente controlado.
