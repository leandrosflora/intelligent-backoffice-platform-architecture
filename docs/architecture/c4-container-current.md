# C4 — Containers atuais

O nível de containers atual representa os processos, stores e ferramentas que podem ser executados hoje no ambiente de referência. Os profiles compartilham o mesmo código-base, mas ativam topologias diferentes para demonstrar capacidades específicas.

[![C4 containers atuais](../assets/diagrams/c4-container-current.png)](../assets/diagrams/c4-container-current.svg)

[**Abrir diagrama em SVG**](../assets/diagrams/c4-container-current.svg)

## Profiles de API

| Container | Profile | Responsabilidade |
|---|---|---|
| Reference API | `runtime`, `observability` | Lifecycle, documentos determinísticos, investigação, recomendação, aprovação, execução mock e timeline |
| Secure API | `secure` | Mesmo domínio com identidade JWT EdDSA e validação de claims |
| Distributed API | `distributed` | Mesmo domínio com transactional outbox, eventing e operações de DLQ e replay |

Os três containers são alternativas de execução do mesmo código-base. Eles não representam três serviços produtivos independentes.

## Policy e persistência

| Container | Estado atual |
|---|---|
| Policy Decision Point | OPA externo com `default deny`, alçada, segregação, purpose binding e testes negativos |
| Profile-local State Stores | SQLite persistido em volumes separados para os profiles runtime, secure e distributed |

## Eventing distribuído

- Redpanda single-node compatível com Kafka;
- Outbox Publisher;
- Workflow Worker com inbox idempotente;
- Timer Worker;
- retries com backoff;
- dead letter durável;
- replay autorizado e auditado.

## Observabilidade

- OpenTelemetry Collector;
- Prometheus;
- Grafana;
- Jaeger;
- SLOs, recording rules e alertas versionados.

## Toolchain e evidências

A toolchain Python/Bash executa testes E2E, evals, validações de contratos e policies, teste de capacidade, backup/restore, geração de SBOM e proveniência. O GitHub Actions executa essa toolchain em ambientes efêmeros e publica os artefatos resultantes.

!!! warning "Limite arquitetural"
    A baseline comprova padrões em ambiente local e CI. Ela não comprova HA, operação multi-AZ, integração corporativa, segurança de rede real, retenção operacional ou suporte 24x7.

Consulte também a [matriz de implementação atual × alvo](implementation-status.md).

**Fonte PlantUML:** `C4/c4-container-current.puml`.
