# ADR-003 — Workflow como autoridade sobre estado e transições

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

A jornada de contestação possui estados, timers, retries, aprovações, reconciliação e encerramento. Agentes e workers podem produzir análises ou executar tarefas, mas não devem decidir livremente a progressão do processo.

Distribuir a autoridade de estado entre agentes, APIs e consumidores criaria transições inconsistentes, difícil recuperação e baixa auditabilidade.

## Decisão

O workflow é a autoridade canônica sobre o lifecycle do caso. Apenas regras e operações explícitas podem alterar estados, sempre com validação da versão esperada, policy aplicável e registro na timeline.

Agentes, document intelligence e workers retornam resultados. O workflow interpreta esses resultados e determina a próxima transição permitida.

Timers, retries e compensações são responsabilidades do workflow, não do modelo de IA.

## Alternativas consideradas

### Agentes controlando a jornada

Rejeitada porque modelos não são uma fonte adequada de verdade transacional, temporização ou recuperação operacional.

### Cada serviço alterando diretamente o estado

Rejeitada porque espalha invariantes e dificulta concorrência, auditoria e replay.

## Consequências

### Positivas

- lifecycle determinístico e auditável;
- concorrência controlada por versão esperada;
- recuperação e diagnóstico concentrados;
- agentes podem evoluir sem redefinir o processo.

### Negativas e trade-offs

- o workflow se torna componente crítico;
- novas transições exigem governança e testes;
- indisponibilidade do orquestrador bloqueia progressão segura.

## Critérios de revisão

Revisar apenas se outra tecnologia de orquestração assumir formalmente as mesmas garantias de estado, durabilidade, concorrência, timers, retries e auditoria.

## Evidências e links

- [Lifecycle do caso](../functional/case-lifecycle.md)
- [Componentes do Workflow Orchestrator](../architecture/component-workflow-orchestrator.md)
- [Diagramas de sequência](../architecture/sequence-diagrams.md)
- `samples/vertical-slice/app/service.py`
- `samples/vertical-slice/app/workflow_worker.py`
