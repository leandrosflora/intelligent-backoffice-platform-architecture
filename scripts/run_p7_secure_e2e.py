from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import jwt

BASE = "http://localhost:8082"
PRIVATE_KEY = Path(".local/security/identity-private.pem")
OUTPUT = Path("artifacts/p7-secure-e2e.jsonl")
ISSUER = "https://identity.local"
AUDIENCE = "intelligent-backoffice-api"
TENANT = "tenant-secure"


def mint(*, subject: str, roles: list[str], subject_type="HUMAN", purpose="CASE_MANAGEMENT", ttl=120, audience=AUDIENCE):
    now = datetime.now(timezone.utc)
    claims = {
        "iss": ISSUER,
        "sub": subject,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl)).timestamp()),
        "jti": str(uuid4()),
        "tenant_id": TENANT,
        "roles": roles,
        "subject_type": subject_type,
        "purpose": purpose,
    }
    return jwt.encode(claims, PRIVATE_KEY.read_text(), algorithm="EdDSA")


def request(method: str, path: str, body=None, token=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Correlation-Id", str(uuid4()))
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        return exc.code, json.loads(raw) if raw else None


def record(step, status, payload):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    entry = {"step": step, "status": status, "payload": payload}
    print(json.dumps(entry, ensure_ascii=False))
    with OUTPUT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def wait_ready():
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        status, _ = request("GET", "/health/ready")
        if status == 200:
            return
        time.sleep(1)
    raise AssertionError("secure API did not become ready")


OUTPUT.unlink(missing_ok=True)
wait_ready()
status, health = request("GET", "/health")
record("health", status, health)
assert status == 200 and health["identityMode"] == "jwt"

payload = {"external_id": "p7-secure-case", "dispute_type": "CARD_PURCHASE", "amount_cents": 15000}
status, response = request("POST", "/v1/cases", payload)
record("missing-token", status, response)
assert status == 401

status, response = request("POST", "/v1/cases", payload, mint(subject="manager", roles=["case-manager"], audience="wrong"))
record("wrong-audience", status, response)
assert status == 401

manager = mint(subject="manager", roles=["case-manager"])
status, created = request("POST", "/v1/cases", payload, manager)
record("signed-create", status, created)
assert status == 200
case_id = created["case_id"]

reader = mint(subject="reader-workload", roles=["case-reader"], subject_type="WORKLOAD")
status, loaded = request("GET", f"/v1/cases/{case_id}", token=reader)
record("signed-workload-read", status, loaded)
assert status == 200 and loaded["case_id"] == case_id

status, response = request(
    "POST",
    "/v1/cases",
    {"external_id": "spoof-attempt", "dispute_type": "CARD_PURCHASE", "amount_cents": 100},
    reader,
    {
        "X-Roles": "case-manager",
        "X-Subject-Id": "spoofed",
        "X-Subject-Type": "HUMAN",
        "X-Tenant-Id": TENANT,
    },
)
record("header-spoof-denied", status, response)
assert status == 403

tampered = reader[:-2] + ("aa" if reader[-2:] != "aa" else "bb")
status, response = request("GET", f"/v1/cases/{case_id}", token=tampered)
record("tampered-token", status, response)
assert status == 401

print("P7 secure identity E2E passed.")
