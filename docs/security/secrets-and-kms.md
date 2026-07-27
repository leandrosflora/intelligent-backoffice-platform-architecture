# Segredos e KMS

## Inventário

`security/secrets/inventory.yaml` registra finalidade, owner, consumidores, origem e rotação. Valores de segredo são proibidos no repositório.

## Baseline local

O P7 gera materiais efêmeros em `.local/security/`:

```bash
python scripts/generate_dev_identity.py
python scripts/generate_dev_kms_key.py
```

`.local/` é protegido por `.local/.gitignore`.

O drill de backup usa AES-256-GCM, separa a chave do backup, valida SHA-256 e executa `PRAGMA integrity_check` após o restore:

```bash
python scripts/backup_restore_drill.py \
  --database artifacts/drill-source.db \
  --key-file .local/security/backup-aes256.key
```

## Produção

- secret manager externo;
- KMS/HSM com separação entre administração e uso;
- data keys por envelope encryption;
- auditoria de `encrypt`, `decrypt` e rotação;
- cópia cross-region da chave quando aprovada;
- nenhum segredo estático em `ConfigMap`, imagem ou manifesto.
