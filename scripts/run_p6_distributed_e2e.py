from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://localhost:8081"
OUTPUT = Path("p6-e2e-output.jsonl")


def record(step: str, status: int, payload) -> None:
    entry = {"step": step, "status": status, "payload": payload}
    print(json.dumps(entry, ensure_ascii=False))
    with OUTPUT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def request(method: str, path: str, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
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


def headers(role: str, subject="case-manager-1", subject_type="HUMAN", correlation="p6-e2e"):
    return {
        "X-Subject-Id": subject,
        "X-Subject-Type": subject_type,
        "X-Roles": role,
        "X-Tenant-Id": "tenant-demo",
        "X-Correlation-Id": correlation,
    }


def wait_for(name: str, fn, timeout=60):
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


OUTPUT.unlink(missing_ok=True)
wait_for("distributed API health", lambda: request("GET", "/health")[0] == 200)
status, health = request("GET", "/health")
record("health", status, health)
assert health["eventingEnabled"] is True

status, expiring_case = request(
    "POST",
    "/v1/cases",
    {"external_id": "p6-expiring-case", "dispute_type": "CARD_PURCHASE", "amount_cents": 12000},
    headers("case-manager"),
)
record("create-expiring-case", status, expiring_case)
assert status == 200
expiring_id = expiring_case["case_id"]

status, timer = request(
    "POST",
    f"/v1/operations/cases/{expiring_id}/timers",
    {"timer_type": "CASE_EXPIRY", "delay_seconds": 1, "payload": {"reason": "synthetic-timeout"}},
    headers("case-manager"),
)
record("schedule-expiry", status, timer)
assert status == 200


def expired_case():
    status, payload = request("GET", f"/v1/cases/{expiring_id}", headers=headers("case-manager"))
    return payload if status == 200 and payload.get("state") == "EXPIRED" else None


expired = wait_for("case expiration through timer event", expired_case)
record("case-expired", 200, expired)

status, poison_case = request(
    "POST",
    "/v1/cases",
    {"external_id": "p6-poison-case", "dispute_type": "CARD_PURCHASE", "amount_cents": 5000},
    headers("case-manager", correlation="p6-poison"),
)
record("create-poison-case", status, poison_case)
assert status == 200
poison_id = poison_case["case_id"]

status, poison_timer = request(
    "POST",
    f"/v1/operations/cases/{poison_id}/timers",
    {"timer_type": "NOOP", "delay_seconds": 0, "payload": {"simulateFailureOnce": True}},
    headers("case-manager", correlation="p6-poison"),
)
record("schedule-poison-timer", status, poison_timer)
assert status == 200
operator_headers = headers("platform-operator", subject="operator-1", correlation="p6-operator")


def open_dead_letter():
    status, rows = request("GET", "/v1/operations/dead-letters", headers=operator_headers)
    if status != 200:
        return None
    return next((row for row in rows if row["aggregate_id"] == poison_id and row["status"] == "OPEN"), None)


letter = wait_for("consumer dead letter", open_dead_letter, timeout=90)
record("dead-letter-open", 200, letter)

status, replay = request(
    "POST",
    f"/v1/operations/dead-letters/{letter['id']}/replay",
    {"reason": "investigated synthetic one-time consumer failure"},
    operator_headers,
)
record("dead-letter-replay", status, replay)
assert status == 200
replay_event_id = replay["replayEventId"]


def replay_projection():
    status, rows = request("GET", "/v1/operations/event-projections", headers=operator_headers)
    if status != 200:
        return None
    return next((row for row in rows if row["event_id"] == replay_event_id and row["replay_count"] == 1), None)


projection = wait_for("replayed event projection", replay_projection, timeout=90)
record("replay-processed", 200, projection)

status, dead_letters = request("GET", "/v1/operations/dead-letters", headers=operator_headers)
record("dead-letters", status, dead_letters)
assert next(row for row in dead_letters if row["id"] == letter["id"])["status"] == "REPLAYED"


def outbox_drained():
    status, rows = request("GET", "/v1/operations/outbox", headers=operator_headers)
    if status != 200:
        return None
    active = [row for row in rows if row["status"] in {"PENDING", "IN_FLIGHT", "RETRY"}]
    return rows if not active and rows else None


outbox = wait_for("outbox drain", outbox_drained, timeout=90)
record("outbox-drained", 200, {"messages": len(outbox), "statuses": sorted({row['status'] for row in outbox})})

status, metrics = request("GET", "/metrics")
record("metrics", status, {"available": status == 200, "eventingMetrics": "backoffice_outbox_messages" in metrics})
assert status == 200 and "backoffice_outbox_messages" in metrics
print("P6 distributed E2E passed: outbox, Kafka, inbox, timer, retry, DLQ and controlled replay.")
