# Runbook local

## Runtime mínimo

```bash
docker compose --profile runtime up --build
```

## Baseline distribuída

Use este profile para outbox, Redpanda, workers, timers, DLQ, replay e o walkthrough completo:

```bash
docker compose --profile distributed up -d --build
```

## Verificar saúde

```bash
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8181/health
```

## Executar o walkthrough

```bash
python scripts/run_dispute_walkthrough.py
```

As evidências são gravadas em:

```text
artifacts/walkthrough/dispute-walkthrough.jsonl
artifacts/walkthrough/dispute-walkthrough-summary.json
```

Consulte o [walkthrough executável](../tutorials/dispute-walkthrough.md) para a leitura passo a passo.

## Executar testes

```bash
cd samples/vertical-slice
python -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest --cov=app --cov-fail-under=85
```

## Resetar dados

Runtime mínimo:

```bash
docker compose --profile runtime down -v
```

Baseline distribuída:

```bash
docker compose --profile distributed down -v
```

## Falha do OPA

A aplicação retorna `503` e não executa a ação protegida. Verifique o container `opa`, a policy montada e o endpoint de decisão.

## Resultado ambíguo

O caso muda para `RECONCILIATION_REQUIRED`. Não repita a execução com uma nova chave.

Consulte a execução pelo endpoint:

```text
GET /v1/cases/{caseId}/executions/{executionId}
```

Depois registre a resolução:

```text
POST /v1/cases/{caseId}/reconciliations/{executionId}/resolve
```

A resolução exige papel `reconciler`, `If-Match`, `Idempotency-Key`, versão do caso e justificativa. A repetição da mesma resolução com a mesma chave retorna a resposta anterior.
