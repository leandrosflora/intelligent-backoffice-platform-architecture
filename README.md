# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Vertical Slice](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para automação inteligente de backoffice com agentes, processamento documental, workflows, human-in-the-loop, policies, auditoria e integração governada com sistemas corporativos.

## Primeiro case aplicado

O primeiro case é uma jornada bancária de contestação:

1. abertura e triagem;
2. recebimento e validação documental;
3. investigação;
4. recomendação explicável;
5. aprovação humana conforme alçada;
6. execução governada e idempotente;
7. reconciliação, auditoria e encerramento.

## Evolução

| Fase | Estado | Conteúdo |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Arquitetura funcional, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries, deployment e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas, catálogo e policies |
| P4 | Implementado nesta branch | Vertical slice executável e OPA em runtime |
| P5 | Próximo | Evals, observabilidade, SLOs e runbooks operacionais |

## P4 — Vertical slice

O primeiro slice executável inclui:

- API FastAPI modular;
- persistência SQLite em volume;
- workflow com versionamento otimista;
- document intelligence e investigação mocks;
- recomendação e aprovação segregadas;
- execução mock com idempotência;
- caminho `RECONCILIATION_REQUIRED` para resultado ambíguo;
- OPA consultado por HTTP em runtime;
- timeline auditável;
- testes unitários e ponta a ponta em Docker Compose.

As responsabilidades permanecem separadas no código, mas são empacotadas em um único serviço para reduzir complexidade do primeiro slice.

## Executar o runtime

Pré-requisitos: Docker e Docker Compose.

```bash
docker compose --profile runtime up --build
```

- API: `http://localhost:8080`
- Swagger: `http://localhost:8080/docs`
- OPA: `http://localhost:8181`

Para remover dados e volumes:

```bash
docker compose --profile runtime down -v
```

## Executar testes

```bash
cd samples/vertical-slice
python -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest --cov=app --cov-fail-under=85
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

## Princípio de leitura

- **atual:** capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em CI ou no ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

O P4 é uma baseline executável. Não utiliza dados reais, modelo real, OCR real ou integração bancária produtiva.
