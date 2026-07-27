# Roadmap e histórico de evolução

As fases abaixo registram a sequência de construção do repositório. Elas não representam o estado operacional de uma capacidade. Para avaliar o que está confirmado, planejado ou pronto para produção, use os diagramas atuais e alvo, a matriz de rastreabilidade e o production readiness.

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

## Estado canônico

O estado formal da solução permanece **`NOT_PRODUCTION_READY`**. Os controles demonstrados localmente comprovam padrões e mecanismos, mas não substituem integração corporativa, testes representativos, operação 24x7 e aprovação formal.

Consulte:

- [Como ler esta arquitetura](guide/how-to-read.md)
- [Arquitetura técnica](architecture/index.md)
- [Implementação de referência](implementation/index.md)
- [Production readiness](governance/production-readiness.md)

## Regra de evolução

Uma capacidade só deve avançar de estado quando possuir evidência atual, owner, contratos, testes, observabilidade e critérios operacionais compatíveis com o risco.