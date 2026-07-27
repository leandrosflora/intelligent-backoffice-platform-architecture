# Matriz de rastreabilidade

| Necessidade | Capacidade | Regras | Estados principais | Contratos HTTP | Eventos | Policies | Evidência esperada |
|---|---|---|---|---|---|---|---|
| Registrar caso sem duplicidade | CAP-001, PLT-001 | BR-001, BR-024 | `CREATED` | `API-CASE-001`, `API-CASE-002` | `EVT-CASE-001` | `POL-CASE-001`, `POL-CASE-002` | comando, chave externa, idempotency key e evento |
| Garantir documentação mínima | CAP-002, PLT-003 | BR-002 a BR-005 | `AWAITING_DOCUMENTS`, `DOCUMENTS_VALIDATED` | `API-DOC-001`, `API-DOC-002` | `EVT-DOC-001`, `EVT-DOC-002`, `EVT-EVIDENCE-001` | `POL-DOC-001`, `POL-DOC-002` | checklist, checksum, status e evidências |
| Investigar com fontes autorizadas | CAP-004, PLT-005, PLT-006 | BR-006, BR-007 | `UNDER_INVESTIGATION` | `API-INV-001`, `API-EVIDENCE-001` | `EVT-INV-001` | `POL-INV-001`, `POL-EVIDENCE-001` | tool calls, findings e decisões de policy |
| Produzir recomendação explicável | CAP-005, PLT-002, PLT-004 | BR-008 a BR-010 | `DECISION_PROPOSED` | `API-REC-001` | `EVT-REC-001` | `POL-REC-001` | versão, regras, evidências e resultado de eval |
| Impedir autoaprovação | CAP-006, PLT-006, PLT-007 | BR-011 a BR-015 | `AWAITING_APPROVAL`, `APPROVED` | `API-APPROVAL-001` | `EVT-APPROVAL-001`, `EVT-APPROVAL-002`, `EVT-APPROVAL-003` | `POL-APPROVAL-001` | identidade, alçada, versão e decisão humana |
| Evitar execução duplicada | CAP-007, PLT-005 | BR-016 a BR-020 | `EXECUTION_PENDING`, `EXECUTED` | `API-EXEC-001`, `API-EXEC-002` | `EVT-EXEC-001`, `EVT-EXEC-002`, `EVT-EXEC-003` | `POL-EXEC-001`, `POL-EXEC-002` | idempotency key, command hash e resultado |
| Tratar resultado ambíguo | CAP-007, PLT-001 | BR-020 | `RECONCILIATION_REQUIRED` | `API-RECON-001` | `EVT-RECON-001` | `POL-RECON-001` | alerta, consulta de reconciliação e resolução |
| Encerrar ou cancelar com rastreabilidade | CAP-001, CAP-009, PLT-012 | BR-021, BR-023, BR-024 | `CLOSED`, `CANCELLED`, `EXPIRED` | `API-CASE-003`, `API-AUDIT-001` | `EVT-CASE-002` | `POL-CASE-003`, `POL-AUDIT-001` | timeline append-only, motivo e retenção |
| Medir valor e operação | CAP-010, PLT-011, PLT-013 | Outcome card | todos | `API-PLATFORM-001` | todos | decisões auditadas | baseline, dashboards e revisão de valor |

## Critério de implementação

Um requisito só pode ser considerado implementado quando possuir:

1. contrato versionado;
2. policy aplicável;
3. teste positivo e negativo;
4. owner técnico e funcional;
5. evidência observável;
6. runbook e SLO quando entrar em operação.

O catálogo `contracts/catalog.yaml` é validado contra OpenAPI, AsyncAPI e policies para impedir divergência silenciosa.
