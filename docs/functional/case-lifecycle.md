# Lifecycle do caso

## Estados canônicos

| Estado | Significado | Responsável predominante |
|---|---|---|
| `CREATED` | Caso registrado e ainda não triado | Case Management |
| `AWAITING_DOCUMENTS` | Há documentos obrigatórios pendentes | Case Management |
| `DOCUMENTS_RECEIVED` | Documentos recebidos e aguardando processamento | Document Processing |
| `DOCUMENTS_VALIDATED` | Documentos mínimos foram validados | Document Processing |
| `UNDER_INVESTIGATION` | Consultas e análise de fatos em andamento | Investigation |
| `DECISION_PROPOSED` | Recomendação gerada e versionada | Decision Support |
| `AWAITING_APPROVAL` | Decisão humana obrigatória pendente | Human Approval |
| `MORE_EVIDENCE_REQUIRED` | Aprovação ou investigação exige informação adicional | Case Management |
| `APPROVED` | Recomendação aprovada dentro da alçada | Human Approval |
| `REJECTED` | Contestação rejeitada com motivo registrado | Human Approval |
| `EXECUTION_PENDING` | Decisão aprovada aguardando execução | Governed Execution |
| `EXECUTED` | Efeito mock executado e registrado | Governed Execution |
| `RECONCILIATION_REQUIRED` | Resultado de execução é ambíguo ou divergente | Governed Execution |
| `CLOSED` | Caso concluído e imutável para operação normal | Case Management |
| `CANCELLED` | Caso cancelado por regra ou solicitação válida | Case Management |
| `EXPIRED` | Prazo máximo atingido sem condição de continuidade | Case Management |
| `FAILED` | Falha não recuperável exige intervenção operacional | Platform Operations |

## Fluxo principal

```text
CREATED
  ├── documentos insuficientes → AWAITING_DOCUMENTS
  └── documentos anexados      → DOCUMENTS_RECEIVED

DOCUMENTS_RECEIVED
  ├── inválidos/incompletos     → AWAITING_DOCUMENTS
  └── válidos                   → DOCUMENTS_VALIDATED

DOCUMENTS_VALIDATED → UNDER_INVESTIGATION → DECISION_PROPOSED → AWAITING_APPROVAL

AWAITING_APPROVAL
  ├── pedir complemento         → MORE_EVIDENCE_REQUIRED
  ├── rejeitar                  → REJECTED → CLOSED
  └── aprovar                   → APPROVED → EXECUTION_PENDING

EXECUTION_PENDING
  ├── sucesso                   → EXECUTED → CLOSED
  ├── resultado ambíguo         → RECONCILIATION_REQUIRED
  └── falha recuperável         → EXECUTION_PENDING
```

## Transições controladas

| Origem | Destino | Condições mínimas |
|---|---|---|
| `CREATED` | `AWAITING_DOCUMENTS` | checklist documental identifica pendência |
| `CREATED` | `DOCUMENTS_RECEIVED` | ao menos um documento registrado |
| `DOCUMENTS_RECEIVED` | `DOCUMENTS_VALIDATED` | documentos obrigatórios, integridade e classificação aprovados |
| `DOCUMENTS_VALIDATED` | `UNDER_INVESTIGATION` | identidade do caso e evidências mínimas disponíveis |
| `UNDER_INVESTIGATION` | `DECISION_PROPOSED` | findings concluídos ou abstention justificada |
| `DECISION_PROPOSED` | `AWAITING_APPROVAL` | recomendação versionada, evidências e regras referenciadas |
| `AWAITING_APPROVAL` | `APPROVED` | aprovador elegível, alçada válida e segregação atendida |
| `AWAITING_APPROVAL` | `REJECTED` | motivo e base da decisão registrados |
| `AWAITING_APPROVAL` | `MORE_EVIDENCE_REQUIRED` | pendências explícitas e prazo definidos |
| `APPROVED` | `EXECUTION_PENDING` | decisão vigente e comando idempotente preparado |
| `EXECUTION_PENDING` | `EXECUTED` | resultado confirmado pelo sistema mock |
| `EXECUTION_PENDING` | `RECONCILIATION_REQUIRED` | timeout ou resposta ambígua após envio |
| `EXECUTED` | `CLOSED` | auditoria e comunicação registradas |
| `REJECTED` | `CLOSED` | comunicação e motivo registrados |

## Invariantes

1. nenhuma transição reduz tenant ou classificação de dados;
2. o recomendador não pode aprovar a própria recomendação;
3. execução exige decisão `APPROVED` vigente;
4. cada execução mutável possui chave de idempotência;
5. mudança de evidência invalida recomendação ainda não executada;
6. toda transição registra ator, origem, correlação, versão e motivo;
7. `CLOSED`, `CANCELLED` e `EXPIRED` são estados terminais para o fluxo normal;
8. retry não pode duplicar efeitos externos;
9. resultado ambíguo nunca é tratado automaticamente como sucesso;
10. o agente deve se abster quando faltarem evidências suficientes.

## Concorrência e versionamento

- cada caso possui `caseVersion` monotônica;
- comandos informam a versão esperada;
- atualização com versão obsoleta retorna conflito;
- somente uma transição de estado pode ser confirmada por versão;
- efeitos assíncronos carregam `caseId`, `caseVersion`, `correlationId` e `causationId`.
