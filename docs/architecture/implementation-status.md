# Estado de implementação — atual × alvo

Esta página é a referência resumida para distinguir capacidades demonstradas, contratos definidos, arquitetura-alvo e requisitos ainda pendentes para produção.

## Vocabulário de estado

| Estado | Significado |
|---|---|
| `TARGET_DEFINED` | Responsabilidade, topologia ou controle definido como alvo, sem evidência de execução no ambiente real |
| `CONTRACT_DEFINED` | API, evento, schema, policy ou configuração versionada e validada, mas sem integração produtiva comprovada |
| `DEMONSTRATED_LOCAL` | Capacidade executada no ambiente de referência ou no CI com dados e integrações sintéticos |
| `VALIDATED_INTEGRATION` | Capacidade validada contra serviços e integrações reais em ambiente controlado |
| `PASSED_PRODUCTION` | Capacidade aprovada para produção com evidência atual, owner, operação, segurança e SLOs |

O repositório possui principalmente evidências `DEMONSTRATED_LOCAL`, contratos `CONTRACT_DEFINED` e controles `TARGET_DEFINED`. O status agregado permanece **`NOT_PRODUCTION_READY`**.

## Matriz de capacidades

| Capacidade | Estado atual | Baseline confirmada | Arquitetura-alvo | Gap principal |
|---|---|---|---|---|
| Intake e gestão de casos | `DEMONSTRATED_LOCAL` | FastAPI, idempotência de criação, versionamento otimista e timeline | Case Intake API e Case Management desacoplados | Canal corporativo, IAM, persistência gerenciada e operação real |
| Workflow persistente | `DEMONSTRATED_LOCAL` | Lifecycle em SQLite, timers e workers no profile distribuído | Workflow Orchestrator de longa duração | HA, banco corporativo, escalabilidade e recovery testado |
| Document Intelligence | `DEMONSTRATED_LOCAL` | Classificação determinística e evidências sintéticas | Workers assíncronos, quarentena, OCR e modelos aprovados | Documentos reais autorizados, object store, dataset e avaliação de qualidade |
| Investigação assistida | `DEMONSTRATED_LOCAL` | Finding determinístico grounded em referências de evidência | Investigation Agent Runtime com tools governadas | Tool Gateway real, fontes corporativas, modelo e evals representativos |
| Recomendação de decisão | `DEMONSTRATED_LOCAL` | Recomendação determinística com `ABSTAIN` quando não há grounding | Decision Support Agent com RAG e Model Gateway | Modelos reais, conhecimento aprovado, avaliação e controle de versões |
| Aprovação humana | `DEMONSTRATED_LOCAL` | Endpoint de aprovação, alçada e segregação verificadas pelo OPA | Human Approval Service e Task UI | UI, identidade corporativa, delegação, filas e regras aprovadas pelo processo |
| Policy Decision Point | `DEMONSTRATED_LOCAL` | OPA externo, `default deny`, purpose binding e testes negativos | PDP corporativo altamente disponível | Distribuição e lifecycle de policies, HA, auditoria e gestão de mudanças |
| Execução governada | `DEMONSTRATED_LOCAL` | Execução mock idempotente e caminho de reconciliação ambígua | Serviço de execução com adapters para sistemas de registro | Integrações reais, reconciliação financeira, compensação e segregação operacional |
| Event backbone | `DEMONSTRATED_LOCAL` | Redpanda single-node, outbox, inbox, retry, DLQ e replay | Kafka multi-broker com governança corporativa | Replicação, ACLs, schema registry, retenção, capacidade e DR |
| Identidade | `DEMONSTRATED_LOCAL` | JWT EdDSA local com issuer, audience, TTL, tenant, papéis e finalidade | IAM corporativo ou SPIFFE, mTLS e workload identity | Federação real, rotação, revogação, secrets manager e trust domain corporativo |
| Observabilidade | `DEMONSTRATED_LOCAL` | OpenTelemetry, Prometheus, Grafana, Jaeger, SLOs e alertas | Stack corporativa de logs, métricas e traces | Autenticação, retenção, integração com incidentes, on-call e operação 24x7 |
| Evals | `DEMONSTRATED_LOCAL` | Dataset versionado para classificação, grounding e abstention | Avaliação contínua com dados representativos e modelos reais | Golden dataset aprovado, métricas de negócio, drift e revisão humana |
| Supply chain | `DEMONSTRATED_LOCAL` | Runtime non-root, SBOM CycloneDX e proveniência gerada | Imagens assinadas por digest com verificação em admission | Registry corporativo, assinatura, attestations verificadas e policy de admission |
| Backup e restore | `DEMONSTRATED_LOCAL` | Backup sintético criptografado e restore com integridade | PITR em banco gerenciado e recuperação de evidências | Backup real, testes recorrentes, retenção e evidência operacional |
| Disaster recovery | `TARGET_DEFINED` | Plano, RTO/RPO propostos e critérios de exercício | Recuperação regional com dependências e dados replicados | Aprovação de RTO/RPO e exercício regional concluído |
| Capacidade | `DEMONSTRATED_LOCAL` | Teste sintético com threshold versionado | Load, soak e failure testing representativos | Volumetria real, concorrência, custos e limites operacionais aprovados |
| Contratos e rastreabilidade | `CONTRACT_DEFINED` | OpenAPI, AsyncAPI, JSON Schemas, catálogo, policies e matriz de rastreabilidade | Governança contínua de contratos entre equipes e ambientes | Owners formais, compatibilidade em integrações reais e gestão de depreciação |

## Fontes de evidência

- [C4 contexto atual](c4-context-current.md)
- [C4 containers atuais](c4-container-current.md)
- [Deployment observado](deployment-observed-baseline.md)
- [Deployment distribuído](deployment-distributed-baseline.md)
- [Implementação de referência](../implementation/index.md)
- [Avaliação das capacidades inteligentes](../evaluation/index.md)
- [Production readiness](../governance/production-readiness.md)
- `governance/production-readiness.yaml`

## Regra de promoção

Uma capacidade não deve avançar de estado apenas porque possui código ou configuração. A promoção exige evidência compatível com o novo nível, owner técnico e funcional, testes positivos e negativos, observabilidade, runbook, segurança e aprovação formal quando aplicável.
