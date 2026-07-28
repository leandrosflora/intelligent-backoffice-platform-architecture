# Arquitetura técnica

A arquitetura técnica materializa o modelo funcional em visões C4, componentes, deployments, trust boundaries, sequências e decisões arquiteturais. As páginas separam explicitamente a baseline de referência, a implementação de produto iniciada, a integração validada e o target corporativo.

## Estado atual e alvo

| Visão | Objetivo |
|---|---|
| [Estado de implementação](implementation-status.md) | Comparar contratos, baseline, produto em construção, integração e gaps para produção |
| [Repositórios de produto](../implementation/product-repositories.md) | Explicar como arquitetura, backend .NET e frontend React se relacionam |
| [Contexto atual](c4-context-current.md) | Mostrar pessoas, sistemas e limites do ecossistema atual |
| [Contexto alvo](c4-context-target.md) | Posicionar a plataforma no ecossistema corporativo futuro |
| [Containers atuais](c4-container-current.md) | Separar containers de produto em construção dos containers da baseline |
| [Containers alvo](c4-container-target.md) | Separar responsabilidades lógicas da futura plataforma |

## Três trilhas complementares

1. **Arquitetura e contratos:** este repositório define decisões, contratos, policies, diagramas e readiness.
2. **Baseline executável:** o vertical slice FastAPI comprova padrões e controles com dados sintéticos.
3. **Implementação de produto:** backend .NET e frontend React começam a materializar a solução em repositórios separados.

A existência das três trilhas não significa integração concluída. O próximo marco é um E2E cross-repo que suba frontend, API, PostgreSQL e OPA e produza evidência reproduzível.

## Decisões arquiteturais

Os [Architecture Decision Records](../decisions/index.md) registram por que as principais escolhas foram adotadas, quais alternativas foram rejeitadas e quais condições exigem revisão.

As decisões cobrem:

- monólito modular na implementação de referência;
- decomposição lógica do target distribuído;
- autoridade do workflow;
- limites de autonomia da IA;
- PDP externo, aprovação humana e execução governada;
- eventing, evidências, identidade, persistência, observabilidade e architecture-as-code.

## Deployments executáveis e alvo

- [Deployment observado](deployment-observed-baseline.md): runtime modular, OPA, observabilidade e evals da baseline.
- [Deployment distribuído](deployment-distributed-baseline.md): event backbone, workers, timers, DLQ e replay da baseline.
- [Repositórios de produto](../implementation/product-repositories.md): topologia local em construção com React, .NET, PostgreSQL e OPA.
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
    Código em um repositório de produto recebe o estado `IMPLEMENTATION_STARTED`. Apenas uma execução integrada, reproduzível e observável permite avançar para `VALIDATED_INTEGRATION`. Diagramas alvo continuam não representando software implementado.
