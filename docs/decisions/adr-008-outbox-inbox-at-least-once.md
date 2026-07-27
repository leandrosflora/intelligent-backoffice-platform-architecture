# ADR-008 — Outbox, inbox e entrega at least once

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline distribuída

## Contexto

Persistir estado e publicar um evento em operações independentes cria dual write: o estado pode ser confirmado sem evento ou o evento pode ser publicado sem o estado correspondente. Brokers também podem reenviar mensagens, e consumidores podem falhar depois de produzir efeitos locais.

## Decisão

Eventos de domínio são gravados no transactional outbox no mesmo commit do estado e da timeline. Um publisher assíncrono envia os registros ao broker e só marca `PUBLISHED` após confirmação.

Consumidores processam com semântica at least once e mantêm inbox idempotente por consumer e `eventId`. O offset só é confirmado após processamento durável, identificação de duplicidade ou registro durável em DLQ.

Replay cria um novo `eventId`, mantém `replayOf`, justificativa e ator. A dead letter original não é removida.

## Alternativas consideradas

### Publicação direta após commit

Rejeitada porque uma falha entre commit e publicação perderia o evento.

### Exactly once como promessa de negócio

Rejeitada porque a garantia depende de broker, consumidor, storage e efeitos externos; idempotência explícita é mais verificável.

### Confirmar offset antes do efeito durável

Rejeitada porque uma falha posterior produziria perda silenciosa.

## Consequências

### Positivas

- elimina dual write entre estado local e intenção de publicação;
- tolera redelivery com deduplicação;
- oferece trilha clara de falha, DLQ e replay;
- desacopla disponibilidade da API e do broker.

### Negativas e trade-offs

- eventos podem chegar duplicados ou com atraso;
- outbox, inbox e DLQ precisam de retenção e monitoramento;
- consumidores devem ser idempotentes.

## Critérios de revisão

Revisar se uma plataforma corporativa oferecer garantias transacionais equivalentes, mantendo auditabilidade, replay, deduplicação e recuperação operacional.

## Evidências e links

- [Mensageria](../contracts/messaging.md)
- [Event backbone](../operations/eventing.md)
- [DLQ e replay](../operations/runbooks/dead-letter-replay.md)
- `samples/vertical-slice/app/eventing.py`
- `samples/vertical-slice/app/outbox_worker.py`
- `samples/vertical-slice/app/workflow_worker.py`
