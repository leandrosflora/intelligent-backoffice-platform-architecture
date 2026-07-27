# Versionamento e compatibilidade

## HTTP

- mudanças compatíveis permanecem na versão `/v1`;
- remoção, mudança de semântica ou tipo cria `/v2`;
- novos campos de resposta devem ser opcionais;
- clientes não devem depender da ordem de propriedades;
- `operationId` e `x-contract-id` são estáveis.

## Eventos

- endereço inclui major version, como `.v1`;
- `eventVersion` identifica revisão compatível do payload;
- breaking changes criam novo address;
- produtor deve suportar período de convivência quando houver migração;
- consumidor desconhecido não pode bloquear a publicação do evento.

## Schemas

- `$id` é imutável dentro da major version;
- referências são locais ao repositório para garantir builds reproduzíveis;
- enum recebe novos valores somente com avaliação de compatibilidade;
- conteúdo sensível não é introduzido sem data classification e revisão de privacidade.

## Policies

- actions e rule IDs são estáveis;
- mudança que amplia permissão exige revisão de segurança;
- mudança que restringe permissão exige análise de impacto operacional;
- toda mudança possui testes positivos e negativos;
- falha de carregamento ou decisão resulta em deny para ações não públicas.
