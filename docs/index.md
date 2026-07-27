# Intelligent Backoffice Platform Architecture

Arquitetura de referência executável para processos de backoffice regulados, documentais e de longa duração.

## Estado da evolução

| Fase | Estado | Entrega |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries e sequências |
| P3 | Concluído | Contratos, schemas, catálogo e policies |
| P4 | Concluído | Vertical slice, persistência local e OPA |
| P5 | Concluído | Evals, observabilidade, SLOs e runbooks |
| P6 | Concluído | Event backbone, outbox, inbox, workers, timers, DLQ e replay |
| P7 | Baseline executável | Identidade assinada, KMS policy, SBOM, proveniência, HA/DR, capacidade e readiness gates |

## O que o P7 prova

- JWT EdDSA de curta duração é validado e headers não elevam privilégios;
- finalidade é ligada à ação pelo OPA;
- imagem local executa sem root;
- backup sintético é criptografado e restaurado com integridade;
- SBOM e proveniência são gerados na pipeline;
- manifests de HA e segurança passam por validação estrutural;
- regressão de capacidade possui threshold;
- o status permanece `NOT_PRODUCTION_READY` com blockers explícitos.

## Comece por aqui

1. [Contexto de negócio](context/business-context.md)
2. [Arquitetura funcional](functional/index.md)
3. [Deployment alvo de produção](architecture/deployment-production-target.md)
4. [Identidade de workload](security/workload-identity.md)
5. [Alta disponibilidade e DR](operations/ha-dr.md)
6. [Production readiness](governance/production-readiness.md)
