# Arquitetura técnica

A arquitetura técnica materializa o modelo funcional em visões C4, componentes, deployments, trust boundaries e sequências. As páginas separam explicitamente o que está confirmado na implementação de referência do que representa a evolução alvo.

!!! info "Fonte canônica da baseline executável"
    As visões C4 chamadas de **atuais** ainda registram o estado documental inicial do repositório. Até a atualização semântica desses diagramas, use os deployments observado e distribuído para entender o runtime que está efetivamente demonstrado.

## Estado atual e alvo

| Visão | Objetivo |
|---|---|
| [Contexto atual](c4-context-current.md) | Registrar o estado documental inicial do repositório |
| [Contexto alvo](c4-context-target.md) | Posicionar a plataforma no ecossistema corporativo futuro |
| [Containers atuais](c4-container-current.md) | Inventariar os artefatos e pipelines da referência inicial |
| [Containers alvo](c4-container-target.md) | Separar responsabilidades lógicas da futura plataforma |

## Deployments executáveis e alvo

- [Deployment observado](deployment-observed-baseline.md): runtime modular, OPA, observabilidade e evals.
- [Deployment distribuído](deployment-distributed-baseline.md): event backbone, workers, timers, DLQ e replay.
- [Deployment alvo de produção](deployment-production-target.md): topologia corporativa com HA, identidade, segurança e recuperação.

## Detalhamento

- [Workflow Orchestrator](component-workflow-orchestrator.md)
- [Document Intelligence](component-document-intelligence.md)
- [Deployment local alvo](deployment-local.md)
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