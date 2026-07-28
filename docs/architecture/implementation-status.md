# Estado de implementação — atual × alvo

Esta página distingue contratos, baseline arquitetural, componentes de produto demonstrados isoladamente, integração cross-repo e requisitos de produção.

## Vocabulário de estado

| Estado | Significado |
|---|---|
| `TARGET_DEFINED` | Responsabilidade, topologia ou controle definido como alvo, sem implementação confirmada |
| `CONTRACT_DEFINED` | API, evento, schema, policy ou configuração versionada, sem integração de produto comprovada |
| `IMPLEMENTATION_STARTED` | Código existe em um repositório de produto, mas os gates de demonstração ou integração ainda são incompletos |
| `DEMONSTRATED_LOCAL` | Capacidade executada localmente ou no CI com dados e dependências sintéticos |
| `VALIDATED_INTEGRATION` | Capacidade validada ponta a ponta entre componentes de produto em ambiente controlado |
| `PASSED_PRODUCTION` | Capacidade aprovada para produção com owner, segurança, operação, SLOs e evidência atual |

Uma mesma solução pode ter componentes `DEMONSTRATED_LOCAL` e continuar agregadamente em `IMPLEMENTATION_STARTED` enquanto a integração entre repositórios não estiver automatizada.

O status agregado permanece **`NOT_PRODUCTION_READY`**.

## Trilhas de entrega

| Trilha | Repositório | Estado | Evidência principal |
|---|---|---|---|
| Arquitetura e baseline | `intelligent-backoffice-platform-architecture` | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` | FastAPI, contracts-as-code, OPA, eventing, observabilidade, evals, readiness e walkthrough |
| Backend de produto | `backoffice-platform-api` | `IMPLEMENTATION_STARTED` com capacidades `DEMONSTRATED_LOCAL` | API .NET, PostgreSQL, OPA, JWT, workers, Redpanda, telemetria, evals e Kubernetes |
| Frontend de produto | `intelligent-backoffice-frontend` | `IMPLEMENTATION_STARTED` com componente `DEMONSTRATED_LOCAL` | React, jornada guiada, modos de identidade, testes, build e Nginx |
| Integração de produto | Frontend + API + PostgreSQL + OPA | Pendente | Execução manual documentada; sem gate E2E browser-based cross-repo |

## Matriz de capacidades

| Capacidade | Baseline de referência | Implementação de produto | Arquitetura-alvo | Gap principal |
|---|---|---|---|---|
| Intake e gestão de casos | `DEMONSTRATED_LOCAL`: FastAPI, idempotência, versionamento e timeline | `DEMONSTRATED_LOCAL`: API .NET e telas React para criar, listar, consultar e cancelar | Case Intake API e Case Management governados | E2E cross-repo, IAM, canais reais, SLOs e operação |
| Workflow persistente | `DEMONSTRATED_LOCAL`: lifecycle em SQLite, timers e workers | `DEMONSTRATED_LOCAL`: aggregate .NET, PostgreSQL, outbox, workers e timers | Workflow Orchestrator de longa duração | HA real, recovery, concorrência e operação multi-instância |
| Document Intelligence | `DEMONSTRATED_LOCAL`: classificação determinística e evidências sintéticas | `IMPLEMENTATION_STARTED`: registro, validação, evidências e formulário documental | Workers assíncronos, quarentena, OCR e modelos aprovados | Upload real, object store, malware scanning, OCR e dataset representativo |
| Investigação assistida | `DEMONSTRATED_LOCAL`: findings determinísticos grounded | `IMPLEMENTATION_STARTED`: handler .NET e acionamento pelo console | Investigation Agent Runtime com tools governadas | Tool Gateway, fontes corporativas, modelo e evals representativos |
| Recomendação de decisão | `DEMONSTRATED_LOCAL`: recomendação determinística e abstention | `IMPLEMENTATION_STARTED`: recomendação grounded e jornada React | Decision Support Agent com RAG e Model Gateway | Recuperação por caso, modelos reais, conhecimento aprovado e versionamento |
| Aprovação humana | `DEMONSTRATED_LOCAL`: alçada e segregação verificadas pelo OPA | `DEMONSTRATED_LOCAL`: aprovação .NET e formulário React com `X-Authority-Limit` | Human Approval Service e Task UI | Recuperação, identidade corporativa, delegação, filas e UX de exceção |
| Policy Decision Point | `DEMONSTRATED_LOCAL`: OPA, default deny, purpose binding e testes negativos | `DEMONSTRATED_LOCAL`: API consulta OPA externo com tenant, papéis, alçada e obrigações | PDP corporativo altamente disponível | Lifecycle de policies, HA, auditoria, distribuição e gestão de mudanças |
| Execução governada | `DEMONSTRATED_LOCAL`: execução mock idempotente e reconciliação | `DEMONSTRATED_LOCAL`: gateway mock .NET, consulta, idempotência e reconciliação; frontend cobre sucesso, falha e ambiguidade | Serviço de execução com adapters reais | Integrações financeiras, compensação, reconciliação e segregação operacional |
| Event backbone | `DEMONSTRATED_LOCAL`: Redpanda, outbox, inbox, retry, DLQ e replay | `DEMONSTRATED_LOCAL`: Redpanda, outbox dispatcher, workflow consumer, timer worker, DLQ e replay | Kafka multi-broker com governança corporativa | Schemas em registry, ACLs, retenção, capacidade, HA e DR |
| Identidade | `DEMONSTRATED_LOCAL`: JWT EdDSA com tenant, papéis e finalidade | `DEMONSTRATED_LOCAL`: headers para desenvolvimento e JWT EdDSA no profile seguro | IAM corporativo ou SPIFFE, mTLS e workload identity | Federação, rotação, revogação, KMS, sessão web e trust domain |
| Observabilidade | `DEMONSTRATED_LOCAL`: OTel, Prometheus, Grafana, Jaeger, SLOs e alertas | `DEMONSTRATED_LOCAL`: instrumentação .NET, métricas HTTP/domínio/eventing, health, readiness e profile observável | Stack corporativa de logs, métricas e traces | Correlação do browser aos workers, retenção, alertas com owner e on-call |
| Evals | `DEMONSTRATED_LOCAL`: datasets e thresholds versionados | `DEMONSTRATED_LOCAL`: harness .NET determinístico incorporado ao workflow de CI | Avaliação contínua com dados e modelos reais | Golden dataset de produto, métricas de negócio, drift e revisão humana |
| Supply chain | `DEMONSTRATED_LOCAL`: runtime non-root, SBOM e proveniência | `IMPLEMENTATION_STARTED`: pipelines, builds Docker e manifests Kubernetes | Imagens assinadas por digest e admission control | SBOM/assinatura do produto, registry, attestations e policy de admission |
| Backup e restore | `DEMONSTRATED_LOCAL`: backup sintético criptografado e restore | `TARGET_DEFINED`: PostgreSQL persistente, sem drill de produto comprovado | PITR em banco gerenciado e recuperação de evidências | Backup real, restore recorrente, retenção e evidência operacional |
| Disaster recovery | `TARGET_DEFINED`: plano, RTO/RPO e critérios | `TARGET_DEFINED`: manifests e PDB não equivalem a DR | Recuperação regional com dados e dependências replicados | RTO/RPO aprovados e exercício regional concluído |
| Capacidade | `DEMONSTRATED_LOCAL`: teste sintético com threshold | `IMPLEMENTATION_STARTED`: HPA e PDB definidos, sem teste conjunto de carga | Load, soak e failure testing representativos | Volumetria, concorrência, custos, limites e autoscaling comprovado |
| Contratos e rastreabilidade | `CONTRACT_DEFINED`: OpenAPI, AsyncAPI, schemas, policies e matriz | `DEMONSTRATED_LOCAL`: testes de OpenAPI, AsyncAPI e JSON Schemas; frontend implementa a jornada | Governança contínua de contratos | Publicação do OpenAPI gerado, compatibilidade cross-repo e depreciação |
| Deployment | `DEMONSTRATED_LOCAL`: profiles Docker da baseline | `IMPLEMENTATION_STARTED`: profiles Docker e manifests Kubernetes para API e workers | Plataforma gerenciada, multi-AZ e segura | Cluster real, secrets, ingress, storage, rollout, autoscaling e operação |

## Fontes de evidência

- [Repositórios de implementação do produto](../implementation/product-repositories.md)
- [Backend de produto](../implementation/backend-product.md)
- [Frontend operacional](../implementation/frontend-console.md)
- [Runtime integrado](../implementation/product-runtime.md)
- [C4 containers atuais](c4-container-current.md)
- [Implementação de referência](../implementation/index.md)
- [Production readiness](../governance/production-readiness.md)
- `governance/production-readiness.yaml`

## Regra de promoção

Uma capacidade só avança para `VALIDATED_INTEGRATION` quando existe execução reproduzível envolvendo os componentes de produto relevantes, contratos compatíveis, cenários positivos e negativos, evidências, observabilidade, owner e runbook.

Uma capacidade não avança apenas porque possui código, Compose ou manifests. A promoção exige evidência compatível com o nível, segurança, operação e aprovação formal quando aplicável.
