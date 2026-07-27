# Intelligent Backoffice Platform Architecture

Arquitetura de referência executável para processos de backoffice regulados, documentais e de longa duração. A proposta combina workflow persistente, capacidades inteligentes, aprovação humana, policies, evidências e execução governada sem transferir decisões sensíveis para agentes.

[![Contexto atual da implementação de referência](assets/diagrams/c4-context-current.png)](assets/diagrams/c4-context-current.svg)

[**Abrir diagrama de contexto atual em SVG**](assets/diagrams/c4-context-current.svg)

## Problema que a arquitetura resolve

Processos de backoffice costumam atravessar documentos, múltiplos sistemas, regras operacionais, investigação, aprovação por alçada e execução financeira. Quando essas etapas ficam fragmentadas, aumentam o tempo de ciclo, o retrabalho, a inconsistência das decisões e o risco de perda de evidências.

A plataforma organiza essa jornada como um processo governado, observável e auditável.

## Princípios arquiteturais

1. **O workflow controla o processo.** Estado, timers, retries, compensações e transições não pertencem ao agente.
2. **A IA investiga e recomenda.** Agentes não aprovam nem executam operações mutáveis.
3. **Policies falham fechadas.** Alçada, segregação de funções, finalidade e autorização são verificadas antes da ação.
4. **Toda decisão relevante produz evidência.** Eventos, versões, tool calls, aprovações e resultados permanecem rastreáveis.
5. **Baseline e alvo são separados.** A implementação local demonstra padrões; a arquitetura-alvo descreve a evolução corporativa.

Os trade-offs e limites desses princípios estão registrados nos [Architecture Decision Records](decisions/index.md).

## O que funciona hoje

| Capacidade | Baseline executável | Limite declarado |
|---|---|---|
| Jornada de contestação | Vertical slice FastAPI com lifecycle persistido e walkthrough automatizado | Dados e integrações sintéticos |
| Aprovação e execução | Aprovação humana, OPA, execução mock idempotente e reconciliação | Sem efeito financeiro real |
| Processamento assíncrono | Outbox, inbox, workers, timers, DLQ e replay | SQLite e broker single-node |
| Observabilidade | Métricas, traces, dashboards, SLOs e alertas | Ambiente local sem operação 24x7 |
| Identidade e supply chain | JWT EdDSA local, SBOM e proveniência | Sem IAM, KMS e admission corporativos |
| Resiliência | Backup criptografado, restore e critérios de DR | Sem exercício regional real |

!!! danger "Status de produção"
    O estado oficial permanece **`NOT_PRODUCTION_READY`**. Controles demonstrados localmente não equivalem a implantação corporativa aprovada.

## Execute a implementação de referência

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

Profile com identidade assinada:

```bash
python scripts/generate_dev_identity.py --force
docker compose --profile secure up --build
python scripts/run_p7_secure_e2e.py
```

Consulte o [runbook local](implementation/runbook.md) para testes, health checks e reset do ambiente.

## Escolha sua trilha de leitura

A documentação possui percursos específicos para executivos, arquitetos, desenvolvedores, segurança, operações e auditoria.

[**Abrir o guia de leitura**](guide/how-to-read.md)

## Como interpretar as visões

| Visão | Pergunta respondida |
|---|---|
| [Walkthrough executável](tutorials/dispute-walkthrough.md) | Como a jornada e seus controles são comprovados ponta a ponta? |
| [Estado de implementação](architecture/implementation-status.md) | O que está demonstrado, contratado, planejado ou pendente para produção? |
| [Contexto atual](architecture/c4-context-current.md) | Quem utiliza e valida a implementação de referência hoje? |
| [Containers atuais](architecture/c4-container-current.md) | Quais processos, stores e ferramentas são executáveis nos profiles atuais? |
| [Architecture Decision Records](decisions/index.md) | Por que as principais decisões foram tomadas e quando devem ser revistas? |
| [Deployment observado](architecture/deployment-observed-baseline.md) | Como OPA, evals e observabilidade são executados localmente? |
| [Deployment distribuído](architecture/deployment-distributed-baseline.md) | Como outbox, eventing, workers, timers, DLQ e replay funcionam? |
| [Contexto alvo](architecture/c4-context-target.md) | Como a plataforma deve se posicionar no ecossistema corporativo? |
| [Containers alvo](architecture/c4-container-target.md) | Como as responsabilidades devem ser separadas na evolução da plataforma? |
| [Production readiness](governance/production-readiness.md) | Quais gates impedem a classificação como produção? |

## Próximos pontos de entrada

- [Walkthrough executável](tutorials/dispute-walkthrough.md)
- [Contexto de negócio](context/business-context.md)
- [Case aplicado](case-study/index.md)
- [Arquitetura funcional](functional/index.md)
- [Arquitetura técnica](architecture/index.md)
- [Decisões arquiteturais](decisions/index.md)
- [Contratos executáveis](contracts/index.md)
- [Implementação de referência](implementation/index.md)
- [Roadmap e histórico](roadmap.md)
