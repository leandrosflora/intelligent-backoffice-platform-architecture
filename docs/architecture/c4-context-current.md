# C4 — Contexto atual

O estado atual passa a combinar **uma baseline arquitetural executável** com **dois repositórios de produto em implementação inicial**.

- este repositório preserva arquitetura, contratos, policies, diagramas, evidências e o runtime FastAPI de referência;
- o `backoffice-platform-api` começa a materializar o backend de produto em .NET e PostgreSQL;
- o `intelligent-backoffice-frontend` começa a materializar a experiência operacional em React.

[![C4 contexto atual](../assets/diagrams/c4-context-current.png)](../assets/diagrams/c4-context-current.svg)

[**Abrir diagrama em SVG**](../assets/diagrams/c4-context-current.svg)

## Pessoas e interações

- o **analista de operações** utiliza o frontend para criar, consultar e avançar casos;
- o **aprovador** registra decisões humanas por meio da interface;
- o **arquiteto ou engenheiro** evolui os três repositórios e mantém a conformidade entre contratos e implementação;
- o **GitHub Actions** valida os repositórios por pipelines independentes;
- o **GitHub Pages** publica arquitetura, status e runbooks.

## Sistemas atuais

| Sistema | Responsabilidade | Estado |
|---|---|---|
| Intelligent Backoffice Frontend | Console React para operar a jornada e simular identidades da baseline | `IMPLEMENTATION_STARTED` |
| Backoffice Platform API | Backend .NET com domínio, PostgreSQL, PDP externo e execução mock | `IMPLEMENTATION_STARTED` |
| Architecture and Reference Environment | Contratos, ADRs, policies e baseline FastAPI executável | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` |

## Relação entre baseline e produto

A baseline FastAPI não foi substituída pelo backend .NET. As duas trilhas possuem objetivos diferentes:

- a **baseline** comprova padrões arquiteturais, eventing, observabilidade, evals, identidade assinada e readiness em ambiente local e CI;
- o **backend de produto** começa a implementar o domínio e a persistência que devem evoluir para a solução real;
- o **frontend de produto** começa a transformar os contratos em uma experiência operacional testável.

## Limites

!!! danger "Integração ainda não validada"
    Frontend e backend existem e possuem código funcional, mas ainda não há um gate E2E cross-repo automatizado que suba React, API .NET, PostgreSQL e OPA como uma única solução validada.

Não existem integrações corporativas, efeitos financeiros reais, IAM corporativo, operação 24x7 ou classificação produtiva.

O status oficial permanece **`NOT_PRODUCTION_READY`**.

Consulte:

- [repositórios de implementação do produto](../implementation/product-repositories.md);
- [matriz de implementação atual × alvo](implementation-status.md).

**Fonte PlantUML:** `C4/c4-context-current.puml`.
