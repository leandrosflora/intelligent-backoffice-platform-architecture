# Classificação de risco

## Classificação por estágio

| Estágio | Classificação | Justificativa |
|---|---|---|
| Documentação e contratos | Baixo | Não processa dados reais nem executa ações |
| Vertical slice sintético com Core mock | Médio | Demonstra decisões e controles, sem efeito financeiro real |
| Piloto com dados mascarados e aprovação humana | Alto | Processa dados sensíveis e influencia decisão regulada |
| Produção com execução financeira | Alto | Pode gerar impacto financeiro, regulatório e reputacional |

## Fatores de risco do case

- dados pessoais e financeiros;
- documentos potencialmente maliciosos;
- decisão com impacto ao cliente;
- integração com sistemas de registro;
- possibilidade de fraude e conflito de evidências;
- dependência de modelos probabilísticos;
- long-running workflow e retries;
- exigência de explicabilidade e auditoria.

## Controles obrigatórios para o MVP

| Risco | Controle |
|---|---|
| Acesso indevido | tenant assinado, autorização default deny e testes negativos |
| Prompt injection documental | quarentena, delimitação de conteúdo e política de não execução de instruções do documento |
| Recomendação sem suporte | citações de evidência, groundedness e abstention |
| Conflito de funções | identidade do recomendador e aprovador comparada por policy |
| Duplicidade financeira | idempotência, hash do comando e replay controlado |
| Resultado ambíguo | estado `RECONCILIATION_REQUIRED` e bloqueio de retry cego |
| Vazamento em telemetria | redaction e proibição de payload integral por padrão |
| Regressão de modelo ou prompt | dataset versionado e gate de avaliação |

## Gates antes de produção

1. integração com identidade corporativa de workload;
2. KMS/HSM, rotação e revogação;
3. contrato certificado com sistema de registro;
4. idempotência persistente e reconciliação comprovadas;
5. threat model, DPIA/LGPD e retenção aprovados;
6. SLOs, plantão e runbooks testados;
7. evals online e monitoramento de qualidade;
8. segregação de funções validada ponta a ponta;
9. artifacts assinados, SBOM e proveniência;
10. owner formal para risco residual.
