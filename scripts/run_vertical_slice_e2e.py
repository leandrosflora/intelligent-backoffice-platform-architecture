from __future__ import annotations
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://localhost:8080"
OUTPUT = Path("e2e-output.jsonl")


def record(step: str, status: int, payload) -> None:
    entry = {"step": step, "status": status, "payload": payload}
    print(json.dumps(entry, ensure_ascii=False))
    with OUTPUT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def request(method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def headers(role, subject="case-manager-1", subject_type="HUMAN"):
    return {
        "X-Subject-Id": subject,
        "X-Subject-Type": subject_type,
        "X-Roles": role,
        "X-Tenant-Id": "tenant-demo",
        "X-Correlation-Id": "ci-e2e",
    }


OUTPUT.unlink(missing_ok=True)
for _ in range(30):
    try:
        status, payload = request("GET", "/health")
        if status == 200:
            record("health", status, payload)
            break
    except Exception:
        pass
    time.sleep(2)
else:
    raise SystemExit("vertical slice did not become healthy")

status, case = request("POST", "/v1/cases", {"external_id": "ci-case-1", "dispute_type": "CARD_PURCHASE", "amount_cents": 12000}, headers("case-manager"))
record("create-case", status, case)
assert status == 200, (status, case)
case_id = case["case_id"]

h = headers("document-processor")
h["If-Match"] = str(case["version"])
status, case = request("POST", f"/v1/cases/{case_id}/documents", {"document_id": "doc-ci", "filename": "proof.pdf"}, h)
record("register-document", status, case)
assert status == 200, (status, case)

h = headers("operations-analyst")
h["If-Match"] = str(case["version"])
status, case = request("POST", f"/v1/cases/{case_id}/investigations", {}, h)
record("investigate", status, case)
assert status == 200, (status, case)

h = headers("decision-agent", "decision-agent-1", "WORKLOAD")
h["If-Match"] = str(case["version"])
status, case = request("POST", f"/v1/cases/{case_id}/recommendations", {"outcome": "APPROVE", "rationale": "synthetic evidence supports approval", "evidence_references": case["evidence_references"]}, h)
record("recommend", status, case)
assert status == 200, (status, case)

h = headers("approver", "approver-1")
h["If-Match"] = str(case["version"])
status, case = request("POST", f"/v1/cases/{case_id}/approvals", {"decision": "APPROVED", "authority_limit_cents": 50000, "reason": "within authority"}, h)
record("approve", status, case)
assert status == 200, (status, case)

h = headers("execution-service", "execution-service", "WORKLOAD")
h["Idempotency-Key"] = "ci-execution-1"
status, case = request("POST", f"/v1/cases/{case_id}/executions", {"result_mode": "SUCCESS"}, h)
record("execute", status, case)
assert status == 200 and case["state"] == "EXECUTED", (status, case)

status, timeline = request("GET", f"/v1/cases/{case_id}/timeline", headers=headers("auditor", "auditor-1"))
record("timeline", status, timeline)
assert status == 200 and len(timeline) == 6, (status, timeline)
print(f"Vertical slice E2E passed for case {case_id} with {len(timeline)} events.")
