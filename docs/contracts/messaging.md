# Topologia de mensageria

O contrato operacional está em `contracts/messaging/topology.yaml`.

## Tópicos

| Tópico | Partições | Chave | Uso |
|---|---:|---|---|
| `backoffice.events.v1` | 3 | `caseId` | Eventos de domínio publicados pelo outbox |
| `backoffice.dlq.v1` | 1 | `caseId` | Referências de eventos que excederam o retry budget |

## Garantias

- entrega at least once;
- ordenação por agregado dentro da partição;
- inbox idempotente por consumer group e `eventId`;
- replay cria nova identidade e mantém referência ao evento original;
- offset só é confirmado depois de um resultado durável.

A API operacional complementar está em `contracts/openapi/eventing-operations-api.yaml`.