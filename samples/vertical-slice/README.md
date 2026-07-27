# Vertical slice executável

Implementação modular do primeiro fluxo de contestação. Case API, workflow, document intelligence mock, aprovação humana e execução governada permanecem separados por responsabilidade no código, mas são empacotados em um único serviço para o primeiro slice.

## Executar

Na raiz do repositório:

```bash
docker compose --profile runtime up --build
```

- API: `http://localhost:8080`
- OpenAPI interativo: `http://localhost:8080/docs`
- OPA: `http://localhost:8181`

## Fluxo demonstrado

1. criar caso;
2. registrar documento sintético;
3. validar documento por mock determinístico;
4. executar investigação mock;
5. produzir recomendação;
6. aprovar com ator diferente do recomendador;
7. executar operação mock com idempotência;
8. consultar timeline.

O runtime usa SQLite persistido em volume e consulta o OPA via HTTP. Os testes utilizam banco temporário e policy embedded equivalente ao subconjunto exercitado.

## Limites

- sem LLM ou OCR real;
- sem sistema bancário real;
- sem dados reais;
- sem mensageria;
- sem identidade criptográfica;
- não é produção.
