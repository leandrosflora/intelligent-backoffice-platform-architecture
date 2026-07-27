from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

BASE = os.getenv("WALKTHROUGH_BASE_URL", "http://localhost:8081").rstrip("/")
OUTPUT_DIR = Path(os.getenv("WALKTHROUGH_OUTPUT_DIR", "artifacts/walkthrough"))
OUTPUT = OUTPUT_DIR / "dispute-walkthrough.jsonl"
SUMMARY = OUTPUT_DIR / "dispute-walkthrough-summary.json"


def record(scenario: str, step: str, status: int, payload) -> None:
    entry = {"scenario": scenario, "step": step, "status": status, "payload": payload}
    print(json.dumps(entry, ensure_ascii=False))
    with OUTPUT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def request(method: str, path: str, body=None, headers=None, timeout=10):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode()
            try:
                payload = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                payload = raw
            return response.status, payload
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            payload = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        return exc.code, payload


def headers(role: str, subject: str, subject_type="HUMAN", correlation="walkthrough"):
    return {
        "X-Subject-Id": subject,
        "X-Subject-Type": subject_type,
        "X-Roles": role,
        "X-Tenant-Id": "tenant-demo",
        "X-Correlation-Id": correlation,
    }


def require(status: int, expected: int, payload, step: str) -> None:
    if status != expected:
        raise AssertionError(f"{step}: expected HTTP {expected}, received {status}: {payload}")


def wait_for(name: str, fn, timeout=90):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = fn()
            last = value
            if value:
                return value
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
        time.sleep(1)
    raise AssertionError(f"timeout waiting for {name}; last={last}")


def progress_to_approved(scenario: str, suffix: str):
    correlation = f"walkthrough-{scenario}-{suffix}"
    status, case = request(
        "POST",
        "/v1/cases",
        {"external_id": f"walkthrough-{scenario}-{suffix}", "dispute_type": "CARD_PURCHASE", "amount_cents": 12000},
        headers("case-manager", "case-manager-1", correlation=correlation),
    )
    record(scenario, "create-case", status, case)
    require(status, 200, case, "create-case")
    case_id = case["case_id"]

    document_headers = headers("document-processor", "document-processor-1", correlation=correlation)
    document_headers["If-Match"] = str(case["version"])
    status, case = request(
        "POST",
        f"/v1/cases/{case_id}/documents",
        {"document_id": f"doc-{suffix}", "filename": "proof.pdf", "content_type": "application/pdf"},
        document_headers,
    )
    record(scenario, "register-document", status, case)
    require(status, 200, case, "register-document")

    investigation_headers = headers("operations-analyst", "analyst-1", correlation=correlation)
    investigation_headers["If-Match"] = str(case["version"])
    status, case = request("POST", f"/v1/cases/{case_id}/investigations", {}, investigation_headers)
    record(scenario, "investigate", status, case)
    require(status, 200, case, "investigate")

    recommendation_headers = headers("decision-agent", "decision-agent-1", "WORKLOAD", correlation)
    recommendation_headers["If-Match"] = str(case["version"])
    status, case = request(
        "POST",
        f"/v1/cases/{case_id}/recommendations",
        {
            "outcome": "APPROVE",
            "rationale": "synthetic evidence supports approval",
            "evidence_references": case["evidence_references"],
        },
        recommendation_headers,
    )
    record(scenario, "recommend", status, case)
    require(status, 200, case, "recommend")

    approval_headers = headers("approver", "approver-1", correlation=correlation)
    approval_headers["If-Match"] = str(case["version"])
    status, case = request(
        "POST",
        f"/v1/cases/{case_id}/approvals",
        {"decision": "APPROVED", "authority_limit_cents": 50000, "reason": "within delegated authority"},
        approval_headers,
    )
    record(scenario, "approve", status, case)
    require(status, 200, case, "approve")
    if case["state"] != "APPROVED":
        raise AssertionError(f"approve: unexpected state {case['state']}")
    return case, correlation


def run_happy_path(suffix: str):
    scenario = "happy-path"
    case, correlation = progress_to_approved(scenario, suffix)
    case_id = case["case_id"]
    execution_headers = headers("execution-service", "execution-service", "WORKLOAD", correlation)
    execution_headers["Idempotency-Key"] = f"walkthrough-exec-{suffix}"
    status, executed = request("POST", f"/v1/cases/{case_id}/executions", {"result_mode": "SUCCESS"}, execution_headers)
    record(scenario, "execute", status, executed)
    require(status, 200, executed, "execute")
    if executed["state"] != "EXECUTED" or executed["execution_status"] != "SUCCEEDED":
        raise AssertionError(f"execute: unexpected result {executed}")

    status, replay = request("POST", f"/v1/cases/{case_id}/executions", {"result_mode": "SUCCESS"}, execution_headers)
    record(scenario, "execute-idempotent-replay", status, replay)
    require(status, 200, replay, "execute-idempotent-replay")
    if replay != executed:
        raise AssertionError("execution replay returned a different response")

    status, execution = request(
        "GET",
        f"/v1/cases/{case_id}/executions/{executed['execution_id']}",
        headers("case-manager", "case-manager-1", correlation=correlation),
    )
    record(scenario, "read-execution", status, execution)
    require(status, 200, execution, "read-execution")

    status, timeline = request(
        "GET",
        f"/v1/cases/{case_id}/timeline",
        headers("auditor", "auditor-1", correlation=correlation),
    )
    record(scenario, "timeline", status, timeline)
    require(status, 200, timeline, "timeline")
    if len(timeline) != 6:
        raise AssertionError(f"happy timeline: expected 6 events, received {len(timeline)}")
    return {"case_id": case_id, "execution_id": executed["execution_id"], "state": executed["state"], "events": len(timeline)}


def run_ambiguous_reconciliation(suffix: str):
    scenario = "ambiguous-reconciliation"
    case, correlation = progress_to_approved(scenario, suffix)
    case_id = case["case_id"]
    execution_headers = headers("execution-service", "execution-service", "WORKLOAD", correlation)
    execution_headers["Idempotency-Key"] = f"walkthrough-ambiguous-{suffix}"
    status, ambiguous = request("POST", f"/v1/cases/{case_id}/executions", {"result_mode": "AMBIGUOUS"}, execution_headers)
    record(scenario, "execute-ambiguous", status, ambiguous)
    require(status, 200, ambiguous, "execute-ambiguous")
    if ambiguous["state"] != "RECONCILIATION_REQUIRED":
        raise AssertionError(f"ambiguous execution did not enter reconciliation: {ambiguous}")

    execution_id = ambiguous["execution_id"]
    status, execution = request(
        "GET",
        f"/v1/cases/{case_id}/executions/{execution_id}",
        headers("reconciler", "reconciler-1", correlation=correlation),
    )
    record(scenario, "read-ambiguous-execution", status, execution)
    require(status, 200, execution, "read-ambiguous-execution")

    reconciliation_headers = headers("reconciler", "reconciler-1", correlation=correlation)
    reconciliation_headers["If-Match"] = str(ambiguous["version"])
    reconciliation_headers["Idempotency-Key"] = f"walkthrough-reconcile-{suffix}"
    reconciliation_payload = {
        "case_version": ambiguous["version"],
        "resolution": "CONFIRMED_SUCCEEDED",
        "reason": "system of record confirms the synthetic refund completed successfully",
    }
    status, reconciled = request(
        "POST",
        f"/v1/cases/{case_id}/reconciliations/{execution_id}/resolve",
        reconciliation_payload,
        reconciliation_headers,
    )
    record(scenario, "resolve-reconciliation", status, reconciled)
    require(status, 200, reconciled, "resolve-reconciliation")
    if reconciled["state"] != "EXECUTED" or reconciled["execution_status"] != "RECONCILED":
        raise AssertionError(f"reconciliation did not close the ambiguity: {reconciled}")

    status, replay = request(
        "POST",
        f"/v1/cases/{case_id}/reconciliations/{execution_id}/resolve",
        reconciliation_payload,
        reconciliation_headers,
    )
    record(scenario, "reconciliation-idempotent-replay", status, replay)
    require(status, 200, replay, "reconciliation-idempotent-replay")
    if replay != reconciled:
        raise AssertionError("reconciliation replay returned a different response")

    status, execution = request(
        "GET",
        f"/v1/cases/{case_id}/executions/{execution_id}",
        headers("reconciler", "reconciler-1", correlation=correlation),
    )
    record(scenario, "read-reconciled-execution", status, execution)
    require(status, 200, execution, "read-reconciled-execution")
    if execution["status"] != "RECONCILED" or execution["resolution"] != "CONFIRMED_SUCCEEDED":
        raise AssertionError(f"unexpected execution reconciliation status: {execution}")

    status, timeline = request(
        "GET",
        f"/v1/cases/{case_id}/timeline",
        headers("auditor", "auditor-1", correlation=correlation),
    )
    record(scenario, "timeline", status, timeline)
    require(status, 200, timeline, "timeline")
    if len(timeline) != 7 or timeline[-1]["eventType"] != "backoffice.reconciliation.succeeded.v1":
        raise AssertionError(f"ambiguous timeline is incomplete: {timeline}")
    return {"case_id": case_id, "execution_id": execution_id, "state": reconciled["state"], "events": len(timeline)}


def collect_event_evidence(case_ids: set[str]):
    operator_headers = headers("platform-operator", "operator-1", correlation="walkthrough-event-evidence")

    def published_rows():
        status, rows = request("GET", "/v1/operations/outbox?limit=500", headers=operator_headers)
        if status != 200:
            return None
        selected = [row for row in rows if row["aggregate_id"] in case_ids]
        if selected and all(row["status"] == "PUBLISHED" for row in selected):
            return selected
        return None

    outbox = wait_for("walkthrough outbox publication", published_rows)
    record("event-evidence", "outbox-published", 200, {"messages": len(outbox), "statuses": sorted({row["status"] for row in outbox})})

    def projected_rows():
        status, rows = request("GET", "/v1/operations/event-projections?limit=500", headers=operator_headers)
        if status != 200:
            return None
        selected = [row for row in rows if row["aggregate_id"] in case_ids]
        return selected if len(selected) >= len(outbox) else None

    projections = wait_for("walkthrough event projections", projected_rows)
    record("event-evidence", "events-projected", 200, {"events": len(projections), "types": sorted({row["event_type"] for row in projections})})
    return {"outbox_messages": len(outbox), "projected_events": len(projections)}


def collect_metrics():
    status, metrics = request("GET", "/metrics")
    require(status, 200, metrics, "metrics")
    checks = {
        "http": "backoffice_http_requests" in metrics,
        "policy": "backoffice_policy_decisions" in metrics,
        "execution": "backoffice_executions" in metrics,
        "outbox": "backoffice_outbox_messages" in metrics,
    }
    record("observability", "metrics", status, checks)
    if not all(checks.values()):
        raise AssertionError(f"expected metrics are missing: {checks}")
    return checks


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.unlink(missing_ok=True)
    SUMMARY.unlink(missing_ok=True)

    wait_for("distributed API health", lambda: request("GET", "/health")[0] == 200)
    status, health = request("GET", "/health")
    record("platform", "health", status, health)
    require(status, 200, health, "health")
    if health.get("eventingEnabled") is not True:
        raise AssertionError("walkthrough requires the distributed profile with eventing enabled")

    suffix = uuid4().hex[:10]
    happy = run_happy_path(suffix)
    ambiguous = run_ambiguous_reconciliation(suffix)
    event_evidence = collect_event_evidence({happy["case_id"], ambiguous["case_id"]})
    metrics = collect_metrics()

    summary = {
        "status": "PASSED",
        "base_url": BASE,
        "happy_path": happy,
        "ambiguous_reconciliation": ambiguous,
        "event_evidence": event_evidence,
        "metrics": metrics,
        "limitations": [
            "synthetic data",
            "mock execution",
            "SQLite local persistence",
            "single-node Redpanda",
            "not production ready",
        ],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record("platform", "summary", 200, summary)
    print(f"Dispute walkthrough passed. Evidence: {OUTPUT} and {SUMMARY}")


if __name__ == "__main__":
    main()
