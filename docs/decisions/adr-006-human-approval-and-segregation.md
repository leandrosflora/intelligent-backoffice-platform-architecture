# ADR-006 — Aprovação humana e segregação de funções para decisões sensíveis

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

Recomendações podem resultar em efeitos financeiros, alterações de cadastro ou outras ações reguladas. A mesma identidade que produz a recomendação não deve aprová-la quando houver exigência de alçada ou segregação de funções.

## Decisão

Decisões sensíveis exigem tarefa de aprovação humana. O aprovador deve possuir papel, finalidade e alçada compatíveis, e não pode ser a mesma identidade que produziu a recomendação quando a regra de segregação se aplicar.

A decisão humana registra identidade, motivo, versão da recomendação, resultado e contexto de autorização. A execução só pode usar a versão explicitamente aprovada.

## Alternativas consideradas

### Autoaprovação baseada em confiança do modelo

Rejeitada porque score de modelo não substitui autorização, accountability ou segregação de funções.

### Aprovação sem vínculo com versão

Rejeitada porque permitiria executar uma recomendação diferente daquela avaliada pela pessoa responsável.

## Consequências

### Positivas

- accountability explícita;
- proteção contra autoaprovação e recomendação alterada;
- aderência a alçada e segregação de funções;
- evidência clara para auditoria.

### Negativas e trade-offs

- aumenta tempo de ciclo para casos sensíveis;
- exige filas, delegação e tratamento de indisponibilidade humana;
- regras de aprovação precisam de owner funcional.

## Critérios de revisão

A obrigatoriedade só pode ser reduzida por decisão formal baseada em risco, regulação, performance comprovada, controles compensatórios e capacidade de contestação e reversão.

## Evidências e links

- [Papéis e responsabilidades](../functional/roles-and-responsibilities.md)
- [Regras de negócio](../functional/business-rules.md)
- [Sequência de investigação e aprovação](../architecture/sequence-diagrams.md)
- `samples/vertical-slice/app/service.py`
- `policies/authorization.rego`
