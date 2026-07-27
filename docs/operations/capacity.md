# Capacidade e performance

O P7 adiciona um gate de regressão local para a operação protegida `GET /v1/cases/{caseId}`.

Configuração inicial:

| Parâmetro | Valor |
|---|---:|
| Requisições | 100 |
| Concorrência | 8 |
| Erro máximo | 1% |
| p95 máximo | 1,5 s |

Executar:

```bash
python scripts/run_capacity_test.py
```

O relatório é gravado em `artifacts/capacity-report.json`.

Este teste detecta regressões graves na baseline. Dimensionamento produtivo exige massa representativa, soak test, picos, dependências reais, falhas induzidas e análise de custo.
