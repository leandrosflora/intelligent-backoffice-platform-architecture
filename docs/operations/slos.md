# SLOs e alertas

Os targets são provisórios para a baseline executável e devem ser recalibrados com carga e operação representativas.

| SLO | Target inicial | Runbook |
|---|---:|---|
| Disponibilidade da API | 99,9% | Erros e latência |
| Latência protegida | p95 abaixo de 500 ms | Erros e latência |
| Disponibilidade do PDP | 99,95% | PDP indisponível |
| Duplicidade de execução | zero | Execução ambígua |
| Qualidade de eval | 100% no dataset v1 | Regressão de eval |
| Entrega de eventos | 99,9% sem DLQ durável | Backlog no outbox |
| Timers | disparo em até 60 segundos do prazo | Timer parado |

## Alertas P6

- backlog de mensagens `PENDING` ou `RETRY` no outbox;
- dead letters abertas;
- timers agendados ou em retry além da janela operacional.

Os alerts operacionais não autorizam replay automático. O replay permanece uma ação governada.
