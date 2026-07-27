from conftest import headers

def create(client, external="ext-1"):
    response = client.post(
        "/v1/cases",
        json={"external_id": external, "dispute_type": "CARD_PURCHASE", "amount_cents": 12000},
        headers=headers("case-manager"),
    )
    assert response.status_code == 200, response.text
    return response.json()

def advance_to_approval(client):
    case = create(client)
    case_id = case["case_id"]
    response = client.post(
        f"/v1/cases/{case_id}/documents",
        json={"document_id": "doc-1", "filename": "proof.pdf"},
        headers=headers("document-processor") | {"If-Match": str(case["version"])},
    )
    assert response.status_code == 200, response.text
    case = response.json()
    response = client.post(
        f"/v1/cases/{case_id}/investigations",
        headers=headers("operations-analyst") | {"If-Match": str(case["version"])},
    )
    assert response.status_code == 200, response.text
    case = response.json()
    response = client.post(
        f"/v1/cases/{case_id}/recommendations",
        json={
            "outcome": "APPROVE",
            "rationale": "evidence confirms dispute",
            "evidence_references": case["evidence_references"],
        },
        headers=headers("decision-agent", subject="agent-1", subject_type="WORKLOAD") | {"If-Match": str(case["version"])},
    )
    assert response.status_code == 200, response.text
    return response.json()

def test_happy_path_and_idempotency(client):
    case = advance_to_approval(client)
    case_id = case["case_id"]
    response = client.post(
        f"/v1/cases/{case_id}/approvals",
        json={"decision": "APPROVED", "authority_limit_cents": 50000, "reason": "within authority"},
        headers=headers("approver", subject="approver-1") | {"If-Match": str(case["version"])},
    )
    assert response.status_code == 200, response.text
    execution_headers = headers("execution-service", subject="execution-service", subject_type="WORKLOAD") | {"Idempotency-Key": "exec-1"}
    first = client.post(f"/v1/cases/{case_id}/executions", json={"result_mode": "SUCCESS"}, headers=execution_headers)
    second = client.post(f"/v1/cases/{case_id}/executions", json={"result_mode": "SUCCESS"}, headers=execution_headers)
    assert first.status_code == 200 and second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["state"] == "EXECUTED"
    timeline = client.get(f"/v1/cases/{case_id}/timeline", headers=headers("auditor")).json()
    assert len(timeline) == 6

def test_cross_tenant_is_hidden(client):
    case = create(client)
    response = client.get(f"/v1/cases/{case['case_id']}", headers=headers("case-reader", tenant="tenant-b"))
    assert response.status_code == 404

def test_self_approval_is_denied(client):
    case = advance_to_approval(client)
    response = client.post(
        f"/v1/cases/{case['case_id']}/approvals",
        json={"decision": "APPROVED", "authority_limit_cents": 50000, "reason": "invalid self approval"},
        headers=headers("approver", subject="agent-1") | {"If-Match": str(case["version"])},
    )
    assert response.status_code == 403

def test_version_conflict(client):
    case = create(client)
    response = client.post(
        f"/v1/cases/{case['case_id']}/documents",
        json={"document_id": "doc-1", "filename": "proof.pdf"},
        headers=headers("document-processor") | {"If-Match": "99"},
    )
    assert response.status_code == 409

def test_ambiguous_execution_enters_reconciliation(client):
    case = advance_to_approval(client)
    case_id = case["case_id"]
    case = client.post(
        f"/v1/cases/{case_id}/approvals",
        json={"decision": "APPROVED", "authority_limit_cents": 50000, "reason": "approved"},
        headers=headers("approver", subject="approver-1") | {"If-Match": str(case["version"])},
    ).json()
    response = client.post(
        f"/v1/cases/{case_id}/executions",
        json={"result_mode": "AMBIGUOUS"},
        headers=headers("execution-service", subject="execution-service", subject_type="WORKLOAD") | {"Idempotency-Key": "amb-1"},
    )
    assert response.status_code == 200
    assert response.json()["state"] == "RECONCILIATION_REQUIRED"

def test_idempotency_conflict(client):
    case = advance_to_approval(client)
    case_id = case["case_id"]
    client.post(
        f"/v1/cases/{case_id}/approvals",
        json={"decision": "APPROVED", "authority_limit_cents": 50000, "reason": "approved"},
        headers=headers("approver", subject="approver-1") | {"If-Match": str(case["version"])},
    )
    execution_headers = headers("execution-service", subject="execution-service", subject_type="WORKLOAD") | {"Idempotency-Key": "same-key"}
    assert client.post(f"/v1/cases/{case_id}/executions", json={"result_mode": "SUCCESS"}, headers=execution_headers).status_code == 200
    assert client.post(f"/v1/cases/{case_id}/executions", json={"result_mode": "AMBIGUOUS"}, headers=execution_headers).status_code == 409
