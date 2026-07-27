# Runbook — alta taxa de erro ou latência

## Trigger

- `BackofficeApiHighErrorRate`; ou
- `BackofficeApiHighLatency`.

## Diagnóstico

1. Confirme o período e as rotas afetadas no Grafana.
2. Consulte traces da rota no Jaeger usando o mesmo intervalo.
3. Verifique logs da API, saturação do processo e latência do OPA.
4. Separe falha de dependência, erro de código e entrada inválida.

## Mitigação

- preserve o fail-closed de autorização;
- interrompa mudanças recentes quando houver correlação temporal;
- reduza tráfego de teste ou carga sintética;
- não desabilite idempotência, versionamento ou aprovação para recuperar disponibilidade.

## Recuperação

O incidente pode ser encerrado quando o error ratio e a latência retornarem ao target por pelo menos duas janelas de avaliação e houver evidência do root cause.
