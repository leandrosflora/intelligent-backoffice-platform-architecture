# Runbook — execução ambígua ou conflito de idempotência

## Trigger

- `BackofficeReconciliationRequired`;
- `BackofficeIdempotencyConflictSpike`;
- estado `RECONCILIATION_REQUIRED`;
- execução com status `RECONCILIATION_REQUIRED`.

## Diagnóstico

1. Localize o caso, o `executionId` e a chave de idempotência na timeline.
2. Compare o hash do comando com tentativas anteriores.
3. Consulte a execução:

   ```text
   GET /v1/cases/{caseId}/executions/{executionId}
   ```

4. Consulte o sistema de registro ou mock de execução.
5. Classifique o efeito como aplicado, não aplicado ou ainda inconclusivo.

## Mitigação

- bloqueie retry automático enquanto o resultado for inconclusivo;
- não envie um novo comando financeiro para “testar” o resultado;
- mantenha a chave original somente para replay idempotente da mesma execução;
- direcione o caso ao papel `reconciler`;
- preserve as evidências usadas para determinar o resultado.

## Resolver a reconciliação

Use:

```text
POST /v1/cases/{caseId}/reconciliations/{executionId}/resolve
```

Headers obrigatórios:

```text
If-Match: <versão atual do caso>
Idempotency-Key: <chave específica da reconciliação>
X-Roles: reconciler
```

Corpo:

```json
{
  "case_version": 6,
  "resolution": "CONFIRMED_SUCCEEDED",
  "reason": "system of record confirms the operation completed successfully"
}
```

Resoluções permitidas:

| Resolução | Caso | Execução |
|---|---|---|
| `CONFIRMED_SUCCEEDED` | `EXECUTED` | `RECONCILED` |
| `CONFIRMED_FAILED` | `FAILED` | `RECONCILED` |
| `ESCALATED` | `RECONCILIATION_REQUIRED` | `RECONCILIATION_REQUIRED` |

A repetição da mesma resolução com a mesma chave retorna o resultado anterior. A reutilização da chave com conteúdo diferente retorna `409 Conflict`.

## Encerramento

Confirme que:

- a timeline contém o evento de reconciliação;
- a execução contém o status e a resolução finais;
- o outbox publicou o evento;
- a projeção do consumer processou o evento;
- ator, motivo e correlação estão registrados.

O [walkthrough executável](../../tutorials/dispute-walkthrough.md) demonstra esse fluxo ponta a ponta com dados sintéticos.
