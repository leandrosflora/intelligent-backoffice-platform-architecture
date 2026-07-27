# ADR-010 — Identidade assinada local evoluindo para IAM ou SPIFFE

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

A baseline precisa demonstrar autenticação verificável de pessoas e workloads sem depender de um provedor corporativo real. Headers livres são úteis para testes simples, mas não comprovam autenticidade e podem permitir spoofing se forem usados em ambientes sensíveis.

Produção exige emissão, rotação, revogação e trust domain gerenciados, além de proteção do canal entre workloads.

## Decisão

O profile seguro usa JWT EdDSA de curta duração com validação de assinatura, issuer, audience, TTL, tenant, papéis, finalidade e método de autenticação. Quando esse modo está ativo, headers não podem elevar privilégios nem substituir claims assinados.

A arquitetura-alvo adota IAM corporativo ou SPIFFE/SPIRE para workload identity, complementado por mTLS, rotação automática, revogação, secret manager e KMS gerenciados.

As chaves e identidades locais servem apenas para demonstração e CI.

## Alternativas consideradas

### Headers como identidade definitiva

Rejeitada porque não fornecem autenticidade criptográfica nem controle confiável de emissão.

### Segredo compartilhado de longa duração

Rejeitada por risco de vazamento, baixa rastreabilidade e rotação operacional difícil.

### Certificados manuais por serviço

Rejeitada como target porque não escala e aumenta risco de expiração e configuração inconsistente.

## Consequências

### Positivas

- baseline comprova validação criptográfica e purpose binding;
- reduz spoofing de identidade e tenant;
- estabelece caminho explícito para identidade corporativa de workload.

### Negativas e trade-offs

- geração local de chaves não comprova operação produtiva;
- integração corporativa exigirá federação e lifecycle de credenciais;
- mTLS e trust domains aumentam exigências operacionais.

## Critérios de revisão

Revisar quando um provedor corporativo for selecionado ou quando requisitos de federação, revogação, attestation, mTLS e identidade de usuário forem definidos.

## Evidências e links

- [Identidade de workload](../security/workload-identity.md)
- [Segredos e KMS](../security/secrets-and-kms.md)
- `security/workload-identity.yaml`
- `samples/vertical-slice/app/security.py`
- `samples/vertical-slice/tests/test_security_jwt.py`
