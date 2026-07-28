# Como ler esta arquitetura

Este repositório combina especificação arquitetural, contratos executáveis, baseline de referência, decisões arquiteturais, repositórios de produto e evidências produzidas por CI. A ordem de leitura depende da decisão que você precisa tomar.

## Conceitos de estado

| Termo | Significado |
|---|---|
| **Contrato definido** | API, evento, schema, policy ou decisão versionada, sem integração de produto comprovada |
| **Implementação iniciada** | Código existe em frontend ou backend, mas o E2E integrado ainda não foi comprovado |
| **Baseline executável** | Controle demonstrado no ambiente local ou no CI, com dados e integrações sintéticos |
| **Integração validada** | Componentes de produto executados em conjunto, com evidência reproduzível e gates compatíveis |
| **Alvo** | Responsabilidade ou topologia planejada, ainda dependente de implementação e validação |
| **Produção** | Integração real, operação, segurança, governança e ownership formalmente aprovados |

!!! warning "Código não significa integração validada"
    Frontend React e backend .NET já foram iniciados, mas o estado canônico de integração permanece pendente até existir um E2E cross-repo automatizado. Diagramas alvo também continuam não representando software implementado.

## Trilhas por público

| Público | Comece por | Continue por | Decisão apoiada |
|---|---|---|---|
| Executivo ou gestor | [Contexto de negócio](../context/business-context.md) | [Outcome card](../functional/outcome-card.md), [repositórios de produto](../implementation/product-repositories.md) e [Production readiness](../governance/production-readiness.md) | Valor, progresso real, risco e condições para evolução |
| Arquiteto | [Arquitetura funcional](../functional/index.md) | [Estado de implementação](../architecture/implementation-status.md), [arquitetura técnica](../architecture/index.md), [ADRs](../decisions/index.md), [walkthrough](../tutorials/dispute-walkthrough.md) e [NFRs](../functional/non-functional-requirements.md) | Limites, responsabilidades, trade-offs e evidências |
| Desenvolvedor | [Repositórios de produto](../implementation/product-repositories.md) | [Walkthrough executável](../tutorials/dispute-walkthrough.md), [implementação](../implementation/index.md), [contratos](../contracts/index.md), [ADRs](../decisions/index.md) e [runbook](../implementation/runbook.md) | Onde implementar, como executar e como validar conformidade |
| Segurança | [Trust boundaries](../architecture/trust-boundaries.md) | [ADRs de controle](../decisions/index.md), [Identidade de workload](../security/workload-identity.md), [policies](../contracts/policies.md) e [supply chain](../security/supply-chain.md) | Controles, confiança e riscos residuais |
| Operações ou SRE | [Estado de implementação](../architecture/implementation-status.md) | [Deployment distribuído](../architecture/deployment-distributed-baseline.md), [observabilidade](../operations/observability.md), [SLOs](../operations/slos.md), [event backbone](../operations/eventing.md) e [runbooks](../operations/index.md) | Operação, diagnóstico, gaps de produto e recuperação |
| Auditoria ou compliance | [Lifecycle](../functional/case-lifecycle.md) | [Walkthrough](../tutorials/dispute-walkthrough.md), [papéis](../functional/roles-and-responsibilities.md), [ADRs](../decisions/index.md), [rastreabilidade](../functional/traceability-matrix.md) e [evidências](../governance/production-readiness.md) | Segregação, decisões e cadeia de evidências |

## Sequência recomendada para leitura completa

1. [Contexto de negócio](../context/business-context.md)
2. [Case aplicado](../case-study/index.md)
3. [Outcome card](../functional/outcome-card.md)
4. [Mapa de capacidades](../functional/capability-map.md)
5. [Lifecycle do caso](../functional/case-lifecycle.md)
6. [Estado de implementação](../architecture/implementation-status.md)
7. [Repositórios de implementação do produto](../implementation/product-repositories.md)
8. [Arquitetura técnica](../architecture/index.md)
9. [Architecture Decision Records](../decisions/index.md)
10. [Contratos executáveis](../contracts/index.md)
11. [Walkthrough executável](../tutorials/dispute-walkthrough.md)
12. [Implementação de referência](../implementation/index.md)
13. [Segurança e operações](../security/index.md)
14. [Production readiness](../governance/production-readiness.md)

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

Código isolado em frontend ou backend sustenta `IMPLEMENTATION_STARTED`. Para sustentar `VALIDATED_INTEGRATION`, a evidência precisa envolver os componentes relevantes executados juntos.

A [matriz de rastreabilidade](../functional/traceability-matrix.md) conecta necessidades, capacidades, regras, estados, contratos, eventos, policies e evidências. Os [ADRs](../decisions/index.md) registram os trade-offs e as condições que sustentam essas escolhas.
