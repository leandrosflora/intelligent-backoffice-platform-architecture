# Eventos

Os eventos seguem AsyncAPI 3.0 e endereços versionados com sufixo `.v1`.

## Eventos canônicos

| Contract ID | Address | Significado |
|---|---|---|
| `EVT-CASE-001` | `backoffice.case.created.v1` | Caso registrado |
| `EVT-DOC-001` | `backoffice.document.received.v1` | Documento recebido em quarentena |
| `EVT-DOC-002` | `backoffice.document.validated.v1` | Documento validado ou rejeitado |
| `EVT-EVIDENCE-001` | `backoffice.evidence.missing.v1` | Evidência obrigatória ausente |
| `EVT-INV-001` | `backoffice.investigation.completed.v1` | Investigação concluída |
| `EVT-REC-001` | `backoffice.decision.proposed.v1` | Recomendação criada |
| `EVT-APPROVAL-001` | `backoffice.approval.requested.v1` | Tarefa humana criada |
| `EVT-APPROVAL-002` | `backoffice.decision.approved.v1` | Decisão aprovada |
| `EVT-APPROVAL-003` | `backoffice.decision.rejected.v1` | Decisão rejeitada |
| `EVT-EXEC-001` | `backoffice.execution.requested.v1` | Execução solicitada |
| `EVT-EXEC-002` | `backoffice.execution.completed.v1` | Execução confirmada |
| `EVT-EXEC-003` | `backoffice.execution.failed.v1` | Falha determinada de execução |
| `EVT-RECON-001` | `backoffice.reconciliation.required.v1` | Resultado ambíguo |
| `EVT-CASE-002` | `backoffice.case.closed.v1` | Caso encerrado |

## Envelope

Todo evento exige:

```text
eventId, eventType, eventVersion, occurredAt,
tenantId, caseId, caseVersion,
correlationId, causationId, traceId,
producer, dataClassification, payload
```

## Regras operacionais

- entrega ao menos uma vez;
- consumidor idempotente;
- `eventId` usado para deduplicação;
- `correlationId` conecta a jornada;
- `causationId` identifica o comando ou evento anterior;
- breaking changes criam novo endereço versionado;
- documentos integrais nunca são copiados para eventos.
