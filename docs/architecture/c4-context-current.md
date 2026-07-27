# C4 — Contexto atual

O estado atual é uma **implementação de referência local e executável** para a jornada sintética de contestação. Ela demonstra workflow persistente, capacidades inteligentes determinísticas, aprovação humana, policies, execução mock, eventing, observabilidade e geração de evidências no CI.

[![C4 contexto atual](../assets/diagrams/c4-context-current.png)](../assets/diagrams/c4-context-current.svg)

[**Abrir diagrama em SVG**](../assets/diagrams/c4-context-current.svg)

## Pessoas e interações

- o **analista de operações** cria casos, registra documentos, executa investigação e consulta a timeline;
- o **aprovador** registra decisões humanas sujeitas a alçada e segregação de funções;
- o **operador da plataforma** executa os profiles, observa telemetria e opera reconciliação, DLQ, replay e drills;
- o **arquiteto ou mantenedor** evolui código, contratos, policies, diagramas e evidências;
- o **GitHub Actions** constrói e valida ambientes efêmeros e publica a documentação.

## Estado confirmado

A implementação possui quatro profiles:

| Profile | Objetivo |
|---|---|
| `runtime` | Jornada síncrona mínima com FastAPI, SQLite e OPA |
| `observability` | Runtime com métricas, traces, dashboards, SLOs e alertas |
| `distributed` | Event backbone, outbox, inbox, workers, timers, DLQ e replay |
| `secure` | Identidade JWT EdDSA de curta duração e purpose binding |

## Limites

!!! danger "Não representa produção"
    O ambiente usa dados e integrações sintéticos, execução financeira mock, bancos SQLite e broker single-node. Não há integração com IAM, sistemas de registro, banco gerenciado, Kafka Multi-AZ ou operação 24x7 corporativos.

O status oficial permanece **`NOT_PRODUCTION_READY`**.

Consulte também a [matriz de implementação atual × alvo](implementation-status.md).

**Fonte PlantUML:** `C4/c4-context-current.puml`.
