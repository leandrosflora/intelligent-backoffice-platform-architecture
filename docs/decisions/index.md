# Architecture Decision Records

Esta seção registra decisões arquiteturais estruturantes da Intelligent Backoffice Platform. Os ADRs explicam por que a arquitetura foi desenhada desta forma, quais alternativas foram consideradas e quais consequências devem ser preservadas durante a evolução.

## Convenção

- o identificador é imutável e segue `ADR-NNN`;
- decisões novas começam como `Proposto`;
- decisões aprovadas usam `Aceito`;
- uma decisão substituída permanece no histórico com status `Substituído por ADR-NNN`;
- mudanças relevantes devem atualizar o ADR ou criar uma nova decisão que o substitua;
- implementação local, arquitetura-alvo e produção não são tratados como estados equivalentes.

## Decisões aceitas

| ADR | Decisão | Escopo |
|---|---|---|
| [ADR-001](adr-001-modular-monolith-reference-implementation.md) | Implementação de referência como monólito modular | Baseline local |
| [ADR-002](adr-002-logical-distributed-target.md) | Arquitetura-alvo distribuída por responsabilidades lógicas | Target corporativo |
| [ADR-003](adr-003-workflow-owns-process-state.md) | Workflow como autoridade sobre estado e transições | Baseline e target |
| [ADR-004](adr-004-ai-investigates-and-recommends.md) | IA investiga e recomenda, mas não aprova nem executa | Baseline e target |
| [ADR-005](adr-005-opa-external-policy-decision-point.md) | OPA externo como Policy Decision Point com default deny | Baseline local |
| [ADR-006](adr-006-human-approval-and-segregation.md) | Aprovação humana e segregação de funções para decisões sensíveis | Baseline e target |
| [ADR-007](adr-007-governed-idempotent-execution.md) | Execução governada, idempotente e reconciliável | Baseline e target |
| [ADR-008](adr-008-outbox-inbox-at-least-once.md) | Outbox, inbox e entrega at least once | Baseline distribuída |
| [ADR-009](adr-009-evidence-and-append-only-audit.md) | Evidências versionadas e auditoria append-only | Baseline e target |
| [ADR-010](adr-010-signed-local-identity-to-corporate-workload-identity.md) | Identidade assinada local evoluindo para IAM ou SPIFFE | Baseline e target |
| [ADR-011](adr-011-local-sqlite-managed-storage-target.md) | SQLite apenas local e armazenamento gerenciado como target | Baseline e target |
| [ADR-012](adr-012-observability-and-evals-as-gates.md) | Observabilidade e evals como gates versionados | Baseline e target |
| [ADR-013](adr-013-architecture-and-contracts-as-code.md) | Arquitetura e contratos como código versionado | Governança |

## Estados permitidos

| Estado | Uso |
|---|---|
| `Proposto` | Em discussão e ainda não vinculante |
| `Aceito` | Decisão vigente |
| `Rejeitado` | Alternativa avaliada e não adotada |
| `Depreciado` | Ainda existente, mas não recomendado para novos usos |
| `Substituído por ADR-NNN` | Mantido apenas como histórico |

## Criar uma decisão

Use o [template de ADR](template.md), escolha o próximo número disponível e inclua links para diagramas, contratos, código, policies, testes ou evidências que sustentem a decisão.
