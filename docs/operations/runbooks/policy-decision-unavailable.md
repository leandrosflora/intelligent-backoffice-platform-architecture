# Runbook — PDP indisponível

## Trigger

`BackofficePolicyUnavailable` ou resposta HTTP `503 Policy decision unavailable`.

## Impacto

Ações protegidas são negadas por segurança. Não existe fallback permissivo.

## Diagnóstico

1. Verifique saúde e logs do container `opa`.
2. Confirme a carga da policy e erros de compilação Rego.
3. Verifique conectividade da API para `http://opa:8181`.
4. Consulte `backoffice_policy_decision_duration_seconds` e traces `policy.authorize`.

## Mitigação

- restaure o PDP ou reverta a policy defeituosa;
- mantenha o runtime fail-closed;
- não altere `POLICY_MODE` para embedded em ambiente que represente produção.

## Evidência de recuperação

- health do OPA disponível;
- policy tests aprovados;
- decisão allow e deny funcionando;
- métrica `decision="unavailable"` sem novos incrementos.
