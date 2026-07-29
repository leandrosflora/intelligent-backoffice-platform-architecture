# HTTP APIs

O contrato OpenAPI 3.1 cobre o lifecycle planejado do primeiro vertical slice.

## Operações

| Contract ID | Método e rota | Policy action | Responsabilidade |
|---|---|---|---|
| `API-PLATFORM-001` | `GET /health` | `public.health` | Health check público |
| `API-CASE-001` | `POST /v1/cases` | `case.create` | Criar caso idempotente |
| `API-CASE-002` | `GET /v1/cases/{caseId}` | `case.read` | Consultar caso |
| `API-CASE-003` | `POST /v1/cases/{caseId}/cancel` | `case.cancel` | Cancelar caso elegível |
| `API-DOC-001` | `POST /v1/cases/{caseId}/documents` | `document.register` | Registrar documento em quarentena |
| `API-DOC-002` | `GET /v1/cases/{caseId}/documents/{documentId}` | `document.read` | Consultar metadados do documento |
| `API-EVIDENCE-001` | `GET /v1/cases/{caseId}/evidence` | `evidence.read` | Consultar evidências minimizadas |
| `API-INV-001` | `POST /v1/cases/{caseId}/investigations` | `investigation.execute` | Iniciar investigação |
| `API-REC-001` | `POST /v1/cases/{caseId}/recommendations` | `recommendation.create` | Criar recomendação versionada |
| `API-REC-002` | `GET /v1/cases/{caseId}/recommendations` | `case.read` | Consultar histórico de recomendações |
| `API-APPROVAL-001` | `POST /v1/cases/{caseId}/approvals` | `approval.decide` | Registrar decisão humana |
| `API-APPROVAL-002` | `GET /v1/cases/{caseId}/approvals` | `case.read` | Consultar histórico de decisões |
| `API-EXEC-001` | `POST /v1/cases/{caseId}/executions` | `execution.request` | Solicitar execução governada |
| `API-EXEC-002` | `GET /v1/cases/{caseId}/executions/{executionId}` | `execution.read` | Consultar execução |
| `API-RECON-001` | `POST /v1/cases/{caseId}/reconciliations/{executionId}/resolve` | `reconciliation.resolve` | Resolver resultado ambíguo |
| `API-AUDIT-001` | `GET /v1/cases/{caseId}/timeline` | `audit.read` | Consultar timeline auditável |

## Headers obrigatórios

Operações protegidas usam:

- `Authorization` com token de usuário ou workload;
- `X-Tenant-Id`, validado contra o tenant assinado;
- `X-Correlation-Id` para rastreabilidade.

Mutações também usam `Idempotency-Key`. Transições sobre caso existente usam `If-Match` com a versão esperada.

## Conflitos

`409 Conflict` cobre:

- chave idempotente reutilizada com payload diferente;
- versão obsoleta do caso;
- transição incompatível com o estado atual;
- recomendação ou aprovação substituída.
