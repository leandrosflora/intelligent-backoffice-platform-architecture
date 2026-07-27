# ADR-009 — Evidências versionadas e auditoria append-only

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

Investigações, recomendações, aprovações e execuções precisam ser explicáveis e reconstruíveis. Manter apenas o estado final do caso não permite entender quais evidências foram usadas, quem tomou uma decisão ou qual versão estava vigente.

Documentos também são conteúdo não confiável e precisam de referências, checksums, versão e cadeia de custódia.

## Decisão

Toda transição relevante registra um evento de timeline com identidade, correlação, tipo, instante e payload mínimo. Evidências são referenciadas por identificadores versionados; conteúdo integral sensível não deve ser copiado indiscriminadamente para eventos, logs ou traces.

Na arquitetura-alvo, o Evidence Service preserva metadados, checksums e relações, enquanto o Audit Service consome eventos em modelo append-only. Correções geram novos registros e não apagam a história anterior.

## Alternativas consideradas

### Armazenar somente o estado atual

Rejeitada porque inviabiliza explicação, investigação de incidentes e auditoria de decisões.

### Atualizar eventos históricos

Rejeitada porque destrói a trilha original e dificulta provar integridade.

### Incluir documentos completos em eventos

Rejeitada por risco de exposição, tamanho, retenção e propagação de PII.

## Consequências

### Positivas

- reconstrução do lifecycle e das decisões;
- suporte a auditoria, investigação e contestação;
- vínculo entre recomendação, evidência e aprovação;
- correções preservam a história.

### Negativas e trade-offs

- aumenta volume e requisitos de retenção;
- exige políticas de acesso, minimização e expurgo;
- integridade e ordenação precisam ser verificadas.

## Critérios de revisão

Revisar quando houver requisitos formais de retenção, imutabilidade, WORM, assinatura, legal hold, privacidade ou integração com plataforma corporativa de auditoria.

## Evidências e links

- [Matriz de rastreabilidade](../functional/traceability-matrix.md)
- [Trust boundaries](../architecture/trust-boundaries.md)
- `samples/vertical-slice/app/store.py`
- `samples/vertical-slice/app/service.py`
- `contracts/schemas/event-envelope.yaml`
