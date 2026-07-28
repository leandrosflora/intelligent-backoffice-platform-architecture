# Como ler esta arquitetura

Este repositório combina especificação arquitetural, contratos executáveis, implementação de referência, decisões arquiteturais e evidências produzidas por CI. A ordem de leitura depende da decisão que você precisa tomar.

## Conceitos de estado

| Termo | Significado |
|---|---|
| **Atual** | Capacidade confirmada por código, configuração, teste ou evidência versionada |
| **Baseline executável** | Controle demonstrado no ambiente local ou no CI, com limitações explícitas |
| **Alvo** | Responsabilidade ou topologia planejada, ainda dependente de implementação e validação |
| **Produção** | Integração real, operação, segurança, governança e ownership formalmente aprovados |

!!! warning "Alvo não significa implementado"
    Diagramas e contratos de arquitetura-alvo descrevem a direção pretendida. O estado canônico de prontidão está em [Production readiness](../governance/production-readiness.md).

## Trilhas por público

| Público | Comece por | Continue por | Decisão apoiada |
|---|---|---|---|
| Executivo ou gestor | [Contexto de negócio](../context/business-context.md) | [Outcome card](../functional/outcome-card.md) e [Production readiness](../governance/production-readiness.md) | Valor, risco e condições para evolução |
| Arquiteto | [Arquitetura funcional](../functional/index.md) | [Arquitetura técnica](../architecture/index.md), [ADRs](../decisions/index.md), [walkthrough](../tutorials/dispute-walkthrough.md), [NFRs](../functional/non-functional-requirements.md) e [rastreabilidade](../functional/traceability-matrix.md) | Limites, responsabilidades, trade-offs e evidências |
| Desenvolvedor | [Walkthrough executável](../tutorials/dispute-walkthrough.md) | [Implementação](../implementation/index.md), [contratos](../contracts/index.md), [ADRs](../decisions/index.md), [cenários testados](../implementation/test-scenarios.md) e [runbook](../implementation/runbook.md) | Como executar, alterar e validar o slice |
| Segurança | [Trust boundaries](../architecture/trust-boundaries.md) | [ADRs de controle](../decisions/index.md), [Identidade de workload](../security/workload-identity.md), [policies](../contracts/policies.md) e [supply chain](../security/supply-chain.md) | Controles, confiança e riscos residuais |
| Operações ou SRE | [Walkthrough executável](../tutorials/dispute-walkthrough.md) | [Deployment distribuído](../architecture/deployment-distributed-baseline.md), [observabilidade](../operations/observability.md), [SLOs](../operations/slos.md), [event backbone](../operations/eventing.md) e [runbooks](../operations/index.md) | Operação, diagnóstico e recuperação |
| Auditoria ou compliance | [Lifecycle](../functional/case-lifecycle.md) | [Walkthrough](../tutorials/dispute-walkthrough.md), [papéis](../functional/roles-and-responsibilities.md), [ADRs](../decisions/index.md), [rastreabilidade](../functional/traceability-matrix.md) e [evidências](../governance/production-readiness.md) | Segregação, decisões e cadeia de evidências |

## Sequência recomendada para leitura completa

1. [Contexto de negócio](../context/business-context.md)
2. [Case aplicado](../case-study/index.md)
3. [Outcome card](../functional/outcome-card.md)
4. [Mapa de capacidades](../functional/capability-map.md)
5. [Lifecycle do caso](../functional/case-lifecycle.md)
6. [Arquitetura técnica](../architecture/index.md)
7. [Architecture Decision Records](../decisions/index.md)
8. [Contratos executáveis](../contracts/index.md)
9. [Walkthrough executável](../tutorials/dispute-walkthrough.md)
10. [Implementação de referência](../implementation/index.md)
11. [Segurança e operações](../security/index.md)
12. [Production readiness](../governance/production-readiness.md)

## Como interpretar evidências

Uma afirmação arquitetural deve apontar para pelo menos um dos seguintes elementos:

- código ou configuração versionada;
- contrato OpenAPI, AsyncAPI, JSON Schema ou policy;
- ADR vigente;
- teste positivo e negativo;
- walkthrough executável;
- relatório ou artifact produzido pelo CI;
- métrica, SLO ou runbook;
- owner técnico e funcional.

A [matriz de rastreabilidade](../functional/traceability-matrix.md) conecta necessidades, capacidades, regras, estados, contratos, eventos, policies e evidências. Os [ADRs](../decisions/index.md) registram os trade-offs e as condições que sustentam essas escolhas.
