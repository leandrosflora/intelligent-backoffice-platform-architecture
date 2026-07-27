# Matriz de rastreabilidade

| Necessidade | Capacidade | Regras | Estados principais | Owner | Evidência esperada |
|---|---|---|---|---|---|
| Registrar caso sem duplicidade | CAP-001, PLT-001 | BR-001, BR-024 | `CREATED` | Case Manager | comando, chave externa e evento de criação |
| Garantir documentação mínima | CAP-002, PLT-003 | BR-002 a BR-005 | `AWAITING_DOCUMENTS`, `DOCUMENTS_VALIDATED` | Data Owner | checklist, extração, checksum e resultado de validação |
| Investigar com fontes autorizadas | CAP-004, PLT-005, PLT-006 | BR-006, BR-007 | `UNDER_INVESTIGATION` | Operations Analyst | tool calls, findings e decisões de policy |
| Produzir recomendação explicável | CAP-005, PLT-002, PLT-004 | BR-008 a BR-010 | `DECISION_PROPOSED` | Agent Owner | versão, regras, evidências e resultado de eval |
| Impedir autoaprovação | CAP-006, PLT-006, PLT-007 | BR-011 a BR-015 | `AWAITING_APPROVAL`, `APPROVED` | Human Approver | identidade, alçada e decisão de policy |
| Evitar execução duplicada | CAP-007, PLT-005 | BR-016 a BR-020 | `EXECUTION_PENDING`, `EXECUTED` | Execution Service Owner | idempotency key, command hash e resultado |
| Tratar resultado ambíguo | CAP-007, PLT-001 | BR-020 | `RECONCILIATION_REQUIRED` | Operations and SRE | alerta, consulta de reconciliação e resolução |
| Preservar auditoria | CAP-003, CAP-009, PLT-008, PLT-012 | BR-021 a BR-025 | todos | Compliance Owner | timeline append-only e evidências versionadas |
| Medir valor | CAP-010, PLT-011, PLT-013 | Outcome card | todos | Business Owner | baseline, dashboards e revisão de valor |

## Uso da matriz

A matriz deve evoluir para incluir identificadores de endpoints, eventos, policies, testes e dashboards. Um requisito só pode ser considerado implementado quando possuir contrato, teste, evidência, owner e operação definida.
