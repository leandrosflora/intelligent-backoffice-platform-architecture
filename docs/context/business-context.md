# Contexto de negócio

## Problema

Processos de contestação bancária dependem de documentos, consultas a diferentes sistemas, regras operacionais, análise humana, aprovação por alçada e execução financeira. Quando essas etapas são conduzidas de forma fragmentada, aumentam o tempo de ciclo, o retrabalho, a inconsistência das decisões e o risco de perda de evidências.

## Hipótese de valor

Uma plataforma compartilhada de backoffice pode combinar workflow persistente, document intelligence, agentes especializados, políticas, aprovação humana e execução governada para reduzir esforço operacional sem remover controles críticos.

## Outcome principal

> Reduzir o tempo e o esforço para tratar contestações, mantendo decisões explicáveis, segregação de funções, evidências completas e execução financeira controlada.

## Atores

| Ator | Responsabilidade principal |
|---|---|
| Cliente ou canal de origem | Abrir a contestação e fornecer documentos |
| Analista de operações | Investigar o caso e complementar evidências |
| Aprovador | Aceitar ou rejeitar a recomendação conforme alçada |
| Gestor de operações | Responder pelo outcome e capacidade operacional |
| Auditoria e compliance | Verificar aderência, evidências e segregação de funções |
| Sistemas corporativos | Fornecer transações, cadastro, fraude, CRM e execução financeira |
| Plataforma de IA | Disponibilizar capacidades compartilhadas e controles técnicos |

## Escopo do primeiro case

- abertura e triagem de uma contestação;
- recebimento de documentos sintéticos;
- classificação e extração de evidências;
- consulta a sistemas mock;
- investigação assistida;
- recomendação de decisão;
- aprovação humana obrigatória;
- execução somente em sistema mock;
- timeline, auditoria e encerramento do caso.

## Fora do escopo inicial

- decisão financeira totalmente autônoma;
- integração com Core bancário produtivo;
- uso de documentos reais de clientes;
- OCR ou modelo multimodal específico de fornecedor;
- reconciliação financeira produtiva;
- substituição do sistema oficial de gestão de casos.

## Restrições e premissas

- agentes não acessam diretamente sistemas de registro;
- qualquer operação mutável exige idempotência;
- recomendações não equivalem a decisões aprovadas;
- aprovação, execução e auditoria são responsabilidades distintas;
- o MVP usa dados sintéticos e integrações mock;
- documentos e evidências são tratados como conteúdo não confiável;
- toda transição relevante produz evento e evidência auditável.

## Critérios para avançar além do MVP

1. baseline operacional medida;
2. regras de negócio aprovadas pelo owner;
3. threat model e privacy assessment concluídos;
4. dataset de avaliação versionado;
5. segregação de funções testada;
6. idempotência e retry validados;
7. runbooks e rollback publicados;
8. aprovação formal para uso de dados e integrações reais.
