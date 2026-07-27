# Event backbone e workflow distribuído

## Garantias demonstradas

| Capacidade | Baseline executável |
|---|---|
| Publicação atômica | Estado, timeline e outbox no mesmo commit SQLite |
| Entrega | At least once |
| Ordenação | Chave `caseId` dentro da partição |
| Deduplicação | Inbox `(consumerName, eventId)` |
| Retry | Até três tentativas com backoff exponencial |
| DLQ | Registro durável e tópico `backoffice.dlq.v1` |
| Replay | Novo `eventId`, referência `replayOf`, motivo e ator auditados |
| Timers | Agenda durável e worker dedicado |

## Profile distribuído

```bash
docker compose --profile distributed up --build
```

- API distribuída: `http://localhost:8081`
- Kafka externo: `localhost:19092`
- OPA: `http://localhost:8181`

## Semântica

A API não publica diretamente no broker. Cada evento de timeline gera uma linha no outbox por trigger transacional. O publisher confirma a mensagem no broker antes de marcar `PUBLISHED`.

O worker só confirma o offset após uma destas condições:

1. processamento e inbox concluídos;
2. evento duplicado identificado;
3. falha registrada de forma durável na DLQ.

## Replay

Replay não altera a dead letter original e não reutiliza o `eventId`. O novo envelope contém `replayOf` e `replayCount`. A operação exige papel `platform-operator`, finalidade `OPERATIONS` e justificativa registrada.