# ADR-012 — Observabilidade e evals como gates versionados

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

Capacidades inteligentes e workflows distribuídos podem degradar sem falha binária evidente. Testes funcionais isolados não detectam regressões de grounding, abstention, latência, erros, backlog, duplicidade ou comportamento operacional.

Sem thresholds versionados, a aceitação depende de avaliação subjetiva e não impede regressões no CI.

## Decisão

Métricas, traces, SLOs, alertas, datasets e thresholds de avaliação são tratados como artefatos versionados da arquitetura. A pipeline deve falhar quando gates mínimos de qualidade, abstention, grounding, cobertura ou capacidade forem violados.

Telemetria não deve usar identificadores de caso ou tenant como labels de alta cardinalidade. Logs, traces e eventos devem minimizar PII e preservar correlação suficiente para diagnóstico.

Na arquitetura-alvo, esses controles integram a stack corporativa, incident management, on-call, retenção e revisão periódica de qualidade.

## Alternativas consideradas

### Avaliação manual antes do release

Rejeitada como controle principal porque é inconsistente, pouco reproduzível e não protege cada mudança.

### Apenas testes unitários

Rejeitada porque não cobre comportamento ponta a ponta, telemetria, distribuição ou qualidade das capacidades inteligentes.

### Monitoramento somente após produção

Rejeitada porque transfere detecção de regressão para usuários e operação.

## Consequências

### Positivas

- regressões são bloqueadas antes do merge;
- qualidade e operação possuem critérios explícitos;
- datasets, SLOs e alertas evoluem junto com o código;
- facilita auditoria das condições de release.

### Negativas e trade-offs

- datasets e thresholds exigem manutenção;
- gates mal calibrados podem gerar falsos positivos ou acomodar baixa qualidade;
- telemetria local não comprova operação 24x7.

## Critérios de revisão

Revisar quando modelos reais, dados representativos, SLIs corporativos, volumetria e processo formal de incidentes forem adotados.

## Evidências e links

- [Avaliação das capacidades inteligentes](../evaluation/index.md)
- [Observabilidade](../operations/observability.md)
- [SLOs e alertas](../operations/slos.md)
- `evals/thresholds.yaml`
- `observability/slos.yaml`
- `.github/workflows/p5-observability-evals.yml`
