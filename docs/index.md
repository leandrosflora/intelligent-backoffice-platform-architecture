# Intelligent Backoffice Platform Architecture

Esta documentação descreve uma plataforma corporativa para automação de processos de backoffice regulados, documentais e de longa duração.

## Hipótese arquitetural

Uma plataforma compartilhada deve permitir que diferentes domínios combinem agentes, documentos, workflows, políticas, aprovação humana e execução em sistemas corporativos sem replicar controles críticos em cada solução.

## Primeiro case

O primeiro case aplicado é uma jornada bancária de contestação, desde a abertura até a decisão e execução governada.

## Estado da evolução

| Fase | Estado | Entrega |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs, pipelines e contratos iniciais |
| P1 | Concluído neste change set | Contexto, outcomes, capacidades, domínios, lifecycle, regras, risco e NFRs |
| P2 | Próximo | C4 e sequências |
| P3 | Planejado | Contratos executáveis completos |
| P4 | Planejado | Policy Enforcement executável |
| P5 | Planejado | Vertical slice mínimo |

## Princípios iniciais

- human-in-the-loop proporcional ao risco;
- default deny para ações e dados não públicos;
- agentes não acessam sistemas de registro diretamente;
- decisões e evidências são versionadas;
- operações mutáveis são idempotentes e reconciliáveis;
- observabilidade não registra conteúdo sensível por padrão;
- aprovação, execução e auditoria possuem responsabilidades separadas.

## Comece por aqui

1. [Contexto de negócio](context/business-context.md)
2. [Arquitetura funcional](functional/index.md)
3. [Case aplicado](case-study/index.md)
4. [Arquitetura técnica](architecture/index.md)
5. [Governança](governance/index.md)
