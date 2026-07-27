# Policies

A autorização possui contrato declarativo e baseline executável em Rego.

## Fluxo

```text
PEP → AuthorizationInput → OPA/PDP → AuthorizationDecision → PEP aplica obrigações
```

## Actions

| Action | Subject esperado | Controle crítico |
|---|---|---|
| `case.create` | Case Manager | idempotência e tenant |
| `case.read` | leitor autorizado | tenant e redaction |
| `case.cancel` | Case Manager humano | estado e versão |
| `document.register` | Case Manager ou Document Processor | quarentena, estado e versão |
| `document.read` | função operacional autorizada | tenant e minimização |
| `evidence.read` | investigação, decisão, aprovação ou auditoria | tenant e finalidade |
| `investigation.execute` | Investigator ou Operations Analyst | tools autorizadas e evidência |
| `recommendation.create` | Decision Agent ou Operations Analyst | evidência e versão |
| `approval.decide` | aprovador humano | alçada e segregação |
| `execution.request` | workload `execution-service` | aprovação, idempotência e evidência |
| `execution.read` | execução, reconciliação, caso ou auditoria | tenant |
| `reconciliation.resolve` | reconciler | estado ambíguo e versão |
| `audit.read` | auditor humano | finalidade `AUDIT` |

## Baseline e produção

O Rego deste P3 demonstra decisões determinísticas e testes negativos. Produção ainda exige identidade corporativa, tokens curtos, KMS, distribuição de bundles, alta disponibilidade do PDP, métricas e processo de mudança de policy.
