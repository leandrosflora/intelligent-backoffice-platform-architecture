# Scripts

## Estrutura

```bash
python scripts/validate_structure.py
```

Confirma que os artefatos obrigatórios de P0 a P3 permanecem no repositório.

## Contratos

```bash
python scripts/validate_contracts.py
```

Valida OpenAPI 3.1, AsyncAPI 3.0, JSON Schema 2020-12, catálogo, referências locais, IDs, rastreabilidade, headers obrigatórios, idempotência e cobertura das actions de policy.

## Policies

```bash
bash scripts/test-policies.sh
```

Executa `opa check --strict` e a suite Rego. A imagem OPA é versionada e o pull possui três tentativas para reduzir falhas transitórias do registry.

## Diagramas

```bash
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
```

Verifica fontes PlantUML, proíbe includes remotos, renderiza SVG/PNG e valida os artefatos usados pelo MkDocs.
