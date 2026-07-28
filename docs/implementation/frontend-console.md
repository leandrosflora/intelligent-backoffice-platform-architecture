# Frontend de produto — `intelligent-backoffice-frontend`

O repositório [`intelligent-backoffice-frontend`](https://github.com/leandrosflora/intelligent-backoffice-frontend) implementa um console operacional em React 19 e Vite para executar, inspecionar e testar a jornada exposta pelo backend .NET.

A interface não controla o lifecycle localmente. Cada transição é enviada à API e validada por estado, versão, tenant, identidade, papéis, policy, alçada e idempotência.

## Classificação atual

| Dimensão | Estado | Leitura correta |
|---|---|---|
| Implementação do componente frontend | `IMPLEMENTATION_STARTED` | O console cobre a jornada principal e cenários de erro |
| Build e testes do componente | `DEMONSTRATED_LOCAL` | Lint, testes, build Vite, Compose e imagem Docker estão automatizados |
| Integração manual com o backend | `DEMONSTRATED_LOCAL` | Vite e Nginx encaminham `/api` para a API configurada |
| Integração E2E cross-repo | Pendente | Não existe gate automatizado envolvendo navegador, frontend, API, PostgreSQL e OPA |
| Produção | `NOT_PRODUCTION_READY` | Não há login corporativo, gestão de sessão, observabilidade E2E ou hardening operacional completo |

## Funcionalidades implementadas

- criação, listagem e consulta de casos;
- jornada guiada pelo estado retornado pela API;
- cancelamento quando permitido pelo lifecycle;
- registro de documento sintético;
- consulta de evidências;
- investigação e recomendação;
- aprovação humana com `X-Authority-Limit`;
- execução mock com sucesso, falha ou resultado ambíguo;
- reconciliação autorizada;
- consulta de execuções e timeline;
- console local de requisições, identidade, latência, correlation ID e Problem Details;
- modo manual para testar negações de policy;
- tratamento de conflitos de versão e falhas HTTP.

## Modos de identidade

### Guiado

O console escolhe a identidade esperada para a ação:

| Identidade | Responsabilidade |
|---|---|
| `case-manager` | Gestão de casos |
| `document-processor` | Registro documental |
| `operations-analyst` | Evidências e investigação |
| `decision-agent` | Recomendação |
| `approver` | Aprovação humana |
| `execution-service` | Execução governada |
| `reconciler` | Reconciliação |
| `auditor` | Timeline e consulta de execuções |

### Manual

Mantém uma identidade selecionada em todas as chamadas. Esse modo permite validar:

- `403 Forbidden`;
- segregação de funções;
- least privilege;
- purpose binding;
- tenant mismatch;
- alçada insuficiente.

## Contratos HTTP usados

O frontend envia os elementos de governança exigidos pelo backend:

- `X-Tenant-Id`;
- identidade e tipo do sujeito;
- papéis;
- `X-Authority-Limit`;
- `X-Correlation-Id`;
- `If-Match`;
- `Idempotency-Key`.

O console apresenta respostas Problem Details e mantém o correlation ID para diagnóstico.

## Continuidade da jornada

A API expõe listagem de casos, evidências, execuções e timeline. Como ainda não existem endpoints de recuperação de recomendações e aprovações por caso, o frontend mantém IDs intermediários no `localStorage`.

Isso permite continuar uma jornada no mesmo navegador, mas não resolve recuperação multiusuário, troca de dispositivo ou retomada operacional após limpeza do storage local.

## Execução local

### Desenvolvimento com Vite

```bash
cd intelligent-backoffice-frontend/intelligent-backoffice-frontend
npm ci
npm run dev
```

A aplicação abre em `http://localhost:5173` e encaminha `/api` para `http://localhost:5260` por padrão.

### Imagem com Nginx

```bash
cd intelligent-backoffice-frontend
BACKEND_URL=http://host.docker.internal:8080 docker compose up -d --build
```

A aplicação abre em `http://localhost:3000`. A porta pode ser alterada por `FRONTEND_PORT`.

## Qualidade

O comando local:

```bash
npm run check
```

executa lint, testes unitários do modelo de workflow e build de produção.

O workflow de CI também valida:

- instalação reproduzível com `npm ci`;
- ESLint;
- testes unitários;
- build Vite;
- `docker compose config`;
- build da imagem Nginx.

## Limites atuais

- identidade baseada em headers para o fluxo padrão;
- sem login JWT/OIDC no navegador;
- sem gestão corporativa de sessão e autorização de rota;
- documentos representados por metadados, não upload binário;
- execução financeira mock;
- IDs intermediários persistidos no `localStorage`;
- sem endpoints de métricas, outbox, timers, DLQ e replay integrados à experiência principal;
- sem teste E2E automatizado cross-repo;
- sem telemetria distribuída do navegador até os workers.

## Próximos gates

1. implementar autenticação OIDC/JWT e sessão segura;
2. criar recuperação de recomendações e aprovações por caso;
3. adicionar upload documental real com progresso e tratamento de quarentena;
4. incorporar telas operacionais de outbox, timers, DLQ e replay;
5. instrumentar frontend com correlação e tracing distribuído;
6. criar E2E browser-based com casos positivos e negações de policy;
7. validar acessibilidade, performance e responsividade em pipeline.
