# Identidade de workload

## Baseline executável

O profile `secure` desabilita confiança em `X-Subject-*`, `X-Roles` e `X-Tenant-Id`. A identidade passa a vir de JWT EdDSA de curta duração.

Claims obrigatórios:

| Claim | Uso |
|---|---|
| `iss` e `aud` | vínculo com emissor e serviço |
| `sub` e `subject_type` | identidade do ator |
| `tenant_id` | isolamento |
| `roles` | autorização |
| `purpose` | finalidade permitida |
| `iat`, `exp` | validade máxima de 300 segundos |
| `jti` | identidade única e correlação |

O OPA também recebe `authentication_method`, `token_id` e `identity_mode`. Quando o modo é `jwt`, identidade baseada em headers é negada.

## Executar

```bash
python scripts/generate_dev_identity.py --force
docker compose --profile secure up --build
python scripts/run_p7_secure_e2e.py
```

## Controles comprovados

- ausência de token retorna `401`;
- audiência incorreta, expiração, TTL excessivo e assinatura alterada retornam `401`;
- headers não elevam privilégios;
- workload assinado pode operar apenas com os papéis do token;
- finalidade incompatível é negada pelo PDP.

## Produção

Produção deve usar OIDC corporativo ou SPIFFE/SPIRE, mTLS, rotação automática, revogação, audience por serviço e trust bundle gerenciado.
