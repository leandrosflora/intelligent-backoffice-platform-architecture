# Vertical slice executável

Implementação modular do fluxo de contestação com três profiles independentes.

## Runtime mínimo

```bash
docker compose --profile runtime up --build
```

API em `http://localhost:8080`.

## Runtime observado

```bash
OTEL_TRACING_ENABLED=true docker compose --profile observability up --build
```

Adiciona Prometheus, Grafana, OpenTelemetry Collector e Jaeger.

## Runtime distribuído P6

```bash
docker compose --profile distributed up --build
```

API em `http://localhost:8081`. O profile adiciona Redpanda, outbox publisher, workflow worker e timer worker.

### Persistência assíncrona

A baseline usa SQLite compartilhado para:

- casos e timeline;
- outbox;
- inbox;
- timers;
- dead letters;
- replay audit.

O uso de SQLite entre processos é restrito ao ambiente local. O banco é configurado com WAL e busy timeout para a demonstração.

### Prova E2E

```bash
python scripts/run_p6_distributed_e2e.py
```

O teste comprova:

1. publicação pelo outbox;
2. consumo idempotente;
3. expiração por timer;
4. retry finito;
5. dead letter;
6. replay autorizado e auditado.

## Limites

- sem LLM ou OCR real;
- sem sistema bancário real;
- sem dados reais;
- broker single-node;
- replication factor um;
- sem schema registry, mTLS ou ACL produtiva;
- sem identidade criptográfica;
- não é produção.
