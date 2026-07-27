# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para automação inteligente de backoffice com agentes, processamento documental, workflows, human-in-the-loop, políticas, auditoria e integração governada com sistemas corporativos.

## Primeiro case aplicado

O primeiro case é uma jornada bancária de contestação:

1. abertura e triagem do caso;
2. recebimento e classificação de documentos;
3. extração e validação de evidências;
4. consulta a sistemas corporativos;
5. recomendação de decisão;
6. aprovação humana quando exigida;
7. execução governada;
8. auditoria e encerramento.

## Evolução

| Fase | Estado | Conteúdo |
|---|---|---|
| P0 | Concluído | Estrutura do repositório, MkDocs e pipelines |
| P1 | Concluído | Arquitetura funcional e lifecycle do case |
| P2 | Implementado nesta branch | C4, componentes, deployment, trust boundaries e sequências |
| P3 | Próximo | OpenAPI, AsyncAPI e policies completas |
| P4 | Planejado | Policy Enforcement executável |
| P5 | Planejado | Vertical slice mínimo |

## Artefatos P2

- contexto atual e alvo;
- containers atuais e alvo;
- componentes do Workflow Orchestrator;
- componentes de Document Intelligence;
- deployment local do futuro vertical slice;
- sete trust boundaries;
- quatro sequências críticas;
- renderização PlantUML em SVG e PNG;
- validação de diagramas no CI.

## Princípio de leitura

O repositório separa explicitamente:

- **atual:** artefato ou capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

Um diagrama alvo não é evidência de implementação.

## Estrutura

```text
.
├── .github/workflows/
├── C4/                         # fontes PlantUML
├── contracts/
├── docs/
│   ├── assets/diagrams/        # gerados em CI
│   ├── context/
│   ├── functional/
│   ├── architecture/
│   ├── case-study/
│   ├── governance/
│   ├── operations/
│   ├── security/
│   └── services/
├── policies/
├── scripts/
├── samples/
├── docker-compose.yml
├── mkdocs.yml
└── IntelligentBackofficePlatformArchitecture.sln
```

## Documentação local

Pré-requisitos: Python e Docker.

```bash
python -m pip install -r requirements-docs.txt
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
mkdocs serve
```

Ou, após gerar os diagramas:

```bash
docker compose --profile docs up
```

Acesse `http://localhost:8000`.

## Validação

```bash
python scripts/validate_structure.py
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
mkdocs build --strict
docker compose config
```

## Estado

O P2 continua documental e arquitetural. Nenhum serviço produtivo, modelo real, documento de cliente ou integração bancária foi adicionado.
