# Runbook local

## Subir o ambiente

```bash
docker compose --profile runtime up --build
```

## Verificar saúde

```bash
curl http://localhost:8080/health
curl http://localhost:8181/health
```

## Executar testes

```bash
cd samples/vertical-slice
python -m pip install -r requirements-dev.txt
PYTHONPATH=. pytest --cov=app --cov-fail-under=85
```

## Resetar dados

```bash
docker compose --profile runtime down -v
```

## Falha do OPA

A aplicação retorna `503` e não executa a ação protegida. Verifique o container `opa`, a policy montada e o endpoint de decisão.

## Resultado ambíguo

O caso muda para `RECONCILIATION_REQUIRED`. Não repita a execução com uma nova chave sem antes reconciliar o resultado.
