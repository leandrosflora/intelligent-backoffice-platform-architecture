# Scripts

## Estrutura

```bash
python scripts/validate_structure.py
```

Confirma que os artefatos obrigatórios de P0 a P5 permanecem no repositório.

## Contratos

```bash
python scripts/validate_contracts.py
```

Valida OpenAPI 3.1, AsyncAPI 3.0, JSON Schema 2020-12, catálogo, referências locais, IDs, rastreabilidade, headers, idempotência e actions de policy.

## Policies

```bash
bash scripts/test-policies.sh
```

Executa `opa check --strict` e a suite Rego.

## Diagramas

```bash
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
```

Verifica fontes PlantUML, proíbe includes remotos, renderiza SVG/PNG e valida os artefatos usados pelo MkDocs.

## Evals

```bash
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
```

Executa o dataset versionado, aplica thresholds e gera relatórios JSON e Markdown.

## Observabilidade

```bash
python scripts/validate_observability.py
python scripts/validate_runtime_observability.py
```

O primeiro comando valida SLOs, alerts, runbooks, Prometheus, Collector, Grafana e dataset. O segundo valida uma stack em execução, incluindo métricas e presença do serviço no Jaeger.

## Jornada E2E

```bash
python scripts/run_vertical_slice_e2e.py
```

Executa a jornada completa contra o runtime Docker e produz `e2e-output.jsonl`.
