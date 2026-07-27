# Outcome card

## Hipótese inicial

| Campo | Definição |
|---|---|
| Objetivo estratégico | Aumentar capacidade e controle do backoffice sem crescimento proporcional do esforço manual |
| Problema | Tratamento fragmentado, alto tempo de ciclo, retrabalho e baixa rastreabilidade |
| Outcome | Reduzir tempo e esforço por contestação mantendo qualidade, compliance e segurança |
| População inicial | Casos sintéticos de contestação em ambiente de demonstração |
| Horizonte de validação | 60 a 90 dias após o início do piloto funcional |
| Owner | Gestor do processo de contestação |
| Decisão esperada | Escalar, ajustar, pausar ou descontinuar com base em evidências |

## Baseline

A baseline real ainda não foi fornecida. Antes do piloto devem ser medidos:

- tempo mediano e p95 do processo;
- quantidade de handoffs;
- horas humanas por caso;
- taxa de retrabalho e reabertura;
- percentual de casos com documentação incompleta;
- taxa de erro operacional;
- custo estimado por caso;
- reclamações e violações de prazo.

## Targets provisórios

Os targets abaixo são hipóteses e precisam ser calibrados após a baseline:

| Indicador | Hipótese inicial |
|---|---|
| Tempo mediano de ciclo | redução de pelo menos 30% |
| Esforço manual por caso | redução de pelo menos 25% |
| Retrabalho documental | redução de pelo menos 40% |
| Casos com evidência completa | pelo menos 95% |
| Acesso cross-tenant | zero ocorrência permitida |
| Execução duplicada | zero ocorrência permitida |
| Decisão sem aprovação obrigatória | zero ocorrência permitida |

## Leading indicators

- percentual de documentos classificados automaticamente;
- percentual de extrações aceitas sem correção;
- tempo para identificar evidência ausente;
- task success do agente de investigação;
- recomendações aceitas pelo aprovador;
- tempo em cada estado do lifecycle;
- taxa de conclusão sem intervenção operacional técnica.

## Guardrails

- nenhuma decisão financeira autônoma no MVP;
- zero acesso não autorizado;
- zero efeito financeiro duplicado;
- abstention quando não houver evidência;
- custo por caso dentro do budget aprovado;
- proteção de PII em logs, traces e eventos;
- aprovação humana e segregação de funções verificáveis.

## Evidências de valor

- eventos de lifecycle;
- dados do Case Management;
- tarefas humanas e decisões;
- resultados de document intelligence;
- evals e testes negativos;
- métricas de execução e reconciliação;
- pesquisa com analistas e aprovadores.
