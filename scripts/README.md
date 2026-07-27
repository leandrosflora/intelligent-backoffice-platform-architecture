# Scripts

## Validação estrutural

```bash
python scripts/validate_structure.py
```

Confirma os artefatos obrigatórios de P0 a P4.

## Contratos

```bash
python scripts/validate_contracts.py
```

Valida OpenAPI, AsyncAPI, schemas, catálogo e rastreabilidade.

## Vertical slice

```bash
python scripts/validate_vertical_slice.py
```

Confirma endpoints, actions, persistence, OPA, Docker Compose, solution e CI.

## Policies

```bash
bash scripts/test-policies.sh
```

Executa `opa check --strict` e os testes Rego.

## Diagramas

```bash
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
```

A renderização utiliza imagem PlantUML versionada e retry de download.
