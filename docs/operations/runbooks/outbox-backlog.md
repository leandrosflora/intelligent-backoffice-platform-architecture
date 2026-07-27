# Runbook — Backlog no outbox

## Sinais

- crescimento de `backoffice_outbox_messages{status="PENDING"}`;
- linhas em `IN_FLIGHT` há mais de dois minutos;
- publisher reiniciando ou sem conexão com o broker.

## Diagnóstico

1. confirme saúde do Redpanda;
2. valide o tópico `backoffice.events.v1`;
3. verifique logs do `outbox-publisher`;
4. inspecione `attempts`, `available_at` e `last_error`;
5. confirme espaço e locks do armazenamento.

## Ação

Restaure o broker ou publisher. Linhas `IN_FLIGHT` antigas retornam para `RETRY`. Não edite para `PUBLISHED` manualmente. Eventos em `DEAD_LETTER` exigem investigação e replay controlado.
