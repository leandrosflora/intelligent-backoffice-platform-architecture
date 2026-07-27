# Runbook — workflow sem progresso

## Trigger

Caso permanece além do tempo esperado em um estado não terminal.

## Diagnóstico

1. Consulte timeline e última transição confirmada.
2. Verifique versão atual do aggregate e tentativas com `If-Match` antigo.
3. Confirme se a próxima ação foi negada pelo PDP.
4. Verifique dependências, timers e evidências obrigatórias.

## Mitigação

- repita apenas operações comprovadamente idempotentes;
- não altere estado diretamente no banco;
- reabra a ação por comando governado com correlação nova;
- escale para reconciliação quando houver side effect externo inconclusivo.
