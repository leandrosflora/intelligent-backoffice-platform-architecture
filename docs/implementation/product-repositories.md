# Repositórios de implementação do produto

A plataforma passa a possuir três trilhas complementares de entrega. Este repositório continua sendo a fonte de arquitetura, contratos e evidências da baseline; backend e frontend começam a materializar o produto em repositórios próprios.

## Visão do ecossistema

| Repositório | Responsabilidade | Estado atual |
|---|---|---|
| [intelligent-backoffice-platform-architecture](https://github.com/leandrosflora/intelligent-backoffice-platform-architecture) | Arquitetura, ADRs, contratos, policies, diagramas, baseline FastAPI executável, evals e readiness | `DEMONSTRATED_LOCAL` para a baseline e `CONTRACT_DEFINED` para os contratos |
| [backoffice-platform-api](https://github.com/leandrosflora/backoffice-platform-api) | Backend de produto em .NET, domínio, persistência PostgreSQL, enforcement via OPA e APIs da jornada | `IMPLEMENTATION_STARTED` |
| [intelligent-backoffice-frontend](https://github.com/leandrosflora/intelligent-backoffice-frontend) | Console React para operar casos, simular identidades e consumir as APIs do backend | `IMPLEMENTATION_STARTED` |

## Backend de produto

O `backoffice-platform-api` inicia a implementação do domínio como um monólito modular em .NET 9.

### Capacidades já materializadas em código

- criação, listagem, consulta e cancelamento de casos;
- versionamento otimista com `If-Match`;
- timeline mantida pelo aggregate de caso;
- registro e consulta de documentos e evidências;
- investigação determinística;
- recomendação grounded;
- aprovação humana com alçada e segregação de funções;
- execução idempotente;
- resultado ambíguo e reconciliação explícita;
- persistência PostgreSQL;
- chamada a PDP OPA externo;
- gateway de execução mock para desenvolvimento e testes.

### Limites atuais

- identidade ainda extraída de headers de desenvolvimento;
- execução permanece mock;
- não há integração corporativa ou efeito financeiro real;
- o Compose do backend inicia PostgreSQL, mas a API e o PDP ainda precisam ser coordenados no ambiente local;
- não há evidência cross-repo suficiente para classificar a integração como `VALIDATED_INTEGRATION`.

## Frontend de produto

O `intelligent-backoffice-frontend` implementa um console operacional em React 19 e Vite.

### Capacidades já materializadas em código

- criação, listagem e consulta de casos;
- jornada guiada pelo estado retornado pelo backend;
- registro documental sintético;
- consulta de evidências, execuções e timeline;
- investigação, recomendação, aprovação, execução e reconciliação;
- modo guiado e modo manual de identidades;
- envio de tenant, papéis, alçada, correlation ID, `If-Match` e `Idempotency-Key`;
- tratamento de Problem Details e conflitos de versão;
- Nginx como reverse proxy para `/api`;
- lint, testes unitários, build Vite, validação do Compose e build da imagem no CI.

### Limites atuais

- não há autenticação JWT ou login corporativo;
- documentos são representados por metadados, não upload binário;
- IDs de recomendação e aprovação precisam permanecer no `localStorage`, pois o backend ainda não oferece consultas desses recursos por caso;
- não há teste E2E automatizado envolvendo os dois repositórios.

## Topologia local em construção

```text
Navegador
   |
   v
React SPA / Vite ou Nginx
   |
   | REST / JSON + headers de identidade da baseline
   v
Backoffice Platform API (.NET 9)
   |                       |
   | SQL                   | HTTP / JSON
   v                       v
PostgreSQL 16           OPA / Rego
```

A baseline FastAPI deste repositório permanece separada. Ela continua validando padrões, eventing, observabilidade, identidade assinada, evals e readiness enquanto esses controles são progressivamente incorporados aos repositórios de produto.

## Estado de integração

O início dos dois repositórios não altera automaticamente o status agregado da solução.

| Gate | Estado |
|---|---|
| Contratos arquiteturais versionados | `CONTRACT_DEFINED` |
| Baseline executável deste repositório | `DEMONSTRATED_LOCAL` |
| Backend de produto | `IMPLEMENTATION_STARTED` |
| Frontend de produto | `IMPLEMENTATION_STARTED` |
| Frontend + backend + PostgreSQL + OPA em E2E automatizado | Pendente |
| Integrações corporativas reais | Pendente |
| Production readiness | `NOT_PRODUCTION_READY` |

## Próximos gates

1. criar pipeline de CI do backend com build, testes, migrations e policy tests;
2. disponibilizar um Compose integrado para PostgreSQL, OPA, API e frontend;
3. criar E2E cross-repo cobrindo a jornada principal e o resultado ambíguo;
4. adicionar endpoints de consulta para recomendações e aprovações;
5. substituir headers de desenvolvimento por identidade assinada;
6. publicar OpenAPI do backend e validar compatibilidade contra os contratos deste repositório;
7. incorporar observabilidade, eventing e evidências operacionais ao backend de produto.

!!! warning "Classificação correta"
    Código existente em repositórios separados comprova que a implementação começou. Não comprova integração validada, operação corporativa ou prontidão produtiva.
