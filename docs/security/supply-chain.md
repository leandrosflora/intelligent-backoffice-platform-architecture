# Supply chain

## Gates do P7

- dependências Python com versão exata;
- imagem executada como UID/GID `10001`;
- target Kubernetes usa imagem por digest;
- SBOM CycloneDX;
- proveniência no formato in-toto/SLSA;
- evidências publicadas como artifact do GitHub Actions;
- policy de admissão alvo exige assinatura, SBOM e proveniência.

Gerar localmente:

```bash
python scripts/generate_sbom.py
python scripts/generate_provenance.py
python scripts/validate_p7.py --require-evidence
```

## Limite

A proveniência da baseline não é assinada criptograficamente. Produção deve usar assinatura keyless ou chave em KMS, registry attestations e admission controller que rejeite imagens sem evidência válida.
