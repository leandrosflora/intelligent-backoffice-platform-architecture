# P4 — Vertical slice executável

O P4 transforma os contratos e policies do P3 em uma baseline executável local.

!!! warning "Baseline de referência"
    O vertical slice usa dados sintéticos, JWT local, mocks e execução sem efeito
    financeiro. Ele demonstra controles arquiteturais; não representa prontidão
    para produção bancária.

## Arquitetura implementada

```text
Cliente E2E
   │ JWT + tenant + correlação + idempotência + If-Match
   ▼
ASP.NET Core API — modular monolith
   ├── Case Management
   ├── Workflow Orchestrator
   ├── Document Intelligence Mock
   ├── Investigation / Recommendation Mock
   ├── Human Approval
   └── Governed Execution Mock
        │
        ├── PostgreSQL
        │    ├── aggregate do caso
        │    ├── idempotência
        │    ├── timeline
        │    └── outbox
        │
        └── OPA Policy Decision Point
```

## Jornada demonstrada

1. `POST /v1/cases`;
2. registro de documento em quarentena sintética;
3. validação determinística e criação de evidência;
4. investigação mock;
5. recomendação explicável;
6. aprovação humana conforme alçada;
7. execução mock com idempotência;
8. leitura auditável da timeline.

## Controles executáveis

| Controle | Evidência no P4 |
|---|---|
| Tenant isolation | token, header e lookup particionado por tenant |
| Default deny | todas as operações protegidas consultam OPA |
| Fail-closed | indisponibilidade ou resposta inválida do PDP resulta em negação |
| Segregação | recomendador e aprovador devem ser atores diferentes |
| Alçada | OPA compara `authority_limit` e valor contestado |
| Concorrência | `If-Match` e `caseVersion` |
| Idempotência | tabela por tenant, action, chave e hash do payload |
| Retry seguro | repetição idêntica retorna o resultado persistido |
| Conflito de payload | mesma chave com hash diferente retorna `409` |
| Resultado ambíguo | estado `RECONCILIATION_REQUIRED` |
| Auditoria | timeline append-only |
| Eventos | outbox gravado na mesma transação do aggregate |

## Persistência

O caso é mantido como aggregate JSONB, acompanhado por colunas de consulta e
versão. Cada mutação:

1. abre transação;
2. bloqueia o aggregate;
3. verifica idempotência;
4. compara versões;
5. consulta OPA;
6. aplica a transição;
7. atualiza o aggregate;
8. grava timeline e outbox;
9. persiste a resposta idempotente;
10. confirma a transação.

## Execução local

```bash
docker compose --profile vertical-slice up -d --build
bash samples/vertical-slice/tests/e2e.sh
```

Serviços:

| Serviço | Porta padrão |
|---|---:|
| API | 8080 |
| OPA | 8181 |
| PostgreSQL | 5432 |

## Teste E2E

A pipeline valida:

- compilação em .NET 10;
- subida do ambiente;
- happy path completo;
- replay idempotente;
- proteção da timeline por role e purpose;
- isolamento entre tenants;
- contratos, policies, diagramas e documentação.

## Próxima evolução

O P5 deve adicionar:

- evaluation datasets;
- testes de prompt injection documental;
- OpenTelemetry;
- métricas, traces e dashboards;
- SLOs e alertas;
- runbooks;
- publicação real do outbox em event backbone;
- avaliação contínua de agentes e documentos.
