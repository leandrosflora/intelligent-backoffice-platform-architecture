import json

from conftest import headers


def create_case(client, external="ops-case"):
    response = client.post(
        "/v1/cases",
        json={"external_id": external, "dispute_type": "CARD_PURCHASE", "amount_cents": 1000},
        headers=headers("case-manager"),
    )
    assert response.status_code == 200
    return response.json()


def test_timer_schedule_and_operational_read(client):
    case = create_case(client)
    response = client.post(
        f"/v1/operations/cases/{case['case_id']}/timers",
        json={"timer_type": "CASE_EXPIRY", "delay_seconds": 60, "payload": {"reason": "test"}},
        headers=headers("case-manager"),
    )
    assert response.status_code == 200, response.text
    listed = client.get(
        "/v1/operations/timers",
        headers=headers("platform-operator", subject="operator-1"),
    )
    assert listed.status_code == 200
    assert listed.json()[0]["timer_type"] == "CASE_EXPIRY"
    denied = client.get("/v1/operations/outbox", headers=headers("case-reader"))
    assert denied.status_code == 403


def test_controlled_replay_requires_operator_and_audits(client):
    case = create_case(client, "replay-case")
    envelope = {
        "eventId": "event-original",
        "eventType": "backoffice.timer.fired.v1",
        "eventVersion": 1,
        "occurredAt": "2026-01-01T00:00:00Z",
        "tenantId": "tenant-a",
        "caseId": case["case_id"],
        "correlationId": "corr-1",
        "producer": "workflow-worker",
        "dataClassification": "INTERNAL",
        "replayCount": 0,
        "payload": {"timerType": "NOOP"},
    }
    store = client.app.state.store
    with store.connection() as conn:
        dead_id = conn.execute(
            "INSERT INTO dead_letters(source,source_topic,event_id,tenant_id,aggregate_id,event_type,envelope_json,error,attempts) "
            "VALUES('consumer','backoffice.events.v1',?,?,?,?,?,?,3)",
            ("event-original", "tenant-a", case["case_id"], envelope["eventType"], json.dumps(envelope), "synthetic"),
        ).lastrowid
    denied = client.post(
        f"/v1/operations/dead-letters/{dead_id}/replay",
        json={"reason": "validated replay after investigation"},
        headers=headers("auditor", subject="auditor-1"),
    )
    assert denied.status_code == 403
    allowed = client.post(
        f"/v1/operations/dead-letters/{dead_id}/replay",
        json={"reason": "validated replay after investigation"},
        headers=headers("platform-operator", subject="operator-1"),
    )
    assert allowed.status_code == 200, allowed.text
    with store.connection() as conn:
        assert conn.execute("SELECT COUNT(*) count FROM replay_audit").fetchone()["count"] == 1
