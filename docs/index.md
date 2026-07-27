# Intelligent Backoffice Platform Architecture

Arquitetura de referência executável para processos de backoffice regulados, documentais e de longa duração. A proposta combina workflow persistente, capacidades inteligentes, aprovação humana, policies, evidências e execução governada sem transferir decisões sensíveis para agentes.

[![Contexto alvo da plataforma](assets/diagrams/c4-context-target.png)](assets/diagrams/c4-context-target.svg)

[**Abrir diagrama de contexto em SVG**](assets/diagrams/c4-context-target.svg)

## Problema que a arquitetura resolve

Processos de backoffice costumam atravessar documentos, múltiplos sistemas, regras operacionais, investigação, aprovação por alçada e execução financeira. Quando essas etapas ficam fragmentadas, aumentam o tempo de ciclo, o retrabalho, a inconsistência das decisões e o risco de perda de evidências.

A plataforma organiza essa jornada como um processo governado, observável e auditável.

## Princípios arquiteturais

1. **O workflow controla o processo.** Estado, timers, retries, compensações e transições não pertencem ao agente.
2. **A IA investiga e recomenda.** Agentes não aprovam nem executam operações mutáveis.
3. **Policies falham fechadas.** Alçada, segregação de funções, finalidade e autorização são verificadas antes da ação.
4. **Toda decisão relevante produz evidência.** Eventos, versões, tool calls, aprovações e resultados permanecem rastreáveis.
5. **Baseline e alvo são separados.** A implementação local demonstra padrões; a arquitetura-alvo descreve a evolução corporativa.

## O que funciona hoje

| Capacidade | Baseline executável | Limite declarado |
|---|---|---|
| Jornada de contestação | Vertical slice FastAPI com lifecycle persistido | Dados e integrações sintéticos |
| Aprovação e execução | Aprovação humana, OPA e execução mock idempotente | Sem efeito financeiro real |
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

Workflow distribuído:

```bash
docker compose --profile distributed up --build
python scripts/run_p6_distributed_e2e.py
```

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
| [Deployment observado](architecture/deployment-observed-baseline.md) | Qual runtime modular está confirmado com OPA, evals e observabilidade? |
| [Deployment distribuído](architecture/deployment-distributed-baseline.md) | Quais capacidades assíncronas estão demonstradas? |
| [Contexto alvo](architecture/c4-context-target.md) | Como a plataforma se posiciona no ecossistema corporativo? |
| [Containers alvo](architecture/c4-container-target.md) | Como as responsabilidades devem ser separadas na evolução da plataforma? |
| [Production readiness](governance/production-readiness.md) | Quais gates impedem a classificação como produção? |

!!! info "Visões C4 atuais"
    Os diagramas C4 chamados de atuais ainda registram o estado documental inicial do repositório. Os deployments observado e distribuído são a fonte de leitura da baseline executável até a atualização semântica desses diagramas.

## Próximos pontos de entrada

- [Contexto de negócio](context/business-context.md)
- [Case aplicado](case-study/index.md)
- [Arquitetura funcional](functional/index.md)
- [Arquitetura técnica](architecture/index.md)
- [Contratos executáveis](contracts/index.md)
- [Implementação de referência](implementation/index.md)
- [Roadmap e histórico](roadmap.md)