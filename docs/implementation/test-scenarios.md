# Cenários testados

| Cenário | Resultado esperado |
|---|---|
| Jornada completa | Caso chega a `EXECUTED` |
| Repetição da mesma execução | Retorna o mesmo resultado |
| Mesma chave com payload diferente | `409 Conflict` |
| Leitura cross-tenant | `404 Not Found` |
| Autoaprovação | `403 Forbidden` |
| Versão obsoleta | `409 Conflict` |
| Resultado ambíguo | `RECONCILIATION_REQUIRED` |

Os testes usam dados sintéticos, SQLite temporário e policy embedded equivalente ao subconjunto exercitado. O runtime Docker utiliza OPA real.
