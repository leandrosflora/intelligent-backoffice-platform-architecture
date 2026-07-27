# Evals do P5

O P5 adiciona uma baseline de avaliação versionada para as capacidades inteligentes do vertical slice. Os componentes continuam determinísticos; o objetivo é estabelecer o contrato de qualidade antes da adoção de OCR ou modelos reais.

## Dataset

O arquivo `evals/datasets/intelligence-v1.jsonl` cobre:

- classificação de comprovante, extrato e documento de identidade;
- abstention para arquivos desconhecidos ou formatos não suportados;
- entrada semelhante a prompt injection tratada como dado não confiável;
- investigação grounded somente quando há evidências;
- recomendação `APPROVE` somente com finding e evidência compatíveis;
- recomendação `ABSTAIN` quando não há grounding suficiente.

## Gates

Os thresholds ficam em `evals/thresholds.yaml`. A pipeline falha quando:

- o score total fica abaixo do mínimo;
- uma capacidade viola o score mínimo específico;
- documentos desconhecidos deixam de gerar abstention;
- uma recomendação sem grounding deixa de gerar abstention.

## Execução

```bash
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
```

Os relatórios JSON e Markdown são gerados em `evals/reports/` e publicados como artefatos do GitHub Actions.

## Limite

Esses evals não medem precisão de OCR, qualidade de LLM ou desempenho com documentos bancários reais. Eles definem a infraestrutura e os guardrails que deverão permanecer quando capacidades reais forem introduzidas.
