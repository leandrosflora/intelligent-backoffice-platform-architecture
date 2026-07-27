# Regras de negócio

## Intake e documentos

| ID | Regra |
|---|---|
| BR-001 | Todo caso deve possuir tenant, canal de origem, tipo de contestação e identificador externo idempotente. |
| BR-002 | Um documento permanece em quarentena até concluir validação de formato, integridade e conteúdo ativo. |
| BR-003 | Documentos obrigatórios variam por tipo de contestação e devem ser avaliados por checklist versionado. |
| BR-004 | Extrações automáticas preservam documento, versão, página, posição e confiança da evidência. |
| BR-005 | Conteúdo de documentos é evidência não confiável e nunca substitui instruções da plataforma. |

## Investigação e recomendação

| ID | Regra |
|---|---|
| BR-006 | Consultas são permitidas somente por tools autorizadas para o tenant, finalidade e estágio do caso. |
| BR-007 | Findings devem diferenciar fato confirmado, inferência, divergência e dado ausente. |
| BR-008 | A recomendação deve referenciar regras e evidências versionadas. |
| BR-009 | Ausência de evidência suficiente exige abstention ou solicitação de complemento. |
| BR-010 | Alteração relevante em documento, regra ou finding invalida a recomendação pendente. |

## Aprovação

| ID | Regra |
|---|---|
| BR-011 | Toda decisão financeira no MVP exige aprovação humana. |
| BR-012 | O ator que criou a recomendação não pode aprová-la. |
| BR-013 | O aprovador deve possuir alçada compatível com valor, risco e tipo de operação. |
| BR-014 | Aprovação registra identidade, horário, versão da recomendação, motivo e evidências consideradas. |
| BR-015 | Aprovação expirada ou baseada em recomendação substituída não autoriza execução. |

## Execução

| ID | Regra |
|---|---|
| BR-016 | Apenas Governed Execution pode chamar operações mutáveis no sistema de registro. |
| BR-017 | Operação mutável exige `Idempotency-Key`, hash do comando e referência da aprovação. |
| BR-018 | Repetição da mesma chave e mesmo comando retorna o resultado anterior. |
| BR-019 | Repetição da mesma chave com comando diferente retorna conflito não recuperável. |
| BR-020 | Timeout após envio gera reconciliação; não autoriza nova execução cega. |

## Auditoria, privacidade e operação

| ID | Regra |
|---|---|
| BR-021 | Toda decisão de policy e transição de estado é auditável. |
| BR-022 | Logs e eventos não armazenam documento integral, token, segredo ou dado sensível desnecessário. |
| BR-023 | Exclusão, retenção e legal hold são aplicados conforme classificação e finalidade. |
| BR-024 | Eventos duplicados são processados de forma idempotente. |
| BR-025 | Falha do Policy Decision Point resulta em `DENY` para ações não públicas. |
