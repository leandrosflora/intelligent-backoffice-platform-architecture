# Intelligent Backoffice Platform Architecture

Esta documentação descreve uma plataforma corporativa para automação de processos de backoffice regulados, documentais e de longa duração.

## Estado da evolução

| Fase | Estado | Entrega |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries e sequências |
| P3 | Concluído | Contratos, schemas, catálogo e policies |
| P4 | Concluído | Vertical slice, persistência local, OPA runtime e testes E2E |
| P5 | Concluído | Evals, métricas, traces, SLOs, alertas e runbooks |
| P6 | Baseline executável | Event backbone, outbox, inbox, workers, timers, retry, DLQ e replay |

## O que o P6 prova

- estado, timeline e evento são persistidos no mesmo commit local;
- o publisher pode reenviar sem perder o evento;
- o consumidor é idempotente;
- timers sobrevivem ao processo da API;
- falhas excedendo o retry budget geram dead letter durável;
- replay exige autorização, motivo e nova identidade de evento;
- a jornada é validada com Redpanda real em Docker Compose.

## O que o P6 não prova

- HA ou disaster recovery;
- storage produtivo;
- replicação multi-AZ;
- ACL, mTLS ou identidade de workload;
- schema registry e compatibility gates de broker;
- retenção corporativa;
- throughput de produção.

## Comece por aqui

1. [Contexto de negócio](context/business-context.md)
2. [Arquitetura funcional](functional/index.md)
3. [Arquitetura técnica](architecture/index.md)
4. [Contratos](contracts/index.md)
5. [Event backbone P6](operations/eventing.md)
6. [Case aplicado](case-study/index.md)
