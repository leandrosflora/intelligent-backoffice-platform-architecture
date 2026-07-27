# Evals

A baseline usa um dataset sintético e versionado para avaliar capacidades determinísticas que futuramente poderão ser implementadas por modelos de IA.

## Cobertura

- classificação documental;
- groundedness da investigação;
- recomendação baseada em evidências;
- abstention quando a evidência é insuficiente;
- entrada com texto semelhante a prompt injection tratada como conteúdo não confiável.

## Execução

```bash
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
```

O comando gera `evals/reports/latest.json` e `evals/reports/latest.md` e retorna código diferente de zero quando um threshold é violado.
