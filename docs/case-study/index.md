# Case aplicado — Contestação bancária

## Problema

Processos de contestação dependem de documentos, consultas, regras, aprovações e registros manuais. Isso aumenta tempo de ciclo, retrabalho e risco operacional.

## Jornada inicial

```text
Caso criado
    ↓
Documentos recebidos
    ↓
Classificação e extração
    ↓
Validação de evidências
    ↓
Investigação e consultas
    ↓
Recomendação de decisão
    ↓
Aprovação humana
    ↓
Execução governada
    ↓
Auditoria e encerramento
```

## Guardrails do MVP

- dados e integrações sintéticos;
- nenhuma decisão financeira autônoma;
- aprovação humana obrigatória;
- execução somente contra sistemas mock;
- trilha completa de eventos e evidências;
- operações mutáveis com idempotência.

## Especificação funcional

O P1 detalha o case nos seguintes artefatos:

- [contexto de negócio](../context/business-context.md);
- [mapa de capacidades](../functional/capability-map.md);
- [mapa de domínios](../functional/domain-map.md);
- [lifecycle e máquina de estados](../functional/case-lifecycle.md);
- [regras de negócio](../functional/business-rules.md);
- [papéis e segregação de funções](../functional/roles-and-responsibilities.md);
- [outcome card](../functional/outcome-card.md);
- [classificação de risco](../functional/risk-classification.md);
- [requisitos não funcionais](../functional/non-functional-requirements.md);
- [rastreabilidade](../functional/traceability-matrix.md).

## Próxima evolução

O P2 deve materializar esta especificação em diagramas C4 de contexto, containers, componentes, trust boundaries e sequências principais.
