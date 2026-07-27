# Catálogo de responsabilidades

Os nomes abaixo representam responsabilidades lógicas da plataforma. Na baseline local, várias delas são consolidadas no mesmo processo FastAPI; na arquitetura-alvo, podem ser separadas conforme escala, risco, ownership e requisitos operacionais.

| Responsabilidade | Função principal | Forma na baseline local |
|---|---|---|
| Case Intake | Receber e normalizar solicitações e documentos | Módulo da API FastAPI |
| Workflow Orchestrator | Manter estado, timers, retries e compensações | Módulo persistente e workers |
| Document Intelligence | Classificar, extrair e validar documentos | Implementação determinística mock |
| Investigation Agent Runtime | Reunir evidências e executar consultas autorizadas | Implementação determinística mock |
| Decision Support Agent Runtime | Produzir recomendação explicável | Implementação determinística com abstention |
| Backoffice Tool Gateway | Expor ferramentas governadas por MCP ou API | Contratos e adapters mock |
| Human Approval | Registrar aprovação, rejeição e justificativa | Endpoints e regras do vertical slice |
| Governed Execution | Executar ações autorizadas e idempotentes | Serviço de domínio contra sistema mock |
| Evidence | Armazenar referências e versões das evidências | Persistência e timeline locais |
| Audit | Manter trilha imutável da jornada | Eventos e timeline append-only |
| Policy Decision Point | Aplicar autorização, alçada e segregação | OPA externo ao processo |
| Event Backbone | Entregar eventos, retries, DLQ e replay | Redpanda single-node e workers |

## Regra de decomposição

A separação em processos independentes não é objetivo por si só. Uma responsabilidade deve ser extraída quando houver justificativa clara de escala, isolamento, segurança, ownership, disponibilidade ou ritmo de mudança.

Consulte os [containers alvo](../architecture/c4-container-target.md) para a decomposição lógica e a [implementação de referência](../implementation/index.md) para o empacotamento atual.