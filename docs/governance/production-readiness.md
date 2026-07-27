# Production readiness

O estado canônico está em `governance/production-readiness.yaml`.

## Regra

O repositório permanece `NOT_PRODUCTION_READY` enquanto existir qualquer gate em `TARGET_DEFINED`, `DEMONSTRATED_LOCAL` ou equivalente. A mudança para produção exige aprovação formal e evidências do ambiente real.

## Gates

- identidade e purpose binding;
- secret manager e KMS;
- SBOM, proveniência, assinatura e admission;
- alta disponibilidade;
- backup e restore;
- disaster recovery;
- capacidade;
- segurança de rede.

## Evidências

O workflow P7 publica:

- resultado E2E da identidade;
- SBOM;
- proveniência;
- relatório de capacidade;
- relatório de backup/restore.

Essas evidências são úteis para arquitetura e CI, mas não substituem testes e aprovações produtivas.
