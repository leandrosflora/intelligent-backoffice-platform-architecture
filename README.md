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
| P3 | Implementado nesta branch | OpenAPI, AsyncAPI, schemas canônicos, catálogo e policies executáveis |
| P4 | Próximo | Vertical slice mínimo e policy enforcement em runtime |
| P5 | Planejado | Evals, observabilidade, SLOs e runbooks |

## Artefatos P3

- 14 operações HTTP rastreadas por `x-contract-id`;
- 14 eventos de domínio versionados;
- 13 actions de autorização;
- 3 catálogos JSON Schema;
- catálogo canônico com 41 contratos;
- policy Rego com default deny, tenant isolation e segregação de funções;
- testes positivos e negativos de policy;
- validação de referências, idempotência, concorrência, rastreabilidade e compatibilidade no CI.

## Princípio de leitura

O repositório separa explicitamente:

- **atual:** artefato ou capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em CI ou ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

Um contrato alvo não é evidência de serviço implementado.

## Estrutura

```text
.
├── .github/workflows/
├── C4/                              # fontes PlantUML
├── contracts/
│   ├── catalog.yaml                 # inventário canônico
│   ├── openapi/                     # operações HTTP
│   ├── asyncapi/                    # eventos
│   ├── schemas/                     # modelos compartilhados
│   └── policy/                      # matriz declarativa
├── docs/
│   ├── contracts/
│   ├── assets/diagrams/             # gerados em CI
│   ├── context/
│   ├── functional/
│   ├── architecture/
│   ├── case-study/
│   ├── governance/
│   ├── operations/
│   ├── security/
│   └── services/
├── policies/                        # Rego e testes
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
python scripts/validate_structure.py
python scripts/validate_contracts.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
mkdocs build --strict
docker compose config
```

## Estado

O P3 adiciona contratos e policies executáveis em CI. Nenhum serviço produtivo, documento real de cliente, modelo real ou integração bancária foi adicionado.
