# Runbook local

Este runbook separa a baseline arquitetural deste repositório do runtime dos repositórios de produto.

## Baseline arquitetural

### Runtime mínimo

```bash
docker compose --profile runtime up --build
```

### Baseline distribuída

Use este profile para outbox, Redpanda, workers, timers, DLQ, replay e walkthrough:

```bash
docker compose --profile distributed up -d --build
```

### Verificar saúde

```bash
curl http://localhost:8080/health
curl http://localhost:8081/health
```

### Executar walkthrough

```bash
python scripts/run_dispute_walkthrough.py
```

Evidências:

```text
artifacts/walkthrough/dispute-walkthrough.jsonl
artifacts/walkthrough/dispute-walkthrough-summary.json
```

Consulte o [walkthrough executável](../tutorials/dispute-walkthrough.md).

## Runtime do backend de produto

Mantenha os repositórios como diretórios irmãos:

```text
workspace/
├── intelligent-backoffice-platform-architecture/
├── backoffice-platform-api/
└── intelligent-backoffice-frontend/
```

### Runtime síncrono

```bash
cd backoffice-platform-api
docker compose --profile runtime up -d --build
```

Serviços:

- API: `http://localhost:8080`;
- PostgreSQL: `localhost:5432`;
- OPA: `http://localhost:8181`.

Verifique:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/health/ready
```

### Runtime distribuído

```bash
cd backoffice-platform-api
docker compose --profile distributed up -d --build
```

Serviços adicionais:

- API: `http://localhost:8081`;
- Redpanda: `localhost:19092`;
- outbox dispatcher;
- workflow worker;
- timer worker.

Endpoints operacionais:

```text
GET  /v1/operations/outbox
GET  /v1/operations/timers
GET  /v1/operations/dead-letters
POST /v1/operations/dead-letters/{deadLetterId}/replay
```

### Observabilidade

```bash
cd backoffice-platform-api
docker compose --profile observability up -d --build
```

| Serviço | Endereço |
|---|---|
| API | `http://localhost:8080` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |
| Jaeger | `http://localhost:16686` |

### Profile seguro

O profile `secure` usa JWT EdDSA e publica a API em `http://localhost:8082`.

Ele exige a chave pública local em:

```text
backoffice-platform-api/.local/security/identity-public.pem
```

## Frontend de produto

### Desenvolvimento

Com o backend em `http://localhost:5260`:

```bash
cd intelligent-backoffice-frontend/intelligent-backoffice-frontend
npm ci
npm run dev
```

Abra `http://localhost:5173`.

### Docker com backend containerizado

Com a API publicada em `8080`:

```bash
cd intelligent-backoffice-frontend
BACKEND_URL=http://host.docker.internal:8080 docker compose up -d --build
```

Abra `http://localhost:3000`.

Quando o Grafana estiver usando `3000`:

```bash
BACKEND_URL=http://host.docker.internal:8080 FRONTEND_PORT=3001 docker compose up -d --build
```

## Resetar dados

Baseline:

```bash
docker compose --profile runtime down -v
docker compose --profile distributed down -v
```

Backend de produto:

```bash
cd backoffice-platform-api
docker compose --profile runtime down -v
docker compose --profile distributed down -v
```

Frontend:

```bash
cd intelligent-backoffice-frontend
docker compose down
```

## Falha do OPA

A aplicação deve falhar fechada e não executar a ação protegida. Verifique:

- container `opa`;
- policies montadas;
- `Opa__BaseUrl`;
- tenant, papel, finalidade e estado enviados no input.

## Resultado ambíguo

O caso muda para `RECONCILIATION_REQUIRED`. Não repita a execução com uma nova chave.

Consulte:

```text
GET /v1/cases/{caseId}/executions/{executionId}
```

Depois registre a resolução:

```text
POST /v1/cases/{caseId}/reconciliations/{executionId}/resolve
```

A resolução exige papel `reconciler`, `If-Match`, `Idempotency-Key`, versão do caso e justificativa.

## Diagnóstico inicial

| Sintoma | Verificação |
|---|---|
| Frontend retorna erro de conexão | Confirme `BACKEND_URL` e a porta publicada pela API |
| Ação protegida retorna `503` | Confirme saúde e URL do OPA |
| Ação retorna `403` | Revise identidade, papéis, tenant, finalidade e alçada |
| Mutação retorna conflito | Atualize o caso e envie a versão correta em `If-Match` |
| Worker não processa | Verifique Redpanda, tópico, consumer group, outbox e dead letters |
| Readiness retorna `503` | Verifique conexão e migrations do PostgreSQL |

## Limite do runbook

Os comandos demonstram execução local controlada. Ainda não existe um pipeline único que suba navegador, frontend, backend, PostgreSQL e OPA e publique evidências E2E cross-repo.
