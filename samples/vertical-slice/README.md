# Vertical Slice — Contestação bancária

Baseline executável do primeiro case da Intelligent Backoffice Platform.

## O que está implementado

- API ASP.NET Core em um modular monolith;
- persistência do aggregate do caso em PostgreSQL;
- máquina de estados alinhada ao lifecycle P1;
- Document Intelligence determinístico e sintético;
- investigação e recomendação mock;
- aprovação humana com segregação e alçada;
- execução mock idempotente;
- reconciliação de resultado ambíguo;
- Policy Decision Point OPA em runtime, fail-closed;
- JWT HS256 exclusivo para desenvolvimento local;
- controle `If-Match` por versão do caso;
- timeline append-only;
- outbox transacional para eventos P3;
- teste E2E do happy path e de controles negativos.

## Executar

Pré-requisitos: Docker, Docker Compose, Python 3 e `jq`.

```bash
export DEMO_JWT_SECRET="local-development-secret-change-me-1234567890"
docker compose --profile vertical-slice up -d --build
bash samples/vertical-slice/tests/e2e.sh
```

A API fica disponível em `http://localhost:8080`.

Para encerrar:

```bash
docker compose --profile vertical-slice down -v
```

## Componentes

| Componente | Implementação P4 |
|---|---|
| Case API | ASP.NET Core Minimal API |
| Workflow Orchestrator | módulo transacional dentro da API |
| Document Intelligence | mock determinístico |
| Human Approval | endpoint protegido por OPA |
| Governed Execution | mock com idempotência e reconciliação |
| Persistence | PostgreSQL 17 |
| Policy Decision Point | OPA |
| Eventing | outbox PostgreSQL; broker ainda não implementado |
| Identity | JWT HS256 local; não é profile produtivo |

## Profile de segurança local

O token local é um JWT HS256 assinado por segredo compartilhado e inclui:

- `sub`;
- `actor_type`;
- `tenant_id`;
- `roles`;
- `purpose`;
- `authority_limit`;
- `iss`, `aud` e `exp`.

Exemplo:

```bash
python samples/vertical-slice/scripts/create-demo-token.py \
  --subject analyst-1 \
  --type HUMAN \
  --tenant 11111111-1111-4111-8111-111111111111 \
  --roles operations-analyst,investigator,decision-agent \
  --purpose OPERATIONS
```

Produção exige identidade corporativa de workload e usuário, chaves gerenciadas,
rotação, revogação, audience por serviço e transporte autenticado.

## Comportamento do mock de execução

- `commandHash` comum: retorna `SUCCEEDED`;
- `commandHash` iniciado por `0000`: retorna `RECONCILIATION_REQUIRED`.

Esse comportamento é determinístico e existe somente para testar os dois caminhos.

## Limites

- não usa dados reais;
- não chama Core bancário;
- não executa efeito financeiro;
- não publica o outbox em Kafka;
- não possui modelo de IA real;
- não substitui certificação de segurança, privacidade ou operação.
