# ADR-001 — Implementação de referência como monólito modular

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline local

## Contexto

A plataforma possui responsabilidades distintas para intake, workflow, inteligência documental, investigação, recomendação, aprovação, execução, evidências e auditoria. Separar todas essas responsabilidades em serviços independentes desde o primeiro vertical slice aumentaria o custo de deploy, testes, observabilidade, versionamento e diagnóstico antes de validar a jornada funcional.

A implementação de referência precisa demonstrar fronteiras arquiteturais e controles, não simular prematuramente uma operação distribuída de produção.

## Decisão

A baseline mínima será implementada como um monólito modular em FastAPI. As responsabilidades permanecem separadas por módulos, contratos, policies e testes, mas são empacotadas no mesmo processo para os profiles `runtime`, `observability` e `secure`.

Workers assíncronos podem executar em processos separados no profile `distributed`, compartilhando o mesmo modelo e armazenamento local.

Essa decisão não define a topologia produtiva e não autoriza acoplamento irrestrito entre módulos.

## Alternativas consideradas

### Microservices desde o início

Rejeitada porque introduziria complexidade operacional, rede, contratos distribuídos e troubleshooting sem evidência de escala ou ownership que justificasse a separação física.

### Aplicação sem fronteiras modulares

Rejeitada porque dificultaria a evolução para containers independentes, reduziria a rastreabilidade e misturaria responsabilidades sensíveis.

## Consequências

### Positivas

- reduz o custo para executar e validar a jornada ponta a ponta;
- mantém testes determinísticos e diagnóstico simples;
- permite comprovar policies, idempotência, eventos e observabilidade antes da distribuição;
- preserva fronteiras lógicas para evolução futura.

### Negativas e trade-offs

- falhas e escalabilidade continuam parcialmente compartilhadas;
- o deployment local não comprova independência operacional;
- disciplina de modularidade precisa ser mantida por código, contratos e revisão.

## Critérios de revisão

Revisar quando houver ownership independente, necessidades distintas de escala, isolamento regulatório, ciclos de release incompatíveis ou limites operacionais comprovados no monólito modular.

## Evidências e links

- [Implementação de referência](../implementation/index.md)
- [C4 containers atuais](../architecture/c4-container-current.md)
- [C4 containers alvo](../architecture/c4-container-target.md)
- `samples/vertical-slice/app/`
- `docker-compose.yml`
