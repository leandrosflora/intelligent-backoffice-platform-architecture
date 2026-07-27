# Case aplicado — Contestação bancária

## Problema

Processos de contestação dependem de documentos, consultas, regras, aprovações e registros manuais. Isso aumenta tempo de ciclo, retrabalho e risco operacional.

## Jornada de referência

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

## Guardrails

- dados e integrações sintéticos;
- nenhuma decisão financeira autônoma;
- aprovação humana obrigatória;
- execução somente contra sistemas mock;
- trilha completa de eventos e evidências;
- operações mutáveis com idempotência.

## Especificação funcional

O case é detalhado pelos seguintes artefatos:

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

## Materialização técnica

A jornada é representada por:

- [diagramas C4](../architecture/index.md);
- [diagramas de sequência](../architecture/sequence-diagrams.md);
- [contratos executáveis](../contracts/index.md);
- [implementação de referência](../implementation/index.md);
- [avaliações versionadas](../evaluation/index.md);
- [controles de produção](../governance/production-readiness.md).

A implementação local comprova o fluxo e os controles com dados sintéticos. Ela não representa uma operação bancária produtiva.