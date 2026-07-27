# Deployment distribuído da baseline P6

[![Deployment distribuído](../assets/diagrams/c4-deployment-distributed-baseline.png)](../assets/diagrams/c4-deployment-distributed-baseline.svg)

[**Abrir diagrama em SVG**](../assets/diagrams/c4-deployment-distributed-baseline.svg)

O P6 adiciona uma baseline executável assíncrona sem substituir os profiles mínimos do P4 e P5.

## Componentes implementados

- API FastAPI com transactional outbox habilitado;
- Redpanda compatível com Kafka;
- outbox publisher;
- workflow worker com inbox idempotente;
- timer worker;
- armazenamento durável de dead letters;
- replay autorizado por OPA e auditado.

## Limites

SQLite, broker single-node, replication factor um e identidades locais não representam produção. A arquitetura produtiva deve definir HA, retenção, ACLs, criptografia, schema registry, capacidade, recuperação e segregação operacional.

**Fonte PlantUML:** `C4/c4-deployment-distributed-baseline.puml`.
