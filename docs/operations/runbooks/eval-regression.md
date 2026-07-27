# Runbook — regressão de eval

## Trigger

Pipeline `P5 Observability and Evals` falha no gate de qualidade.

## Diagnóstico

1. Abra `evals/reports/latest.md` no artefato do workflow.
2. Identifique a capacidade e os casos com score reduzido.
3. Classifique a mudança como regressão, alteração intencional ou dataset incorreto.
4. Verifique especialmente abstention e groundedness.

## Mitigação

- corrija a implementação quando o comportamento esperado permanecer válido;
- altere dataset e threshold somente com justificativa arquitetural;
- não reduza threshold apenas para liberar o pipeline;
- adicione caso de regressão antes do merge.
