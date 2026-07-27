# ADR-013 — Arquitetura e contratos como código versionado

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Governança

## Contexto

Diagramas, APIs, eventos, schemas, policies, SLOs e readiness gates podem divergir quando são mantidos em ferramentas e processos separados. Imagens estáticas e documentos sem validação não oferecem rastreabilidade suficiente entre intenção arquitetural e implementação.

## Decisão

A arquitetura será mantida como código no mesmo fluxo de versionamento e revisão da implementação de referência.

- diagramas C4 usam PlantUML e a biblioteca C4-PlantUML;
- APIs usam OpenAPI;
- eventos usam AsyncAPI e envelopes versionados;
- modelos canônicos usam JSON Schema ou YAML estruturado;
- autorização usa Rego e catálogo de policies;
- SLOs, alertas, evals e readiness gates são arquivos versionados;
- MkDocs publica a narrativa e os links entre artefatos;
- CI valida estrutura, referências, renderização e consistência básica.

Artefatos gerados não substituem as fontes versionadas. Mudanças arquiteturais relevantes devem atualizar diagramas, contratos, ADRs e evidências aplicáveis no mesmo pull request ou em mudanças explicitamente vinculadas.

## Alternativas consideradas

### Diagramas manuais em ferramenta proprietária

Rejeitada como fonte canônica porque dificulta diff, revisão automatizada, reprodução e validação em CI.

### Documentação separada do repositório

Rejeitada porque aumenta atraso e divergência entre código, contratos e arquitetura.

### Apenas código como documentação

Rejeitada porque código não expressa adequadamente contexto, decisões, responsabilidades, riscos e arquitetura-alvo.

## Consequências

### Positivas

- histórico e revisão por pull request;
- diagramas e contratos reproduzíveis;
- maior rastreabilidade entre necessidade, decisão, contrato e evidência;
- gates automáticos contra ausência ou quebra estrutural.

### Negativas e trade-offs

- autores precisam conhecer formatos e toolchain;
- validações semânticas completas exigem evolução contínua;
- conteúdo visual sofisticado pode demandar ferramentas complementares.

## Critérios de revisão

Revisar se uma plataforma corporativa oferecer governança, versionamento, automação e portabilidade equivalentes sem perder fontes abertas e rastreabilidade no repositório.

## Evidências e links

- [Arquitetura técnica](../architecture/index.md)
- [Contratos executáveis](../contracts/index.md)
- [Matriz de rastreabilidade](../functional/traceability-matrix.md)
- `C4/`
- `contracts/`
- `scripts/validate_diagrams.py`
- `scripts/validate_contracts.py`
- `mkdocs.yml`
