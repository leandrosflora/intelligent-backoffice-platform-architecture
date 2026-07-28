# Walkthrough executável — contestação bancária

Este tutorial executa a jornada de contestação no profile distribuído e produz evidências verificáveis da API, workflow, policies, eventing, observabilidade, idempotência e reconciliação.

!!! warning "Baseline local"
    Todos os dados e efeitos são sintéticos. A execução financeira é mock, o armazenamento usa SQLite e o broker Redpanda opera em single-node. O walkthrough não altera o status `NOT_PRODUCTION_READY`.

## O que será demonstrado

O script executa dois casos independentes:

| Cenário | Resultado esperado |
|---|---|
| Jornada principal | criação → documento → investigação → recomendação → aprovação → execução `SUCCEEDED` |
| Resultado ambíguo | execução `RECONCILIATION_REQUIRED` → consulta da execução → reconciliação `CONFIRMED_SUCCEEDED` → caso `EXECUTED` |

Nos dois casos também são verificados:

- segregação entre agente, aprovador, serviço de execução e reconciliador;
- controle otimista por `If-Match`;
- repetição idempotente de execução e reconciliação;
- timeline auditável;
- publicação do outbox;
- consumo e projeção dos eventos;
- métricas HTTP, policy, execução e mensageria.

## Pré-requisitos

- Docker com Compose;
- Python 3.12 ou compatível;
- portas `8081`, `8181` e `19092` disponíveis.

## Executar automaticamente

Suba a baseline distribuída:

```bash
docker compose --profile distributed up -d --build
```

Execute o walkthrough:

```bash
python scripts/run_dispute_walkthrough.py
```

Encerre o ambiente e remova os volumes:

```bash
docker compose --profile distributed down -v
```

## Evidências produzidas

O script cria:

```text
artifacts/walkthrough/dispute-walkthrough.jsonl
artifacts/walkthrough/dispute-walkthrough-summary.json
```

O arquivo JSONL registra cada chamada com:

- cenário;
- etapa;
- status HTTP;
- payload retornado.

O resumo registra os casos executados, quantidade de eventos, evidências do outbox, projeções e métricas encontradas.

Exemplo de resumo:

```json
{
  "status": "PASSED",
  "happy_path": {
    "state": "EXECUTED",
    "events": 6
  },
  "ambiguous_reconciliation": {
    "state": "EXECUTED",
    "events": 7
  },
  "limitations": [
    "synthetic data",
    "mock execution",
    "SQLite local persistence",
    "single-node Redpanda",
    "not production ready"
  ]
}
```

Os identificadores reais são gerados a cada execução e aparecem no artifact.

## Jornada principal

A progressão esperada é:

```text
CREATED
  ↓ document.register
DOCUMENTS_VALIDATED
  ↓ investigation.execute
UNDER_INVESTIGATION
  ↓ recommendation.create
AWAITING_APPROVAL
  ↓ approval.decide
APPROVED
  ↓ execution.request
EXECUTED
```

A execução retorna também:

- `execution_id`;
- `execution_status: SUCCEEDED`.

A repetição da mesma chamada com a mesma `Idempotency-Key` deve retornar exatamente a mesma resposta, sem novo efeito ou evento.

## Resultado ambíguo e reconciliação

A segunda jornada força `result_mode: AMBIGUOUS`:

```text
APPROVED
  ↓ execution.request
RECONCILIATION_REQUIRED
  ↓ reconciliation.resolve
EXECUTED
```

O reconciliador registra:

```json
{
  "case_version": 6,
  "resolution": "CONFIRMED_SUCCEEDED",
  "reason": "system of record confirms the synthetic refund completed successfully"
}
```

A operação exige:

- papel `reconciler`;
- estado `RECONCILIATION_REQUIRED`;
- versão esperada no corpo e no header `If-Match`;
- `Idempotency-Key` própria;
- motivo auditável.

Após a resolução:

- o caso volta para `EXECUTED`;
- a execução fica `RECONCILED`;
- a resolução fica `CONFIRMED_SUCCEEDED`;
- a timeline recebe `backoffice.reconciliation.succeeded.v1`.

## Eventos e outbox

Cada entrada da timeline gera um registro no outbox no mesmo commit SQLite. O walkthrough aguarda até que todos os eventos dos dois casos estejam:

1. com status `PUBLISHED` no outbox;
2. registrados na projeção do consumer;
3. deduplicados pela inbox.

As consultas operacionais usadas são:

```text
GET /v1/operations/outbox
GET /v1/operations/event-projections
```

Elas exigem o papel `platform-operator` e finalidade operacional derivada pela baseline.

## Métricas verificadas

O script consulta `GET /metrics` e exige as famílias:

```text
backoffice_http_requests_total
backoffice_policy_decisions_total
backoffice_executions_total
backoffice_outbox_messages
```

Para inspeção visual, use o profile de observabilidade separadamente ou consulte as páginas de [observabilidade](../operations/observability.md) e [SLOs](../operations/slos.md).

## Executado no CI

O workflow **P6 Eventing and Distributed Workflow** executa automaticamente:

```bash
python scripts/run_p6_distributed_e2e.py
python scripts/run_dispute_walkthrough.py
```

O artifact `p6-eventing-evidence` contém tanto a evidência operacional do P6 quanto os arquivos do walkthrough.

## Relação com contratos e decisões

O fluxo demonstra diretamente:

- [ADR-003 — Workflow como autoridade](../decisions/adr-003-workflow-owns-process-state.md);
- [ADR-005 — OPA como PDP](../decisions/adr-005-opa-external-policy-decision-point.md);
- [ADR-006 — Aprovação humana](../decisions/adr-006-human-approval-and-segregation.md);
- [ADR-007 — Execução governada](../decisions/adr-007-governed-idempotent-execution.md);
- [ADR-008 — Outbox e inbox](../decisions/adr-008-outbox-inbox-at-least-once.md);
- [ADR-009 — Evidência e auditoria](../decisions/adr-009-evidence-and-append-only-audit.md).

Os endpoints canônicos estão em:

```text
contracts/openapi/paths/analysis-approval.yaml
contracts/openapi/paths/execution-audit.yaml
contracts/openapi/eventing-operations-api.yaml
```

## Diagnóstico

### API não fica saudável

```bash
docker compose --profile distributed ps
docker compose --profile distributed logs distributed-api opa
```

### Outbox não é publicado

```bash
docker compose --profile distributed logs outbox-publisher redpanda
```

### Evento não aparece na projeção

```bash
docker compose --profile distributed logs workflow-worker
```

### Reconciliação recebe `403`

Confirme o papel `reconciler`, o tenant, o estado do caso e a policy `reconciliation.resolve`.

### Reconciliação recebe `409`

Consulte novamente o caso. A versão do corpo e o `If-Match` precisam representar a versão atual, exceto na repetição idempotente da mesma requisição.
