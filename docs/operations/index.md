# Operações

A baseline cobre diagnóstico de API, policies, inteligência determinística e processamento assíncrono.

## Capacidades implementadas

- métricas e traces;
- SLOs e alertas versionados;
- transactional outbox;
- inbox idempotente;
- backlog e estados de publicação;
- timers duráveis;
- retries com backoff;
- dead letter durável;
- replay explícito e auditado;
- evidência E2E publicada pelo CI.

## Princípios

- não usar identificadores de caso ou tenant como labels Prometheus;
- não confirmar offset antes de processamento, deduplicação ou DLQ durável;
- não apagar a dead letter após replay;
- não reutilizar o `eventId` original;
- não realizar replay sem causa corrigida e justificativa;
- não corrigir timers alterando diretamente o estado do caso.
