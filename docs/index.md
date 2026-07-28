# Intelligent Backoffice Platform Architecture

Arquitetura de referência executável para processos de backoffice regulados, documentais e de longa duração. A proposta combina workflow persistente, capacidades inteligentes, aprovação humana, policies, evidências e execução governada sem transferir decisões sensíveis para agentes.

[![Contexto atual do ecossistema](assets/diagrams/c4-context-current.png)](assets/diagrams/c4-context-current.svg)

[**Abrir diagrama de contexto atual em SVG**](assets/diagrams/c4-context-current.svg)

## Ecossistema atual

A solução passa a ter três trilhas de entrega:

| Trilha | Repositório | Estado |
|---|---|---|
| Arquitetura e baseline | `intelligent-backoffice-platform-architecture` | `DEMONSTRATED_LOCAL` / `CONTRACT_DEFINED` |
| Backend de produto | `backoffice-platform-api` | `IMPLEMENTATION_STARTED` |
| Frontend de produto | `intelligent-backoffice-frontend` | `IMPLEMENTATION_STARTED` |

O backend .NET e o frontend React já possuem código inicial. A integração conjunta entre frontend, API, PostgreSQL e OPA ainda precisa de um gate E2E cross-repo para avançar a `VALIDATED_INTEGRATION`.

[**Abrir o mapa dos repositórios de produto**](implementation/product-repositories.md)

## Problema que a arquitetura resolve

Processos de backoffice costumam atravessar documentos, múltiplos sistemas, regras operacionais, investigação, aprovação por alçada e execução financeira. Quando essas etapas ficam fragmentadas, aumentam o tempo de ciclo, o retrabalho, a inconsistência das decisões e o risco de perda de evidências.

A plataforma organiza essa jornada como um processo governado, observável e auditável.

## Princípios arquiteturais

1. **O workflow controla o processo.** Estado, timers, retries, compensações e transições não pertencem ao agente.
2. **A IA investiga e recomenda.** Agentes não aprovam nem executam operações mutáveis.
3. **Policies falham fechadas.** Alçada, segregação de funções, finalidade e autorização são verificadas antes da ação.
4. **Toda decisão relevante produz evidência.** Eventos, versões, tool calls, aprovações e resultados permanecem rastreáveis.
5. **Baseline e produto são separados.** A implementação local demonstra padrões; os repositórios de produto materializam a evolução real.

Os trade-offs e limites desses princípios estão registrados nos [Architecture Decision Records](decisions/index.md).

## O que funciona na baseline

| Capacidade | Baseline executável | Limite declarado |
|---|---|---|
| Jornada de contestação | Vertical slice FastAPI com lifecycle persistido e walkthrough automatizado | Dados e integrações sintéticos |
| Aprovação e execução | Aprovação humana, OPA, execução mock idempotente e reconciliação | Sem efeito financeiro real |
| Processamento assíncrono | Outbox, inbox, workers, timers, DLQ e replay | SQLite e broker single-node |
| Observabilidade | Métricas, traces, dashboards, SLOs e alertas | Ambiente local sem operação 24x7 |
| Identidade e supply chain | JWT EdDSA local, SBOM e proveniência | Sem IAM, KMS e admission corporativos |
| Resiliência | Backup criptografado, restore e critérios de DR | Sem exercício regional real |

## O que começou no produto

| Componente | Implementação inicial |
|---|---|
| Backend .NET | Casos, documentos, evidências, investigação, recomendação, aprovação, execução, reconciliação, PostgreSQL e OPA externo |
| Frontend React | Criação e consulta de casos, jornada guiada, identidades da baseline, evidências, execuções, timeline e console HTTP |

!!! danger "Status de produção"
    O estado oficial permanece **`NOT_PRODUCTION_READY`**. Código implementado não equivale a integração validada ou implantação corporativa aprovada.

## Execute a baseline de arquitetura

Runtime mínimo:

```bash
docker compose --profile runtime up --build
```

Walkthrough completo no profile distribuído:

```bash
docker compose --profile distributed up -d --build
python scripts/run_dispute_walkthrough.py
```

O roteiro valida a jornada principal, uma execução ambígua, a reconciliação, a timeline, o outbox, as projeções e as métricas.

[**Abrir o walkthrough executável**](tutorials/dispute-walkthrough.md)

## Execute os repositórios de produto

Backend:

```bash
cd backoffice-platform-api
docker compose --profile runtime up -d postgres
dotnet run --project src/Backoffice.Api
```

Frontend:

```bash
cd intelligent-backoffice-frontend/intelligent-backoffice-frontend
npm ci
npm run dev
```

A API utiliza `http://localhost:5260`; o frontend utiliza `http://localhost:5173`. Operações governadas dependem de um PDP OPA compatível.

## Escolha sua trilha de leitura

A documentação possui percursos específicos para executivos, arquitetos, desenvolvedores, segurança, operações e auditoria.

[**Abrir o guia de leitura**](guide/how-to-read.md)

## Como interpretar as visões

| Visão | Pergunta respondida |
|---|---|
| [Repositórios de produto](implementation/product-repositories.md) | Como arquitetura, backend e frontend se relacionam e qual é o próximo gate? |
| [Walkthrough executável](tutorials/dispute-walkthrough.md) | Como a baseline e seus controles são comprovados ponta a ponta? |
| [Estado de implementação](architecture/implementation-status.md) | O que está contratado, iniciado, demonstrado, integrado ou pendente para produção? |
| [Contexto atual](architecture/c4-context-current.md) | Quem utiliza e evolui o ecossistema atual? |
| [Containers atuais](architecture/c4-container-current.md) | Quais containers pertencem ao produto em construção e à baseline? |
| [Architecture Decision Records](decisions/index.md) | Por que as principais decisões foram tomadas e quando devem ser revistas? |
| [Contexto alvo](architecture/c4-context-target.md) | Como a plataforma deve se posicionar no ecossistema corporativo? |
| [Production readiness](governance/production-readiness.md) | Quais gates impedem a classificação como produção? |

## Próximos pontos de entrada

- [Repositórios de implementação do produto](implementation/product-repositories.md)
- [Walkthrough executável](tutorials/dispute-walkthrough.md)
- [Contexto de negócio](context/business-context.md)
- [Case aplicado](case-study/index.md)
- [Arquitetura funcional](functional/index.md)
- [Arquitetura técnica](architecture/index.md)
- [Decisões arquiteturais](decisions/index.md)
- [Contratos executáveis](contracts/index.md)
- [Implementação de referência](implementation/index.md)
- [Roadmap e histórico](roadmap.md)
