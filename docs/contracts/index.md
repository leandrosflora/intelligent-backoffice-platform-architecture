# Contratos executáveis

Lifecycle, regras e responsabilidades são traduzidos em contratos verificáveis antes da implementação ou integração dos serviços.

## Inventário

| Tipo | Quantidade | Fonte | Estado |
|---|---:|---|---|
| Operações HTTP | 14 | `contracts/openapi/platform-api.yaml` | Target contract |
| Eventos de domínio | 14 | `contracts/asyncapi/platform-events.yaml` | Target contract |
| Regras de autorização | 13 | `contracts/policy/authorization.yaml` | Baseline executável |
| Catálogos JSON Schema | 3 | `contracts/schemas/` | Modelo canônico |

## Princípios

- nenhum contrato confia somente em headers fornecidos pelo cliente;
- toda operação protegida exige tenant e correlação;
- mutações exigem idempotência;
- transições de caso exigem versão esperada;
- eventos possuem envelope, versão e causalidade;
- documentos e payloads não carregam conteúdo sensível integral por padrão;
- cada operação, evento e policy referencia capacidades e regras de negócio;
- policy usa `default deny` e segregação de funções.

## Catálogo

O arquivo `contracts/catalog.yaml` é a lista canônica de contratos. O CI compara o catálogo com OpenAPI, AsyncAPI e policies e falha quando houver divergência.