# Vertical slice executável

Implementação modular do fluxo de contestação com profiles independentes.

## Runtime mínimo

```bash
docker compose --profile runtime up --build
```

API em `http://localhost:8080`. A identidade usa headers exclusivamente para compatibilidade da baseline P4.

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

## Runtime seguro P7

```bash
python scripts/generate_dev_identity.py --force
docker compose --profile secure up --build
```

API em `http://localhost:8082`. Nesse profile:

- headers de identidade são ignorados;
- JWT EdDSA é obrigatório;
- TTL máximo é 300 segundos;
- issuer, audience, tenant, roles, finalidade e assinatura são validados;
- o OPA verifica o método de autenticação e a finalidade.

Prova E2E:

```bash
python scripts/run_p7_secure_e2e.py
```

## Persistência assíncrona

A baseline P6 usa SQLite compartilhado para casos, timeline, outbox, inbox, timers, dead letters e replay audit. WAL e busy timeout são escolhas locais.

## Limites

- sem LLM ou OCR real;
- sem sistema bancário ou dados reais;
- broker single-node;
- replication factor um;
- chaves P7 locais e efêmeras;
- sem SPIFFE, OIDC corporativo, mTLS, KMS ou secret manager real;
- sem database Multi-AZ;
- não é produção.
