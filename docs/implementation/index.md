# Implementação P4

O P4 introduz o primeiro **vertical slice executável** da plataforma.

## Escopo implementado

- Case API;
- workflow persistido;
- document intelligence mock;
- investigação mock;
- recomendação;
- aprovação humana;
- execução governada mock;
- OPA em runtime;
- idempotência;
- versionamento otimista;
- timeline auditável;
- caminho de reconciliação para resultado ambíguo.

## Estratégia de empacotamento

As responsabilidades permanecem separadas por módulo, mas são executadas em um único serviço FastAPI. Essa decisão reduz custo operacional do primeiro slice sem transformar o monólito modular em arquitetura-alvo definitiva.

## Persistência

O slice usa SQLite persistido em volume. A escolha é restrita ao ambiente de referência. Produção deve utilizar armazenamento corporativo, HA, backup, restore e mecanismos de concorrência compatíveis com os NFRs.

## Policy enforcement

Em Docker Compose, toda operação sensível consulta o OPA por HTTP. A aplicação falha fechada quando o PDP está indisponível.

## Evidência de implementação

- testes ponta a ponta;
- cobertura mínima de 85%;
- imagem Docker construída no CI;
- Compose validado;
- policies Rego do P3 carregadas no OPA.
