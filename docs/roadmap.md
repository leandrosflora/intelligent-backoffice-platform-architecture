# Roadmap e histórico de evolução

As fases abaixo registram a sequência de construção da arquitetura, da baseline e dos repositórios de produto. Elas não representam automaticamente o estado operacional de uma capacidade. Para avaliar o que está contratado, iniciado, demonstrado, integrado ou pronto para produção, use a matriz de implementação e o production readiness.

| Fase | Estado | Entrega principal |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries, deployments e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas, catálogo e policies |
| P4 | Concluído | Vertical slice executável, persistência local e OPA |
| P5 | Concluído | Evals, observabilidade, SLOs, alertas e runbooks |
| P6 | Concluído | Event backbone, outbox, inbox, workers, timers, DLQ e replay |
| P7 | Baseline executável | Identidade assinada, KMS policy, SBOM, proveniência, HA/DR, capacidade e readiness gates |
| P8 | Em andamento | Backend de produto em .NET e frontend React em repositórios separados |

## P8 — Implementação de produto

### Entregas iniciadas

- `backoffice-platform-api`: domínio, APIs, PostgreSQL, OPA externo, execução mock e reconciliação;
- `intelligent-backoffice-frontend`: console React, jornada guiada, identidades da baseline, evidências, execuções, timeline e Nginx;
- atualização desta arquitetura para representar o ecossistema multi-repositório.

### Critério de conclusão

P8 não será considerado concluído apenas porque frontend e backend compilam separadamente. O gate mínimo exige:

1. Compose ou ambiente integrado com frontend, API, PostgreSQL e OPA;
2. E2E automatizado da jornada principal;
3. E2E do resultado ambíguo e reconciliação;
4. OpenAPI publicada pelo backend e teste de compatibilidade contratual;
5. pipeline de CI do backend;
6. observabilidade e correlation ID atravessando frontend e backend;
7. evidências reproduzíveis publicadas pelo CI.

## Próximas fases sugeridas

| Fase | Objetivo |
|---|---|
| P9 | Integração cross-repo, Compose unificado e contract testing |
| P10 | Identidade assinada, observabilidade e eventing no backend de produto |
| P11 | Integrações reais, dados representativos e validação operacional |

## Estado canônico

O estado formal da solução permanece **`NOT_PRODUCTION_READY`**. A baseline comprova padrões; os repositórios de produto comprovam que a implementação começou. Ainda faltam integração validada, operação 24x7 e aprovação formal.

Consulte:

- [Repositórios de implementação do produto](implementation/product-repositories.md)
- [Estado de implementação](architecture/implementation-status.md)
- [Como ler esta arquitetura](guide/how-to-read.md)
- [Arquitetura técnica](architecture/index.md)
- [Production readiness](governance/production-readiness.md)

## Regra de evolução

Uma capacidade só deve avançar de estado quando possuir evidência atual, owner, contratos, testes, observabilidade e critérios operacionais compatíveis com o risco.
