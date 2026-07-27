# Intelligent Backoffice Platform Architecture

Esta documentação descreve uma plataforma corporativa para automação de processos de backoffice regulados, documentais e de longa duração.

## Estado da evolução

| Fase | Estado | Entrega |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries e sequências |
| P3 | Concluído | Contratos, schemas, catálogo e policies |
| P4 | Baseline executável | Vertical slice, persistência local, OPA runtime e testes E2E |
| P5 | Baseline executável | Evals, métricas, traces, SLOs, alertas e runbooks |
| P6 | Planejado | Mensageria, outbox, workers e workflow distribuído |

## O que o P5 prova

- instrumentação OpenTelemetry sem registrar conteúdo integral de documentos;
- métricas Prometheus de baixa cardinalidade;
- dashboard Grafana provisionado;
- traces consultáveis no Jaeger;
- SLOs e alertas vinculados a runbooks;
- dataset e thresholds de eval versionados;
- abstention para entrada desconhecida ou sem grounding;
- evidence artifacts publicados pelo CI.

## O que ainda não prova

- prontidão produtiva;
- qualidade de OCR ou LLM real;
- retenção e segurança corporativa de telemetria;
- testes de carga e capacidade;
- plantão, incident management e operação 24x7;
- mensageria e execução distribuída.

## Comece por aqui

1. [Contexto de negócio](context/business-context.md)
2. [Arquitetura funcional](functional/index.md)
3. [Arquitetura técnica](architecture/index.md)
4. [Contratos](contracts/index.md)
5. [Implementação P4](implementation/index.md)
6. [Evals P5](evaluation/index.md)
7. [Operações P5](operations/index.md)
