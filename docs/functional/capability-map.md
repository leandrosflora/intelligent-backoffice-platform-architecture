# Mapa de capacidades

## Capacidades de negócio

| ID | Capacidade | Resultado esperado |
|---|---|---|
| CAP-001 | Intake e triagem | Registrar o caso e direcionar o tratamento correto |
| CAP-002 | Gestão documental | Receber, classificar, extrair e validar documentos |
| CAP-003 | Gestão de evidências | Preservar origem, integridade, versão e relação com a decisão |
| CAP-004 | Investigação | Consultar fontes autorizadas e consolidar fatos do caso |
| CAP-005 | Recomendação assistida | Propor decisão explicável com regras e evidências |
| CAP-006 | Aprovação humana | Aplicar alçada, segregação e registro da decisão humana |
| CAP-007 | Execução governada | Executar a decisão aprovada com idempotência e reconciliação |
| CAP-008 | Comunicação | Informar andamento, pendências e resultado aos canais autorizados |
| CAP-009 | Auditoria e compliance | Demonstrar quem fez o quê, quando, por quê e com qual evidência |
| CAP-010 | Gestão operacional | Medir backlog, tempo de ciclo, qualidade, risco e custo |

## Capacidades de plataforma

| ID | Capacidade | Responsabilidade |
|---|---|---|
| PLT-001 | Workflow orchestration | Estado persistente, timers, retries, compensações e retomada |
| PLT-002 | Agent runtime | Execução controlada de agentes de investigação e recomendação |
| PLT-003 | Document intelligence | Classificação, extração, validação e detecção de conteúdo malicioso |
| PLT-004 | Knowledge service | Recuperação de políticas e procedimentos autorizados |
| PLT-005 | Tool execution | Acesso governado a APIs por contratos e identidade de workload |
| PLT-006 | Policy enforcement | Decisão default deny, obrigações e segregação de funções |
| PLT-007 | Human task management | Criação, atribuição, prazo e resolução de tarefas humanas |
| PLT-008 | Evidence store | Armazenamento versionado e verificável de evidências |
| PLT-009 | Event backbone | Eventos duráveis, correlação, replay e integração assíncrona |
| PLT-010 | Evaluation | Testes determinísticos, evals de IA e gates de release |
| PLT-011 | Observability | Logs, métricas, traces, alertas e SLOs |
| PLT-012 | Audit | Trilha imutável com proteção de dados sensíveis |
| PLT-013 | FinOps | Custo por caso, agente, modelo, documento e tenant |

## Mapeamento inicial

| Outcome | Capacidades prioritárias |
|---|---|
| Reduzir tempo de ciclo | CAP-001, CAP-002, CAP-004, PLT-001, PLT-003 |
| Reduzir retrabalho | CAP-003, CAP-005, PLT-004, PLT-010 |
| Controlar risco financeiro | CAP-006, CAP-007, PLT-005, PLT-006 |
| Aumentar auditabilidade | CAP-003, CAP-009, PLT-008, PLT-012 |
| Escalar para novos processos | PLT-001, PLT-002, PLT-005, PLT-009 |
