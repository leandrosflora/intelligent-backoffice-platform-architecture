# Case aplicado — Contestação bancária

## Problema

Processos de contestação dependem de múltiplos documentos, consultas, regras, aprovações e registros manuais. Isso aumenta tempo de ciclo, retrabalho e risco operacional.

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
