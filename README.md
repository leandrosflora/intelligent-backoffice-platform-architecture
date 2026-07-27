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
| P1 | Implementado nesta branch | Arquitetura funcional e lifecycle do case |
| P2 | Próximo | C4, trust boundaries e sequências |
| P3 | Planejado | OpenAPI, AsyncAPI e policies completas |
| P4 | Planejado | Vertical slice executável |

## Artefatos P1

- contexto de negócio;
- outcome card e métricas;
- mapa de capacidades;
- mapa de domínios;
- lifecycle com estados, transições e invariantes;
- regras de negócio versionadas;
- papéis, RACI e segregação de funções;
- classificação de risco;
- requisitos não funcionais;
- matriz de rastreabilidade.

## Objetivos

- demonstrar workflows agentic assíncronos e de longa duração;
- separar análise, aprovação, execução e auditoria;
- aplicar default deny, segregação por tenant e políticas por ação;
- versionar contratos, eventos, evidências e decisões;
- permitir evolução do case para fraude, chargeback, onboarding, compliance e jurídico.

## Estrutura

```text
.
├── .github/workflows/
├── C4/
├── contracts/
├── docs/
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

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```

Ou com Docker Compose:

```bash
docker compose --profile docs up
```

Acesse `http://localhost:8000`.

## Validação

```bash
python scripts/validate_structure.py
mkdocs build --strict
docker compose config
```

## Estado

O repositório continua sendo uma referência documental e arquitetural. O P1 não adiciona serviços produtivos, modelos reais ou integração com sistemas bancários.
