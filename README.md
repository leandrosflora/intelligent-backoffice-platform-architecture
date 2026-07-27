# Intelligent Backoffice Platform Architecture

[![Quality](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/quality.yml)
[![Vertical Slice](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/vertical-slice.yml)
[![P5 Observability and Evals](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p5-observability-evals.yml)
[![P6 Eventing](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p6-eventing.yml)
[![P7 Production Readiness](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p7-production-readiness.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/p7-production-readiness.yml)
[![Documentation](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml/badge.svg)](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/actions/workflows/docs.yml)

Arquitetura de referência executável para automação inteligente de backoffice com agentes, processamento documental, workflows, human-in-the-loop, policies, auditoria e integração governada com sistemas corporativos.

## Case aplicado

O primeiro case é uma jornada bancária de contestação:

1. abertura e triagem;
2. recebimento e validação documental;
3. investigação;
4. recomendação explicável;
5. aprovação humana conforme alçada;
6. execução governada e idempotente;
7. reconciliação, auditoria e encerramento.

## Evolução

| Fase | Estado | Conteúdo |
|---|---|---|
| P0 | Concluído | Estrutura, MkDocs e pipelines |
| P1 | Concluído | Arquitetura funcional, lifecycle, regras, risco e NFRs |
| P2 | Concluído | C4, trust boundaries, deployment e sequências |
| P3 | Concluído | OpenAPI, AsyncAPI, schemas, catálogo e policies |
| P4 | Concluído | Vertical slice executável e OPA em runtime |
| P5 | Concluído | Evals, OpenTelemetry, métricas, SLOs, alertas e runbooks |
| P6 | Concluído | Kafka/Redpanda, outbox, inbox, workers, timers, DLQ e replay |
| P7 | Baseline executável | Identidade assinada, segredos/KMS, SBOM, proveniência, HA, DR, capacidade e readiness |

## P7 — Production readiness baseline

O P7 adiciona:

- JWT EdDSA de curta duração para identidades humanas e workloads;
- validação de issuer, audience, TTL, assinatura, tenant, papéis e finalidade;
- negação de spoofing por headers quando o profile seguro está ativo;
- policy OPA com `purpose binding` e verificação do método de autenticação;
- inventário de segredos e policy de KMS;
- backup local criptografado com AES-256-GCM e restore validado;
- runtime non-root;
- SBOM CycloneDX e proveniência in-toto/SLSA;
- deployment Kubernetes alvo com três réplicas, PDB, HPA, anti-affinity e NetworkPolicy;
- plano de DR, RTO/RPO e critérios de exercício;
- gate de capacidade;
- matriz de readiness com blockers explícitos.

O status oficial continua sendo **`NOT_PRODUCTION_READY`**. Os controles locais comprovam padrões, não uma implantação corporativa multi-região.

## Executar o profile seguro

```bash
python scripts/generate_dev_identity.py --force
docker compose --profile secure up --build
python scripts/run_p7_secure_e2e.py
```

- API segura: `http://localhost:8082`
- Swagger: `http://localhost:8082/docs`
- OPA: `http://localhost:8181`

Parar e remover o volume:

```bash
docker compose --profile secure down -v
```

## Executar capacidade, backup e supply chain

```bash
python scripts/generate_dev_kms_key.py --force
python scripts/run_capacity_test.py

python scripts/backup_restore_drill.py \
  --database artifacts/drill-source.db \
  --key-file .local/security/backup-aes256.key

python scripts/generate_sbom.py
python scripts/generate_provenance.py
python scripts/validate_p7.py --require-evidence
```

## Profiles anteriores

Runtime mínimo:

```bash
docker compose --profile runtime up --build
```

Observabilidade:

```bash
OTEL_TRACING_ENABLED=true docker compose --profile observability up --build
```

Workflow distribuído:

```bash
docker compose --profile distributed up --build
python scripts/run_p6_distributed_e2e.py
```

## Validação completa

```bash
python scripts/validate_structure.py
python scripts/validate_contracts.py
python scripts/validate_observability.py
python scripts/validate_eventing.py
python scripts/validate_p7.py
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
bash scripts/test-policies.sh
python scripts/validate_diagrams.py
bash scripts/render-diagrams.sh
mkdocs build --strict
docker compose --profile secure config
```

## Princípio de leitura

- **atual:** capacidade confirmada;
- **alvo:** responsabilidade planejada;
- **baseline executável:** controle demonstrado em CI ou no ambiente de referência;
- **produção:** integração real, operação e governança aprovadas.

Produção ainda exige identidade corporativa ou SPIFFE, mTLS, secret manager/KMS real, assinatura de artifacts, admission control, database e Kafka Multi-AZ, testes representativos, DR real e operação 24x7.
