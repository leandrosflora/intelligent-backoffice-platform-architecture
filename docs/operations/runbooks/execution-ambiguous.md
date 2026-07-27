# Runbook — execução ambígua ou conflito de idempotência

## Trigger

- `BackofficeReconciliationRequired`;
- `BackofficeIdempotencyConflictSpike`;
- estado `RECONCILIATION_REQUIRED`.

## Diagnóstico

1. Localize o caso e a chave de idempotência na evidência de auditoria.
2. Compare o hash do comando com tentativas anteriores.
3. Consulte o sistema de registro ou mock de execução.
4. Confirme se existe efeito aplicado, não aplicado ou inconclusivo.

## Mitigação

- bloqueie retry automático enquanto o resultado for inconclusivo;
- direcione o caso para reconciliação humana;
- mantenha a mesma chave somente para replay do mesmo comando;
- use nova chave apenas após decisão explícita de compensação ou novo comando.

## Encerramento

Registre decisão, evidência consultada, ator responsável e resultado reconciliado na timeline.
