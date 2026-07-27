# Runbook — Dead letter e replay

## Pré-condições

- causa identificada e corrigida;
- impacto e tenant confirmados;
- operador com papel `platform-operator`;
- justificativa específica, sem dados sensíveis.

## Procedimento

1. consulte `/v1/operations/dead-letters`;
2. valide envelope, erro e número de tentativas;
3. registre a decisão operacional;
4. execute o endpoint de replay com a justificativa;
5. confirme novo `eventId`, `replayOf` e `replayCount`;
6. acompanhe outbox, inbox e projeção;
7. preserve a dead letter original como evidência.

Replay em massa não faz parte da baseline. Produção exige change record, limite de volume, janela e mecanismo de interrupção.
