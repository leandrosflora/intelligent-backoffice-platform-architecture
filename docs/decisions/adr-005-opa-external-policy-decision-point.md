# ADR-005 — OPA externo como Policy Decision Point com default deny

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline local

## Contexto

A plataforma precisa aplicar autorização, tenant, finalidade, alçada, segregação de funções e obrigações de forma consistente. Embutir essas regras diretamente em cada endpoint dificultaria revisão, testes negativos, auditoria e evolução independente.

## Decisão

Operações sensíveis consultam um Policy Decision Point externo baseado em OPA. A aplicação envia identidade, ação, recurso e contexto relevante; o PDP retorna uma decisão explícita.

A política usa `default deny`. Indisponibilidade, resposta inválida ou contexto insuficiente resultam em negação e falha fechada. Headers fornecidos pelo cliente não são aceitos como fonte suficiente de privilégio no profile seguro.

## Alternativas consideradas

### Autorização codificada na aplicação

Rejeitada como mecanismo principal porque espalha regras, aumenta divergência e reduz a capacidade de revisão independente.

### Policy enforcement permissivo em falha

Rejeitada porque priorizaria disponibilidade sobre segurança em operações sensíveis.

### Apenas RBAC

Rejeitada porque papéis isolados não cobrem tenant, finalidade, estado, versão, alçada e segregação contextual.

## Consequências

### Positivas

- policies versionadas e testáveis;
- decisões consistentes e auditáveis;
- separação entre regra de autorização e lógica de domínio;
- suporte a testes negativos e purpose binding.

### Negativas e trade-offs

- o PDP entra no caminho crítico;
- latência e disponibilidade precisam ser tratadas;
- mudanças de schema entre aplicação e policy exigem compatibilidade.

## Critérios de revisão

Revisar quando houver PDP corporativo aprovado ou necessidade de distribuição, caching, bundles assinados, HA e lifecycle operacional de policies.

## Evidências e links

- [Policies](../contracts/policies.md)
- [PDP indisponível](../operations/runbooks/policy-decision-unavailable.md)
- `policies/authorization.rego`
- `contracts/policy/authorization.yaml`
- `samples/vertical-slice/app/policy.py`
