# Contracts

O diretório concentra os contratos executáveis que ligam a arquitetura funcional ao futuro vertical slice.

## Inventário

- `catalog.yaml`: catálogo canônico de HTTP operations, eventos e policies;
- `openapi/platform-api.yaml`: API do lifecycle de contestação;
- `asyncapi/platform-events.yaml`: eventos versionados do lifecycle;
- `schemas/canonical-models.yaml`: modelos funcionais compartilhados;
- `schemas/event-envelope.yaml`: envelope e payloads de eventos;
- `schemas/policy-contracts.yaml`: entrada e saída do Policy Decision Point;
- `policy/authorization.yaml`: matriz declarativa de autorização.

## Estados de maturidade

- `TARGET_CONTRACT`: contrato de arquitetura aprovado para orientar implementação;
- `EXECUTABLE_BASELINE`: controle executável em CI, sem integração produtiva;
- `PRODUCTION_CERTIFIED`: reservado para contrato certificado contra sistemas reais.

O P3 não classifica nenhum endpoint ou evento como produção.

## Validação

```bash
python scripts/validate_contracts.py
bash scripts/test-policies.sh
```

A validação cobre sintaxe, referências locais, rastreabilidade, IDs, headers obrigatórios, idempotência, versionamento, catálogo e testes Rego.
