# Implementação de referência

O repositório contém um **vertical slice executável** que demonstra a jornada principal e os controles arquiteturais com dados sintéticos e integrações mock.

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

As responsabilidades permanecem separadas por módulo, mas são executadas em um único serviço FastAPI. Essa decisão reduz o custo operacional da implementação de referência sem transformar o monólito modular na arquitetura-alvo definitiva.

## Persistência

O slice usa SQLite persistido em volume. A escolha é restrita ao ambiente de referência. Produção deve utilizar armazenamento corporativo, HA, backup, restore e mecanismos de concorrência compatíveis com os NFRs.

## Policy enforcement

Em Docker Compose, toda operação sensível consulta o OPA por HTTP. A aplicação falha fechada quando o PDP está indisponível.

## Evidência de implementação

- testes ponta a ponta;
- cobertura mínima de 85%;
- imagem Docker construída no CI;
- Compose validado;
- policies Rego carregadas no OPA;
- evals, métricas e traces;
- cenários distribuídos com outbox, inbox, timers, DLQ e replay.

## Limite da baseline

A implementação comprova padrões e mecanismos. Ela não comprova escala, integração corporativa, dados reais, operação multi-região ou prontidão produtiva.