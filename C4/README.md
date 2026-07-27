# C4

Esta pasta contém as fontes PlantUML canônicas da arquitetura.

## Visões

### Contexto e containers

- `c4-context-current.puml`
- `c4-context-target.puml`
- `c4-container-current.puml`
- `c4-container-target.puml`

### Componentes e deployment

- `c4-component-workflow-orchestrator.puml`
- `c4-component-document-intelligence.puml`
- `c4-deployment-local.puml` — deployment alvo do futuro slice distribuído;
- `c4-deployment-observed-baseline.puml` — baseline executável confirmada no P5;
- `c4-trust-boundaries.puml`

### Sequências

- `sequence-case-intake.puml`
- `sequence-investigation-approval.puml`
- `sequence-governed-execution.puml`
- `sequence-missing-evidence.puml`

## Renderização

```bash
bash scripts/render-diagrams.sh
python scripts/validate_diagrams.py --require-generated
```

O script gera SVG e PNG em `docs/assets/diagrams/`.

## Regra de leitura

- **atual:** confirmado no repositório;
- **alvo:** responsabilidade ou integração planejada;
- **baseline executável:** comportamento demonstrado em CI e Docker Compose;
- **produção:** operação e integrações reais aprovadas.

A arquitetura não pode usar um diagrama alvo como evidência de implementação.
