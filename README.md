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

## Objetivos

- demonstrar workflows agentic assíncronos e de longa duração;
- separar análise, aprovação, execução e auditoria;
- aplicar default deny, segregação por tenant e políticas por ação;
- versionar contratos, eventos, evidências e decisões;
- permitir evolução do case para fraude, chargeback, onboarding, compliance e jurídico.

## Estrutura

```text
.
├── .github/workflows/                 # qualidade e publicação da documentação
├── C4/                               # modelos arquiteturais
├── contracts/
│   ├── openapi/                      # contratos HTTP
│   ├── asyncapi/                     # contratos de eventos
│   └── policy/                       # contratos declarativos de autorização
├── docs/
│   ├── architecture/
│   ├── case-study/
│   ├── governance/
│   ├── operations/
│   ├── security/
│   └── services/
├── policies/                         # policies executáveis
├── scripts/                          # validações e automações
├── samples/                          # vertical slices e exemplos
├── docker-compose.yml
├── mkdocs.yml
└── IntelligentBackofficePlatformArchitecture.sln
```

## Documentação local

Com Python instalado:

```bash
python -m pip install mkdocs-material pyyaml
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

Este repositório inicia como referência documental e arquitetural. Serviços executáveis, contratos completos, políticas de produção e vertical slices serão adicionados de forma incremental.
