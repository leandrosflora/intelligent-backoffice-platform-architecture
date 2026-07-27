# Requisitos não funcionais

Os valores são baselines de engenharia para o vertical slice e devem ser recalibrados para produção.

## Segurança e privacidade

| ID | Requisito |
|---|---|
| NFR-001 | Toda chamada interna propaga identidade do workload, tenant, finalidade e correlação. |
| NFR-002 | A decisão padrão de autorização é `DENY`. |
| NFR-003 | Dados sensíveis não são registrados integralmente em logs, traces ou eventos. |
| NFR-004 | Documentos permanecem em quarentena até os checks obrigatórios. |
| NFR-005 | Criptografia em trânsito é obrigatória fora do ambiente local. |
| NFR-006 | Evidências mantêm checksum, origem, versão, classificação e owner. |

## Confiabilidade e consistência

| ID | Requisito |
|---|---|
| NFR-007 | Comandos mutáveis são idempotentes e detectam conflito de payload. |
| NFR-008 | Estado e side effects são coordenados por Inbox/Outbox ou mecanismo equivalente. |
| NFR-009 | Eventos são processados ao menos uma vez com deduplicação no consumidor. |
| NFR-010 | Timeout após envio de comando mutável exige reconciliação. |
| NFR-011 | Atualizações concorrentes usam versionamento otimista do caso. |
| NFR-012 | Falha de policy ou identidade resulta em fail-closed. |

## Desempenho e escala

| ID | Baseline inicial |
|---|---|
| NFR-013 | criação ou consulta de caso p95 menor ou igual a 1 segundo, sem processamento documental síncrono |
| NFR-014 | decisão de policy p95 menor ou igual a 100 ms no ambiente de referência |
| NFR-015 | aceite de documento p95 menor ou igual a 2 segundos, com processamento assíncrono |
| NFR-016 | backlog e consumer lag observáveis por tenant e etapa |
| NFR-017 | limites de tamanho, quantidade e taxa de documentos configuráveis |

## Disponibilidade e recuperação

| ID | Baseline inicial |
|---|---|
| NFR-018 | disponibilidade mensal de 99,5% para APIs do piloto |
| NFR-019 | RPO menor ou igual a 15 minutos para dados do vertical slice |
| NFR-020 | RTO menor ou igual a 4 horas para o ambiente de demonstração |
| NFR-021 | restore testado em ambiente descartável antes de classificar o backup como válido |

## Observabilidade e auditoria

| ID | Requisito |
|---|---|
| NFR-022 | traces propagam `traceId`, `caseId`, `tenantId` e `correlationId` sem conteúdo sensível. |
| NFR-023 | cada transição publica métrica de duração, resultado e erro. |
| NFR-024 | decisões de agente, policy, humano e execução são distinguíveis. |
| NFR-025 | auditoria é append-only para consumidores comuns. |
| NFR-026 | alertas cobrem workflow parado, DLQ, falha de execução e reconciliação pendente. |

## Evolutividade e portabilidade

| ID | Requisito |
|---|---|
| NFR-027 | agentes dependem de contratos funcionais, não de payloads específicos de sistemas legados. |
| NFR-028 | modelos, prompts, policies e datasets são versionados independentemente. |
| NFR-029 | troca de provider ocorre por adapter ou gateway, sem alterar o lifecycle. |
| NFR-030 | contratos OpenAPI, AsyncAPI e policy são validados em CI. |
