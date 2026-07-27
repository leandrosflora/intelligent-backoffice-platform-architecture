# Arquitetura técnica

O P2 materializa a arquitetura funcional do case em C4, componentes, deployment, trust boundaries e sequências.

## Estado atual e alvo

| Visão | Objetivo |
|---|---|
| [Contexto atual](c4-context-current.md) | Mostrar honestamente o repositório documental já existente |
| [Contexto alvo](c4-context-target.md) | Posicionar a futura plataforma no ecossistema corporativo |
| [Containers atuais](c4-container-current.md) | Inventariar artefatos e pipelines já implementados |
| [Containers alvo](c4-container-target.md) | Separar responsabilidades da futura plataforma |

## Detalhamento

- [Workflow Orchestrator](component-workflow-orchestrator.md)
- [Document Intelligence](component-document-intelligence.md)
- [Deployment local](deployment-local.md)
- [Trust boundaries](trust-boundaries.md)
- [Diagramas de sequência](sequence-diagrams.md)

## Camadas da arquitetura-alvo

1. canais e intake;
2. workflow orchestration;
3. agent runtime;
4. document intelligence;
5. knowledge;
6. policy enforcement;
7. human approval;
8. governed execution;
9. evidence, audit e observability.

!!! warning "Leitura obrigatória"
    Diagramas marcados como alvo não representam software implementado. Uma capacidade só muda de estado quando possui código, teste, evidência, owner, monitoramento e documentação.
