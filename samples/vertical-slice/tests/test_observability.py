from conftest import headers


def test_metrics_endpoint_exposes_platform_metrics(client):
    client.get("/health")
    client.post(
        "/v1/cases",
        json={"external_id": "metrics-case", "dispute_type": "CARD_PURCHASE", "amount_cents": 1000},
        headers=headers("case-manager"),
    )
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "backoffice_http_requests_total" in text
    assert "backoffice_cases_created_total" in text
    assert "backoffice_policy_decisions_total" in text


def test_health_discloses_observability_mode(client):
    response = client.get("/health")
    assert response.json()["metricsEnabled"] is True
    assert response.json()["tracingEnabled"] is False
