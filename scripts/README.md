# Scripts

## Estrutura e contratos

```bash
python scripts/validate_structure.py
python scripts/validate_contracts.py
```

## Policies

```bash
bash scripts/test-policies.sh
```

## Diagramas

```bash
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
```

## Evals e observabilidade

```bash
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
python scripts/validate_observability.py
```

## Eventing P6

```bash
python scripts/validate_eventing.py
docker compose --profile distributed config
docker compose --profile distributed up -d --build
python scripts/run_p6_distributed_e2e.py
docker compose --profile distributed down -v
```

A evidência E2E é gravada em `p6-e2e-output.jsonl` e publicada como artifact do GitHub Actions.
