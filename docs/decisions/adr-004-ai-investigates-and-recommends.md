# ADR-004 — IA investiga e recomenda, mas não aprova nem executa

- **Status:** Aceito
- **Data:** 2026-07-27
- **Decisores:** Architecture Review Board
- **Escopo:** Baseline e target

## Contexto

A plataforma usa capacidades inteligentes para classificar documentos, reunir evidências e produzir recomendações. Em processos financeiros e regulados, análise probabilística não deve equivaler a decisão autorizada nem a efeito mutável em sistema de registro.

## Decisão

A IA pode classificar, extrair, investigar, sintetizar e recomendar. Ela não pode aprovar a própria recomendação, alterar diretamente o lifecycle nem executar operações mutáveis em sistemas de registro.

Resultados inteligentes devem incluir evidências, versão, explicação suficiente e `ABSTAIN` quando o grounding for insuficiente. A progressão do processo permanece sob autoridade do workflow, das policies e das pessoas responsáveis.

## Alternativas consideradas

### Decisão autônoma de baixo valor

Rejeitada na baseline por ausência de dados reais, avaliação representativa, autorização regulatória e critérios formais de risco.

### Agente com acesso direto aos sistemas corporativos

Rejeitada porque elimina mediação por policy, idempotência, reconciliação e segregação de responsabilidades.

## Consequências

### Positivas

- reduz risco de efeito indevido ou não explicável;
- permite substituir modelos sem alterar a autoridade do processo;
- cria espaço para abstention e revisão humana;
- mantém evidências ligadas à recomendação.

### Negativas e trade-offs

- preserva etapas humanas e pode limitar automação total;
- exige contratos explícitos entre IA, workflow e aprovação;
- qualidade da recomendação precisa ser medida continuamente.

## Critérios de revisão

Qualquer ampliação de autonomia exige risk assessment, base legal, dataset representativo, thresholds aprovados, mecanismo de contestação, monitoramento, rollback e autorização formal do processo.

## Evidências e links

- [Princípio central](../functional/index.md)
- [Classificação de risco](../functional/risk-classification.md)
- [Avaliação das capacidades inteligentes](../evaluation/index.md)
- `samples/vertical-slice/app/intelligence.py`
- `evals/datasets/intelligence-v1.jsonl`
