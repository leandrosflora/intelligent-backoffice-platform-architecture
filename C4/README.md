# C4

Esta pasta contém as fontes PlantUML canônicas da arquitetura.

## Visões

### Contexto e containers

- `c4-context-current.puml`
- `c4-context-target.puml`
- `c4-container-current.puml`
- `c4-container-target.puml`

### Componentes e deployments

- `c4-component-workflow-orchestrator.puml`
- `c4-component-document-intelligence.puml`
- `c4-deployment-local.puml`
- `c4-deployment-observed-baseline.puml`
- `c4-deployment-distributed-baseline.puml`
- `c4-trust-boundaries.puml`

### Sequências

- `sequence-case-intake.puml`
- `sequence-investigation-approval.puml`
- `sequence-governed-execution.puml`
- `sequence-missing-evidence.puml`
- `sequence-outbox-delivery.puml`
- `sequence-retry-dlq-replay.puml`

## Regra de leitura

- **atual:** confirmado no repositório;
- **alvo:** responsabilidade ou integração planejada;
- **baseline executável:** capacidade comprovada em CI;
- **produção:** controles operacionais aprovados e integração real.

A baseline distribuída P6 não implica prontidão produtiva.
