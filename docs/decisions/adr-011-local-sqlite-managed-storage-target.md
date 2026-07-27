# ADR-011 — SQLite apenas local e armazenamento gerenciado como target

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

A implementação de referência precisa de persistência simples, reproduzível e suficiente para demonstrar lifecycle, concorrência otimista, outbox, inbox, timers, idempotência e timeline. SQLite atende esse objetivo local sem dependências adicionais.

Ele não atende, por si só, requisitos corporativos de alta disponibilidade, concorrência, backup gerenciado, point-in-time recovery, observabilidade e operação distribuída.

## Decisão

SQLite será usado exclusivamente na baseline local e em testes. Produção deve utilizar banco relacional gerenciado, preferencialmente PostgreSQL compatível com transações, HA, PITR, backup e controles de acesso corporativos.

Documentos e artefatos binários devem permanecer fora do banco relacional, em object store gerenciado com quarentena, versionamento, criptografia e políticas de retenção. O banco armazena metadados, checksums, relações e estado do workflow.

## Alternativas consideradas

### SQLite em produção

Rejeitada por limitações de HA, concorrência, operação distribuída e suporte corporativo.

### Documentos completos no banco relacional

Rejeitada por custo, crescimento, retenção e acoplamento entre estado transacional e conteúdo binário.

### Banco NoSQL como store único

Rejeitada como padrão inicial porque a jornada depende de transações, versão, outbox e relações que são bem atendidas por modelo relacional.

## Consequências

### Positivas

- baseline simples e reproduzível;
- target com responsabilidades claras entre estado e documentos;
- caminho explícito para HA, backup e recuperação;
- reduz propagação de conteúdo sensível.

### Negativas e trade-offs

- migração de schema e comportamento precisa ser validada;
- produção depende de dois tipos de storage;
- consistência entre metadados e objetos exige desenho operacional.

## Critérios de revisão

Revisar quando volumetria, padrões de acesso, requisitos de retenção, residência de dados ou serviços gerenciados corporativos forem definidos.

## Evidências e links

- [Deployment observado](../architecture/deployment-observed-baseline.md)
- [Deployment alvo de produção](../architecture/deployment-production-target.md)
- [Alta disponibilidade e DR](../operations/ha-dr.md)
- `samples/vertical-slice/app/store.py`
- `resilience/backup-policy.yaml`
