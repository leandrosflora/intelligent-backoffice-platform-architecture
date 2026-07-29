# Roadmap e histórico de evolução

As fases abaixo registram a sequência de construção da arquitetura, da baseline e dos repositórios de produto. Elas não representam automaticamente o estado operacional de uma capacidade. Para avaliar o que está contratado, iniciado, demonstrado, integrado ou pronto para produção, use a matriz de implementação e o production readiness.

| Fase | Estado | Entrega principal |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Contexto, outcomes, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries, deployments e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas, catálogo e policies |
| P4 | Concluído | Vertical slice executável, persistência local e OPA |
| P5 | Concluído | Evals, observabilidade, SLOs, alertas e runbooks |
| P6 | Concluído | Event backbone, outbox, inbox, workers, timers, DLQ e replay |
| P7 | Baseline executável | Identidade assinada, KMS policy, SBOM, proveniência, HA/DR, capacidade e readiness gates |
| P8 | Quase concluído (5/7 critérios) | Backend de produto em .NET e frontend React, integrados e validados por E2E cross-repo automatizado |

## P8 — Implementação de produto

### Entregas iniciadas

- `backoffice-platform-api`: domínio, APIs, PostgreSQL, OPA externo, execução mock e reconciliação;
- `intelligent-backoffice-frontend`: console React, jornada guiada, identidades da baseline, evidências, execuções, timeline e Nginx;
- atualização desta arquitetura para representar o ecossistema multi-repositório.

### Critério de conclusão

P8 não será considerado concluído apenas porque frontend e backend compilam separadamente. O gate mínimo exige:

1. ✅ Compose ou ambiente integrado com frontend, API, PostgreSQL e OPA — `intelligent-backoffice-frontend/e2e/docker-compose.yml`, um comando por repositório;
2. ✅ E2E automatizado da jornada principal — [`Cross-repository E2E`](https://github.com/leandrosflora/intelligent-backoffice-frontend/actions/workflows/e2e.yml), jornada completa `createCase → registerDocument → investigate → recommend → approve → execute` até `EXECUTED`, pela UI real;
3. ✅ E2E do resultado ambíguo e reconciliação — mesmo workflow, caminho `execute` (ambíguo) → `RECONCILIATION_REQUIRED` → `reconcile` → `EXECUTED`, pela UI real;
4. ✅ OpenAPI publicada pelo backend e teste de compatibilidade contratual — `Backoffice.Contracts.Tests`, executado na CI do backend a cada push/PR;
5. ✅ pipeline de CI do backend — `backoffice-platform-api/.github/workflows/ci.yml` (build, `dotnet test`, evals, render Kubernetes, `promtool check rules`);
6. parcial — correlation ID (`X-Correlation-Id`) já atravessa frontend e API; OpenTelemetry já instrumenta API e workers do backend; a propagação ainda não foi observada ponta a ponta dentro do ambiente de E2E (sem coletor OTel conectado a essa stack);
7. parcial — o relatório do Playwright é publicado como artifact do GitHub Actions em toda execução (vinculado a commit/run), mas falta um resumo único consolidado equivalente ao `run_dispute_walkthrough.py` da baseline.

Itens 1–5 estão evidenciados e reproduzíveis. Os itens 6 e 7 são o trabalho restante antes de considerar P8 integralmente concluído.

## Próximas fases sugeridas

| Fase | Objetivo |
|---|---|
| P9 | ~~Integração cross-repo, Compose unificado e contract testing~~ — concluído como parte do P8 (itens 1–5 do critério de conclusão) |
| P10 | Observabilidade ponta a ponta no ambiente integrado (correlation ID/traces visíveis através do E2E), evidências consolidadas por execução, e eventing no backend de produto |
| P11 | Integrações reais, dados representativos e validação operacional |

## Estado canônico

O estado formal da solução permanece **`NOT_PRODUCTION_READY`**. A baseline comprova padrões; os repositórios de produto comprovam que a implementação começou e que a jornada principal e a reconciliação já têm integração validada ponta a ponta (E2E cross-repo automatizado). Ainda faltam IAM corporativo, DR, operação 24x7 e aprovação formal.

Consulte:

- [Repositórios de implementação do produto](implementation/product-repositories.md)
- [Estado de implementação](architecture/implementation-status.md)
- [Como ler esta arquitetura](guide/how-to-read.md)
- [Arquitetura técnica](architecture/index.md)
- [Production readiness](governance/production-readiness.md)

## Regra de evolução

Uma capacidade só deve avançar de estado quando possuir evidência atual, owner, contratos, testes, observabilidade e critérios operacionais compatíveis com o risco.
