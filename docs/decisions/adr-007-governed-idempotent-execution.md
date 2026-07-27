# ADR-007 — Execução governada, idempotente e reconciliável

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

Operações mutáveis podem produzir efeitos financeiros ou alterações irreversíveis. Retries, timeouts e respostas ambíguas podem gerar duplicidade ou perda de confirmação. Permitir que agentes ou integrações chamem diretamente sistemas de registro eliminaria controles essenciais.

## Decisão

Toda operação mutável passa por uma capacidade de Governed Execution. A execução exige autorização do PDP, aprovação válida quando aplicável, chave de idempotência e hash do comando.

A mesma chave com o mesmo payload retorna o resultado previamente registrado. A reutilização da chave com payload diferente falha. Resultados ambíguos não são repetidos automaticamente: o caso entra em `RECONCILIATION_REQUIRED` e segue um processo explícito de reconciliação.

Na arquitetura-alvo, integrações com sistemas de registro devem ocorrer por adapters ou portas funcionais governadas, nunca diretamente por agentes.

## Alternativas consideradas

### Retry cego após timeout

Rejeitada porque pode duplicar efeitos quando o sistema remoto executou a operação, mas a resposta foi perdida.

### Acesso direto do agente ao sistema de registro

Rejeitada porque remove policy enforcement, idempotência, reconciliação e ownership do serviço de domínio.

### Deduplicação apenas no sistema remoto

Rejeitada como garantia única porque nem todos os sistemas possuem semântica compatível ou evidência suficiente.

## Consequências

### Positivas

- reduz efeitos duplicados;
- preserva comando, ator, autorização e resultado;
- trata incerteza como estado operacional explícito;
- desacopla agentes de integrações mutáveis.

### Negativas e trade-offs

- exige armazenamento durável de idempotência;
- reconciliação aumenta complexidade operacional;
- adapters precisam traduzir semântica e erros dos sistemas reais.

## Critérios de revisão

Revisar quando sistemas de registro reais fornecerem contratos transacionais, idempotência nativa ou mecanismos de confirmação que permitam simplificar sem reduzir garantias.

## Evidências e links

- [Execução ambígua](../operations/runbooks/execution-ambiguous.md)
- [Sequência de execução governada](../architecture/sequence-diagrams.md)
- `samples/vertical-slice/app/service.py`
- `contracts/openapi/platform-api.yaml`
- `policies/authorization.rego`
