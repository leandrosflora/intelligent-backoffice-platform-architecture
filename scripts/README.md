# Scripts

## Validação estrutural

```bash
python scripts/validate_structure.py
```

Confirma que os artefatos obrigatórios de P0, P1 e P2 permanecem no repositório.

## Validação de diagramas

```bash
python scripts/validate_diagrams.py
```

Verifica inventário, delimitadores PlantUML e proíbe includes ou URLs remotas.

## Renderização

```bash
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
```

A renderização utiliza uma imagem PlantUML versionada e tenta o download até três vezes para reduzir falhas transitórias do registry.
