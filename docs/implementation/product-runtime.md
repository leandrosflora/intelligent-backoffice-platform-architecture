# Runtime integrado do produto

Esta página descreve como os repositórios de produto são executados em conjunto no ambiente local e quais controles já foram incorporados ao backend.

## Topologia atual

```text
Navegador
   |
   v
React SPA / Vite ou Nginx
   |
   | REST / JSON + identidade, tenant, versão e idempotência
   v
Backoffice Platform API (.NET 9)
   |             |                 |
   | SQL         | HTTP / JSON     | outbox / eventos
   v             v                 v
PostgreSQL 16    OPA / Rego        Redpanda
                                      |
                                      v
                       Outbox Dispatcher / Workflow Worker / Timer Worker

API e workers
   |
   | OTLP / métricas
   v
OTel Collector → Prometheus / Grafana / Jaeger
```

O frontend e o backend continuam em repositórios e Composes separados. O backend, entretanto, já oferece profiles completos para runtime síncrono, eventing, observabilidade e identidade assinada.

## Organização dos diretórios

O Compose do backend reutiliza policies e configurações de observabilidade do repositório de arquitetura. Mantenha os checkouts como diretórios irmãos:

```text
workspace/
├── intelligent-backoffice-platform-architecture/
├── backoffice-platform-api/
└── intelligent-backoffice-frontend/
```

## Runtime síncrono

No backend:

```bash
cd backoffice-platform-api
docker compose --profile runtime up -d --build
```

Esse profile inicia:

- PostgreSQL;
- OPA com as policies do repositório de arquitetura;
- API .NET publicada em `http://localhost:8080`.

Verifique:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/health/ready
```

## Frontend

Na raiz do repositório do frontend:

```bash
cd intelligent-backoffice-frontend
BACKEND_URL=http://host.docker.internal:8080 docker compose up -d --build
```

Abra:

```text
http://localhost:3000
```

Em máquinas nas quais a porta `3000` está ocupada:

```bash
BACKEND_URL=http://host.docker.internal:8080 FRONTEND_PORT=3001 docker compose up -d --build
```

## Profile distribuído

```bash
cd backoffice-platform-api
docker compose --profile distributed up -d --build
```

Esse profile adiciona:

- Redpanda;
- tópicos `backoffice.events.v1` e `backoffice.dlq.v1`;
- outbox dispatcher;
- workflow consumer;
- timer worker;
- API distribuída em `http://localhost:8081`.

A superfície operacional permite inspecionar outbox, timers e dead letters, além de solicitar replay governado.

## Profile de observabilidade

```bash
cd backoffice-platform-api
docker compose --profile observability up -d --build
```

Serviços principais:

| Serviço | Endereço padrão |
|---|---|
| API | `http://localhost:8080` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` |
| Jaeger | `http://localhost:16686` |
| OTel Collector | `localhost:4317` / `localhost:4318` |

!!! warning "Conflito de porta"
    O Grafana e o frontend usam `3000` por padrão. Suba o frontend com `FRONTEND_PORT=3001` quando executar o profile de observabilidade.

## Profile seguro

O profile `secure` inicia a API em modo JWT EdDSA e publica o serviço em `http://localhost:8082`.

Ele exige material de chave local compatível em:

```text
backoffice-platform-api/.local/security/identity-public.pem
```

A demonstração valida assinatura, issuer, audience e TTL. Ainda não representa IAM corporativo, rotação automática ou KMS.

## O que a execução local comprova

- frontend consumindo a API por proxy;
- persistência PostgreSQL;
- autorização OPA em runtime;
- lifecycle e versionamento otimista;
- execução idempotente e reconciliação;
- eventing com broker e workers;
- timers, DLQ e replay;
- métricas e traces do backend;
- identidade JWT assinada no profile seguro.

## O que ainda não está comprovado

- E2E browser-based automatizado cross-repo;
- execução dos três repositórios por um único comando ou pipeline;
- compatibilidade contínua entre OpenAPI implementada e contratos arquiteturais;
- integração com IAM, object storage e sistemas de registro reais;
- telemetria distribuída iniciada no navegador;
- carga, soak, chaos, backup, restore e DR em ambiente representativo;
- operação multi-instância ou multi-região validada.

## Critério para `VALIDATED_INTEGRATION`

A integração só deve avançar quando um pipeline reproduzível:

1. sobe frontend, API, PostgreSQL e OPA;
2. executa a jornada principal no navegador;
3. valida negações de policy e conflito de versão;
4. cobre resultado ambíguo e reconciliação;
5. registra traces, métricas e evidências;
6. publica artifacts vinculados ao commit;
7. possui owner e runbook de falhas.
