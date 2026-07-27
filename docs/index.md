# Intelligent Backoffice Platform Architecture

Esta documentação descreve uma plataforma corporativa para automação de processos de backoffice regulados, documentais e de longa duração.

## Hipótese arquitetural

Uma plataforma compartilhada deve permitir que diferentes domínios combinem agentes, documentos, workflows, policies, aprovação humana e execução em sistemas corporativos sem replicar controles críticos em cada solução.

## Primeiro case

O primeiro case aplicado é uma jornada bancária de contestação, desde a abertura até a decisão, execução governada e reconciliação.

## Estado da evolução

| Fase | Estado | Entrega |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, capacidades, domínios, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, deployment, trust boundaries e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas, catálogo e policies |
| P4 | Concluído neste change set | Vertical slice executável, OPA em runtime e E2E |
| P5 | Próximo | Evals, observabilidade, SLOs e runbooks |

## Princípios

- human-in-the-loop proporcional ao risco;
- default deny para ações e dados não públicos;
- agentes não acessam sistemas de registro diretamente;
- decisões e evidências são versionadas;
- operações mutáveis são idempotentes e reconciliáveis;
- observabilidade não registra conteúdo sensível por padrão;
- aprovação, execução e auditoria possuem responsabilidades separadas;
- contratos e policies são validados antes da implementação;
- uma baseline executável não equivale a prontidão produtiva.

## Comece por aqui

1. [Contexto de negócio](context/business-context.md)
2. [Arquitetura funcional](functional/index.md)
3. [Arquitetura técnica](architecture/index.md)
4. [Contratos executáveis](contracts/index.md)
5. [P4 — Vertical slice](implementation/vertical-slice.md)
6. [Case aplicado](case-study/index.md)
7. [Governança](governance/index.md)
