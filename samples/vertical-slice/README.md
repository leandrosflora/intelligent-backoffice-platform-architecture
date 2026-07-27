# Vertical slice executável

Implementação modular do primeiro fluxo de contestação. Case API, workflow, document intelligence mock, aprovação humana e execução governada permanecem separados por responsabilidade no código, mas são empacotados em um único serviço.

## Runtime mínimo

Na raiz do repositório:

```bash
docker compose --profile runtime up --build
```

- API: `http://localhost:8080`
- OpenAPI interativo: `http://localhost:8080/docs`
- métricas: `http://localhost:8080/metrics`
- OPA: `http://localhost:8181`

## Runtime observado

```bash
OTEL_TRACING_ENABLED=true docker compose --profile observability up --build
```

O profile observado adiciona Prometheus, Grafana, OpenTelemetry Collector e Jaeger.

## Fluxo demonstrado

1. criar caso;
2. registrar e classificar documento sintético;
3. validar evidência;
4. executar investigação mock;
5. produzir recomendação grounded;
6. aprovar com ator diferente do recomendador;
7. executar operação mock com idempotência;
8. consultar timeline, métricas e traces.

## Evals

```bash
cd ../..
PYTHONPATH=samples/vertical-slice python scripts/run_evals.py
```

Os testes rápidos utilizam banco temporário e policy embedded equivalente ao subconjunto exercitado. O runtime Docker consulta o OPA real via HTTP.

## Limites

- sem LLM ou OCR real;
- sem sistema bancário real;
- sem dados reais;
- sem mensageria;
- sem identidade criptográfica;
- sem retenção corporativa de telemetria;
- não é produção.
