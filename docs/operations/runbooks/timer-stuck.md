# Runbook — Timer atrasado ou parado

## Sinais

- timer `SCHEDULED` com `due_at` no passado;
- timer `IN_FLIGHT` por mais de dois minutos;
- casos aguardando expiração sem transição.

## Diagnóstico e recuperação

1. verifique o container `timer-worker`;
2. inspecione `attempts` e `last_error`;
3. confirme acesso ao SQLite compartilhado;
4. valide se o caso ainda não está em estado terminal;
5. reinicie o worker se necessário;
6. confirme geração de `backoffice.timer.fired.v1` no outbox.

Não altere diretamente o estado do caso para compensar um timer sem registrar evidência operacional.
