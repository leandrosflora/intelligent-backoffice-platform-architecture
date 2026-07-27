# Papéis e responsabilidades

## Papéis funcionais

| Papel | Responsabilidades | Restrições |
|---|---|---|
| Business Owner | Outcome, prioridade, regras e decisão de escala | Não administra controles técnicos isoladamente |
| Case Manager | Estado, SLA, atribuição e exceções do caso | Não executa efeito financeiro direto |
| Operations Analyst | Investigação, complementação e recomendação manual | Não aprova recomendação própria |
| Human Approver | Decisão conforme alçada e evidências | Não altera evidências nem executa transação |
| Auditor | Consulta timeline, decisões e evidências | Somente leitura e finalidade autorizada |
| Data Owner | Classificação, retenção e qualidade das fontes | Não aprova ação financeira por padrão |

## Papéis técnicos

| Papel | Responsabilidades |
|---|---|
| Platform Owner | Capacidades compartilhadas, golden paths e roadmap |
| Service Owner | Contrato, disponibilidade, segurança e operação do serviço |
| Security and Privacy | Threat model, policies, proteção de dados e incidentes |
| SRE | SLOs, alertas, capacidade, recuperação e runbooks |
| Model or Agent Owner | Prompt, tools, dataset, evals e versão publicada |
| Compliance Owner | Requisitos regulatórios, evidências e revisões periódicas |

## Segregação mínima

| Ação | Agente | Analista | Aprovador | Execution Service | Auditor |
|---|---:|---:|---:|---:|---:|
| Classificar documento | Sim | Sim | Não | Não | Leitura |
| Consultar sistemas | Sim, via tool | Sim | Leitura | Não | Leitura autorizada |
| Criar recomendação | Sim | Sim | Não | Não | Leitura |
| Aprovar decisão | Não | Condicional, sem conflito | Sim | Não | Não |
| Executar decisão | Não | Não | Não | Sim | Não |
| Alterar auditoria | Não | Não | Não | Não | Não |

## RACI do lifecycle

| Etapa | Business Owner | Case Manager | Analyst | Approver | Platform/Service Owners |
|---|---|---|---|---|---|
| Definir regras | A | C | C | C | R técnico |
| Abrir e triar caso | I | A/R | C | I | C |
| Processar documentos | I | A | C | I | R técnico |
| Investigar | I | A | R | I | C |
| Recomendar | I | A | R | C | C |
| Aprovar | I | C | C | A/R | C |
| Executar | I | A | I | C | R técnico |
| Operar e recuperar | I | C | I | I | A/R |
| Revisar valor | A/R | C | C | C | C |

Legenda: **R** responsável pela execução, **A** accountable, **C** consultado, **I** informado.
