# Alta disponibilidade, backup e disaster recovery

## Alta disponibilidade

O target Kubernetes define:

- mínimo de três réplicas;
- distribuição por zona e anti-affinity por host;
- `PodDisruptionBudget` com duas réplicas disponíveis;
- rolling update sem indisponibilidade planejada;
- HPA entre três e doze réplicas;
- probes de liveness e readiness;
- requests e limits;
- execução non-root e filesystem somente leitura.

## Backup local comprovado

A pipeline cria estado sintético, produz snapshot consistente, criptografa com AES-256-GCM, restaura e valida integridade e contagem de tabelas.

## DR alvo

`resilience/dr-plan.yaml` define warm standby cross-region, RPO/RTO, autoridade de ativação, cenários de exercício e reconciliação antes do failback.

## Critério

A documentação e o drill local não satisfazem produção. O gate só pode ser aprovado após exercício real em infraestrutura corporativa e medição do RPO/RTO.
