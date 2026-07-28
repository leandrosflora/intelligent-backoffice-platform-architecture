# Estado de implementação — atual × alvo

Esta página distingue a baseline arquitetural executável, os repositórios de produto que começam a ser implementados, a integração validada e os requisitos ainda pendentes para produção.

## Vocabulário de estado

| Estado | Significado |
|---|---|
| `TARGET_DEFINED` | Responsabilidade, topologia ou controle definido como alvo, sem implementação confirmada no produto |
| `CONTRACT_DEFINED` | API, evento, schema, policy ou configuração versionada e validada, mas sem integração de produto comprovada |
| `IMPLEMENTATION_STARTED` | Código ou configuração já existe em um repositório de produto, mas a integração E2E e os gates operacionais ainda não foram comprovados |
| `DEMONSTRATED_LOCAL` | Capacidade executada na baseline de referência ou no CI com dados e integrações sintéticos |
| `VALIDATED_INTEGRATION` | Capacidade validada de ponta a ponta entre os componentes de produto em ambiente controlado |
| `PASSED_PRODUCTION` | Capacidade aprovada para produção com evidência atual, owner, operação, segurança e SLOs |

Uma mesma capacidade pode estar `DEMONSTRATED_LOCAL` na baseline e apenas `IMPLEMENTATION_STARTED` no produto. Esses estados não são intercambiáveis.

O status agregado permanece **`NOT_PRODUCTION_READY`**.

## Trilhas de entrega

| Trilha | Repositório | Estado | Evidência principal |
|---|---|---|---|
| Arquitetura e baseline | `intelligent-backoffice-platform-architecture` | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` | FastAPI, contracts-as-code, OPA, eventing, observabilidade, evals, readiness e walkthrough |
| Backend de produto | `backoffice-platform-api` | `IMPLEMENTATION_STARTED` | API .NET, domínio, PostgreSQL, OPA externo, execução mock e reconciliação |
| Frontend de produto | `intelligent-backoffice-frontend` | `IMPLEMENTATION_STARTED` | React, jornada guiada, integração HTTP, testes, build e imagem Nginx |
| Integração de produto | Frontend + API + PostgreSQL + OPA | Pendente | Ainda não existe gate E2E cross-repo automatizado |

## Matriz de capacidades

| Capacidade | Baseline de referência | Implementação de produto | Arquitetura-alvo | Gap principal |
|---|---|---|---|---|
| Intake e gestão de casos | `DEMONSTRATED_LOCAL`: FastAPI, idempotência de criação, versionamento otimista e timeline | `IMPLEMENTATION_STARTED`: API .NET e telas React para criar, listar, consultar e cancelar casos | Case Intake API e Case Management governados | E2E cross-repo, IAM, migrations operacionais, SLOs e integração com canais reais |
| Workflow persistente | `DEMONSTRATED_LOCAL`: lifecycle em SQLite, timers e workers | `IMPLEMENTATION_STARTED`: aggregate .NET controla transições e timeline; frontend guia ações pelo estado | Workflow Orchestrator de longa duração | Timers e workers de produto, HA, recovery e concorrência representativa |
| Document Intelligence | `DEMONSTRATED_LOCAL`: classificação determinística e evidências sintéticas | `IMPLEMENTATION_STARTED`: registro, validação e evidências no backend; formulário documental no frontend | Workers assíncronos, quarentena, OCR e modelos aprovados | Upload real, object store, malware scanning real, OCR, dataset e qualidade representativa |
| Investigação assistida | `DEMONSTRATED_LOCAL`: findings determinísticos grounded | `IMPLEMENTATION_STARTED`: handler de investigação e interface de acionamento | Investigation Agent Runtime com tools governadas | Tool Gateway real, fontes corporativas, modelo e evals representativos |
| Recomendação de decisão | `DEMONSTRATED_LOCAL`: recomendação determinística e abstention | `IMPLEMENTATION_STARTED`: recomendação grounded no backend e avanço da jornada no frontend | Decision Support Agent com RAG e Model Gateway | Consulta de recomendações, modelos reais, conhecimento aprovado e versionamento operacional |
| Aprovação humana | `DEMONSTRATED_LOCAL`: endpoint, alçada e segregação verificadas pelo OPA | `IMPLEMENTATION_STARTED`: aprovação .NET e formulário React com `X-Authority-Limit` | Human Approval Service e Task UI | Recuperação de aprovações, identidade corporativa, delegação, filas e UX de exceções |
| Policy Decision Point | `DEMONSTRATED_LOCAL`: OPA, `default deny`, purpose binding e testes negativos | `IMPLEMENTATION_STARTED`: API chama OPA externo com tenant, papéis, alçada e obrigações | PDP corporativo altamente disponível | Compose integrado, lifecycle de policies, HA, auditoria e gestão de mudanças |
| Execução governada | `DEMONSTRATED_LOCAL`: execução mock idempotente e reconciliação ambígua | `IMPLEMENTATION_STARTED`: gateway mock .NET, idempotência, consulta e reconciliação; frontend cobre sucesso, falha e ambiguidade | Serviço de execução com adapters para sistemas de registro | Integrações reais, reconciliação financeira, compensação e segregação operacional |
| Event backbone | `DEMONSTRATED_LOCAL`: Redpanda, outbox, inbox, retry, DLQ e replay | `TARGET_DEFINED`: ainda não incorporado ao backend de produto | Kafka multi-broker com governança corporativa | Outbox de produto, broker, consumers, schemas, ACLs, retenção, capacidade e DR |
| Identidade | `DEMONSTRATED_LOCAL`: JWT EdDSA local com tenant, papéis e finalidade | `IMPLEMENTATION_STARTED`: headers de desenvolvimento simulados pelo frontend e lidos pela API | IAM corporativo ou SPIFFE, mTLS e workload identity | Tokens assinados, federação, rotação, revogação, secrets manager e trust domain |
| Observabilidade | `DEMONSTRATED_LOCAL`: OpenTelemetry, Prometheus, Grafana, Jaeger, SLOs e alertas | `TARGET_DEFINED`: frontend registra chamadas localmente; backend de produto ainda não expõe stack operacional completa | Stack corporativa de logs, métricas e traces | Instrumentação E2E, correlação cross-repo, retenção, incidentes e on-call |
| Evals | `DEMONSTRATED_LOCAL`: dataset versionado para classificação, grounding e abstention | `TARGET_DEFINED`: ainda não conectado a modelos ou dados do produto | Avaliação contínua com dados representativos e modelos reais | Golden dataset, métricas de negócio, drift e revisão humana |
| Supply chain | `DEMONSTRATED_LOCAL`: runtime non-root, SBOM e proveniência | `IMPLEMENTATION_STARTED`: frontend possui lint, testes, build e imagem no CI; backend ainda precisa de pipeline equivalente confirmado | Imagens assinadas por digest com verificação em admission | CI do backend, registry, assinatura, attestations e policy de admission |
| Backup e restore | `DEMONSTRATED_LOCAL`: backup sintético criptografado e restore | `TARGET_DEFINED`: PostgreSQL existe no produto, sem drill integrado comprovado | PITR em banco gerenciado e recuperação de evidências | Backup real, restore recorrente, retenção e evidência operacional |
| Disaster recovery | `TARGET_DEFINED`: plano, RTO/RPO e critérios de exercício | `TARGET_DEFINED` | Recuperação regional com dependências e dados replicados | Aprovação de RTO/RPO e exercício regional concluído |
| Capacidade | `DEMONSTRATED_LOCAL`: teste sintético com threshold | `TARGET_DEFINED`: sem teste conjunto frontend/API/PostgreSQL/OPA | Load, soak e failure testing representativos | Volumetria, concorrência, custos e limites aprovados |
| Contratos e rastreabilidade | `CONTRACT_DEFINED`: OpenAPI, AsyncAPI, schemas, catálogo, policies e matriz | `IMPLEMENTATION_STARTED`: backend e frontend implementam parte dos contratos da jornada | Governança contínua de contratos entre equipes e ambientes | OpenAPI publicada pelo backend, teste de compatibilidade e gestão de depreciação |

## Fontes de evidência

- [Repositórios de implementação do produto](../implementation/product-repositories.md)
- [C4 contexto atual](c4-context-current.md)
- [C4 containers atuais](c4-container-current.md)
- [Deployment observado](deployment-observed-baseline.md)
- [Deployment distribuído](deployment-distributed-baseline.md)
- [Implementação de referência](../implementation/index.md)
- [Avaliação das capacidades inteligentes](../evaluation/index.md)
- [Production readiness](../governance/production-readiness.md)
- `governance/production-readiness.yaml`

## Regra de promoção

`IMPLEMENTATION_STARTED` só avança para `VALIDATED_INTEGRATION` quando existe uma execução reproduzível envolvendo os componentes de produto relevantes, com contratos compatíveis, testes positivos e negativos, evidências, observabilidade, owner e runbook.

Uma capacidade não deve avançar de estado apenas porque possui código ou configuração. A promoção exige evidência compatível com o novo nível, owner técnico e funcional, segurança e aprovação formal quando aplicável.
