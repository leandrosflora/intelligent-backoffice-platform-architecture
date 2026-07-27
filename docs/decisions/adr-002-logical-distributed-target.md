# ADR-002 — Arquitetura-alvo distribuída por responsabilidades lógicas

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Target corporativo

## Contexto

A evolução corporativa exige isolamento, escala, ownership e operação distintos para workflow, inteligência, políticas, execução, evidências, mensageria e observabilidade. Entretanto, representar responsabilidades como containers C4 não significa que cada container deva obrigatoriamente virar um microservice independente.

Uma decomposição física prematura criaria mais rede e operação sem dados suficientes sobre volumetria, criticidade e estrutura organizacional.

## Decisão

A arquitetura-alvo será descrita por responsabilidades lógicas independentes. A separação física ocorrerá apenas quando houver justificativa por escala, risco, ownership, disponibilidade, segurança ou ciclo de mudança.

Os containers C4 definem fronteiras de responsabilidade, contratos e dependências permitidas. Eles não são uma prescrição automática de quantidade de processos, clusters ou repositórios.

## Alternativas consideradas

### Um único serviço corporativo permanente

Rejeitada porque limita isolamento, escalabilidade e ownership para capacidades com perfis operacionais muito diferentes.

### Um microservice por container C4

Rejeitada como regra geral porque confunde modelagem lógica com topologia física e pode produzir fragmentação excessiva.

## Consequências

### Positivas

- mantém a arquitetura compreensível sem prescrever distribuição prematura;
- permite consolidar ou separar capacidades conforme evidências;
- preserva contratos e ownership mesmo quando há coimplantação.

### Negativas e trade-offs

- exige governança para evitar fronteiras apenas nominais;
- a topologia final depende de decisões posteriores de plataforma e operação;
- algumas integrações podem mudar de chamada local para rede.

## Critérios de revisão

Revisar a decomposição quando surgirem dados de capacidade, SLOs, domínios de falha, requisitos regulatórios, ownership formal ou restrições de deploy.

## Evidências e links

- [C4 containers alvo](../architecture/c4-container-target.md)
- [Estado de implementação](../architecture/implementation-status.md)
- [Deployment alvo de produção](../architecture/deployment-production-target.md)
