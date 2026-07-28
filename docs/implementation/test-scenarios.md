# Cenários testados

| Cenário | Resultado esperado |
|---|---|
| Jornada completa | Caso chega a `EXECUTED` e execução a `SUCCEEDED` |
| Consulta da execução | Retorna status e identificador da execução do tenant |
| Repetição da mesma execução | Retorna exatamente o mesmo resultado |
| Mesma chave de execução com payload diferente | `409 Conflict` |
| Leitura cross-tenant | `404 Not Found` |
| Autoaprovação | `403 Forbidden` |
| Versão obsoleta | `409 Conflict` |
| Resultado ambíguo | Caso e execução chegam a `RECONCILIATION_REQUIRED` |
| Reconciliação confirmada | Caso retorna a `EXECUTED` e execução fica `RECONCILED` |
| Repetição da mesma reconciliação | Retorna exatamente o mesmo resultado |
| Reconciliação sem papel `reconciler` | `403 Forbidden` |
| Outbox e projeção | Eventos da jornada ficam `PUBLISHED` e processados pelo consumer |

Os testes unitários usam dados sintéticos, SQLite temporário e policy embedded equivalente ao subconjunto exercitado. O runtime Docker utiliza OPA real.

O [walkthrough executável](../tutorials/dispute-walkthrough.md) roda no profile distribuído e adiciona evidências de API, timeline, outbox, projeções e métricas.
