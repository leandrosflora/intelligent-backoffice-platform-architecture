# Mapa de domínios

## Domínios principais

| Domínio | Responsabilidade | Dados sob ownership |
|---|---|---|
| Case Management | Identidade, estado e timeline do caso | caso, estado, prioridade, SLA, responsáveis |
| Document Processing | Recepção e processamento técnico dos documentos | documento, versão, classificação, extração |
| Evidence Management | Cadeia de custódia e vínculo entre fato e decisão | evidência, origem, checksum, validade, relações |
| Investigation | Consolidação de consultas e fatos relevantes | consulta, finding, inconsistência, pendência |
| Decision Support | Recomendação explicável e nível de confiança | recomendação, justificativa, regras aplicadas |
| Human Approval | Tarefas humanas, alçada e decisão final | tarefa, aprovador, decisão, motivo, prazo |
| Governed Execution | Execução da decisão em sistemas de registro | comando, idempotência, resultado, reconciliação |

## Domínios de suporte

| Domínio | Responsabilidade |
|---|---|
| Knowledge | Políticas, procedimentos e regras aprovadas |
| Identity and Policy | Identidade, tenant, autorização e obrigações |
| Audit and Compliance | Eventos de auditoria e evidências regulatórias |
| Notification | Comunicação com canais e usuários |
| Evaluation | Datasets, resultados, thresholds e regressões |
| Platform Operations | SLOs, incidentes, capacidade e custos |

## Relações entre domínios

```text
Case Management
    ├── solicita processamento a Document Processing
    ├── referencia evidências em Evidence Management
    ├── aciona Investigation
    ├── solicita recomendação a Decision Support
    ├── cria tarefa em Human Approval
    └── solicita execução a Governed Execution

Identity and Policy controla todas as chamadas.
Audit and Compliance recebe eventos de todos os domínios.
```

## Regras de acoplamento

- cada domínio possui contrato próprio e não compartilha banco como integração;
- o identificador do caso é a correlação funcional principal;
- documentos não são copiados para payloads de eventos;
- decisões referenciam evidências por identificador e versão;
- agentes consomem portas funcionais, nunca payloads legados diretamente;
- Governed Execution é o único domínio autorizado a produzir efeito financeiro.
