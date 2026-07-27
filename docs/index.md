# Intelligent Backoffice Platform Architecture

Esta documentação descreve uma plataforma corporativa para automação de processos de backoffice regulados, documentais e de longa duração.

## Primeiro case

O primeiro case aplicado é uma jornada bancária de contestação, desde a abertura até a decisão e execução governada.

## Estado da evolução

| Fase | Estado | Entrega |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries e sequências |
| P3 | Concluído | Contratos, schemas, catálogo e policies |
| P4 | Baseline executável | Vertical slice, persistência local, OPA runtime e testes E2E |
| P5 | Próximo | Evals, observabilidade, SLOs e operação |

## O que o P4 prova

- jornada ponta a ponta com dados sintéticos;
- separação entre recomendação, aprovação e execução;
- policy enforcement em runtime;
- versionamento otimista;
- idempotência de execução;
- reconciliação para resultado ambíguo;
- timeline auditável;
- testes automatizados em CI.

## O que o P4 não prova

- prontidão produtiva;
- integração bancária real;
- processamento documental real;
- identidade criptográfica de workloads;
- alta disponibilidade;
- mensageria e execução distribuída.

## Comece por aqui

1. [Contexto de negócio](context/business-context.md)
2. [Arquitetura funcional](functional/index.md)
3. [Arquitetura técnica](architecture/index.md)
4. [Contratos](contracts/index.md)
5. [Implementação P4](implementation/index.md)
6. [Case aplicado](case-study/index.md)
