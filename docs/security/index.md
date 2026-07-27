# Segurança

## Princípios

- `default deny`;
- identidade assinada de usuário e workload;
- tenant, papéis e finalidade derivados de claims confiáveis;
- nenhuma credencial em código, logs ou eventos;
- segredos fornecidos por serviço externo e chaves protegidas por KMS/HSM;
- imagens sem privilégios e políticas de rede restritivas;
- ações financeiras exigem evidência, aprovação e idempotência;
- falha do policy decision point resulta em `fail closed`.

## P7

O P7 adiciona uma baseline verificável para:

- [identidade de workload](workload-identity.md);
- [segredos e KMS](secrets-and-kms.md);
- [supply chain](supply-chain.md);
- policy OPA com `purpose binding`;
- imagem executada como usuário não root;
- deployment Kubernetes alvo com security context e `NetworkPolicy`.

A baseline local não substitui OIDC corporativo, SPIFFE, mTLS, secret manager, KMS ou admission control produtivo.
