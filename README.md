# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para automação inteligente de backoffice com agentes, processamento documental, workflows, human-in-the-loop, policies, auditoria e integração governada com sistemas corporativos.

## Primeiro case aplicado

O primeiro case é uma jornada bancária de contestação:

1. abertura e triagem do caso;
2. recebimento e classificação de documentos;
3. extração e validação de evidências;
4. investigação com fontes autorizadas;
5. recomendação explicável;
6. aprovação humana conforme alçada;
7. execução governada e idempotente;
8. reconciliação, auditoria e encerramento.

## Evolução

| Fase | Estado | Conteúdo |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Arquitetura funcional, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries, deployment e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas canônicos, catálogo e policies |
| P4 | Implementado nesta branch | Vertical slice ASP.NET Core, PostgreSQL, OPA e E2E |
| P5 | Próximo | Evals, observabilidade, SLOs e runbooks |

## Baseline executável P4

O vertical slice implementa:

- modular monolith em ASP.NET Core;
- aggregate persistido em PostgreSQL;
- lifecycle e versionamento otimista;
- Document Intelligence mock;
- investigação e recomendação determinísticas;
- aprovação humana com segregação e alçada;
- execução mock idempotente e reconciliável;
- OPA em runtime com fail-closed;
- JWT HS256 exclusivo para desenvolvimento;
- timeline append-only;
- outbox transacional;
- teste E2E completo.

## Executar o vertical slice

Pré-requisitos: Docker, Docker Compose, Python 3 e `jq`.

```bash
export DEMO_JWT_SECRET="local-development-secret-change-me-1234567890"
docker compose --profile vertical-slice up -d --build
bash samples/vertical-slice/tests/e2e.sh
```

API: `http://localhost:8080`

Encerrar:

```bash
docker compose --profile vertical-slice down -v
```

Detalhes: [`samples/vertical-slice/README.md`](samples/vertical-slice/README.md).

## Princípio de leitura

O repositório separa explicitamente:

- **atual:** artefato ou capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em CI ou ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

O P4 é uma baseline executável com dados sintéticos e mocks. Não é produção bancária.

## Estrutura

```text
.
├── .github/workflows/
├── C4/
├── contracts/
├── docs/
│   ├── implementation/
│   ├── contracts/
│   ├── architecture/
│   └── ...
├── policies/
├── samples/
│   └── vertical-slice/
│       ├── src/IntelligentBackoffice.Api/
│       ├── scripts/
│       └── tests/
├── scripts/
├── docker-compose.yml
├── mkdocs.yml
└── IntelligentBackofficePlatformArchitecture.sln
```

## Documentação local

```bash
python -m pip install -r requirements-docs.txt
python scripts/validate_structure.py
python scripts/validate_contracts.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
mkdocs serve
```

Acesse `http://localhost:8000`.

## Validação completa

```bash
dotnet restore IntelligentBackofficePlatformArchitecture.sln
dotnet build IntelligentBackofficePlatformArchitecture.sln -c Release --no-restore
python scripts/validate_structure.py
python scripts/validate_contracts.py
python scripts/validate_vertical_slice.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
mkdocs build --strict
docker compose config
docker compose --profile vertical-slice up -d --build
bash samples/vertical-slice/tests/e2e.sh
docker compose --profile vertical-slice down -v
```

## Estado

O P4 não usa documentos reais, modelos reais, Core bancário ou efeitos financeiros. O event backbone, observabilidade completa e identidade corporativa permanecem para as próximas fases.
