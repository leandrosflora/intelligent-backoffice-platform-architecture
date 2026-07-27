# Segurança

## Princípios

- default deny;
- identidade de usuário e workload propagada ponta a ponta;
- isolamento por tenant e finalidade;
- ferramentas permitidas por estágio e papel;
- documentos tratados como conteúdo não confiável;
- nenhuma credencial ou payload sensível em logs e eventos;
- ações financeiras exigem evidência, aprovação e idempotência;
- falha do policy decision point resulta em fail closed.

A evolução produtiva deverá incluir identidade nativa de workload, KMS/HSM, rotação, revogação, mTLS e policies assinadas.
