from __future__ import annotations

import argparse
import json
import math
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import jwt
import yaml


def mint(private_key: Path, subject: str, roles: list[str], tenant: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "iss": "https://identity.local",
            "sub": subject,
            "aud": "intelligent-backoffice-api",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=300)).timestamp()),
            "jti": str(uuid4()),
            "tenant_id": tenant,
            "roles": roles,
            "subject_type": "WORKLOAD",
            "purpose": "CASE_MANAGEMENT",
        },
        private_key.read_text(encoding="utf-8"),
        algorithm="EdDSA",
    )


def http(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Correlation-Id", str(uuid4()))
    if body is not None:
        req.add_header("Content-Type", "application/json")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            response.read()
            return response.status, time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        exc.read()
        return exc.code, time.perf_counter() - started


def percentile(values, q):
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(q * len(ordered)) - 1))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="capacity/profile.yaml")
    parser.add_argument("--private-key", default=".local/security/identity-private.pem")
    parser.add_argument("--output", default="artifacts/capacity-report.json")
    args = parser.parse_args()
    profile = yaml.safe_load(Path(args.profile).read_text(encoding="utf-8"))
    base = profile["baseUrl"]
    tenant = profile["tenant"]
    private = Path(args.private_key)

    manager = mint(private, "capacity-manager", ["case-manager"], tenant)
    status, _ = http(
        "POST",
        f"{base}/v1/cases",
        manager,
        {"external_id": f"capacity-{uuid4()}", "dispute_type": "CARD_PURCHASE", "amount_cents": 100},
    )
    if status != 200:
        raise SystemExit(f"could not seed capacity case: HTTP {status}")

    # Discover the case using a second idempotent create with a stable external id.
    stable_external = f"capacity-stable-{uuid4()}"
    body = {"external_id": stable_external, "dispute_type": "CARD_PURCHASE", "amount_cents": 100}
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{base}/v1/cases", data=data, method="POST")
    req.add_header("Authorization", f"Bearer {manager}")
    req.add_header("X-Correlation-Id", str(uuid4()))
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=5) as response:
        case_id = json.loads(response.read().decode())["case_id"]

    reader = mint(private, "capacity-reader", ["case-reader"], tenant)
    requests = int(profile["requests"])
    concurrency = int(profile["concurrency"])
    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(http, "GET", f"{base}/v1/cases/{case_id}", reader) for _ in range(requests)]
        for future in as_completed(futures):
            results.append(future.result())

    latencies = [duration for _, duration in results]
    errors = sum(1 for status, _ in results if status >= 400)
    report = {
        "status": "PASSED",
        "requests": requests,
        "concurrency": concurrency,
        "errors": errors,
        "errorRatio": errors / requests,
        "p50Seconds": statistics.median(latencies),
        "p95Seconds": percentile(latencies, 0.95),
        "p99Seconds": percentile(latencies, 0.99),
        "thresholds": profile["thresholds"],
    }
    if report["errorRatio"] > float(profile["thresholds"]["maxErrorRatio"]):
        report["status"] = "FAILED"
    if report["p95Seconds"] > float(profile["thresholds"]["p95Seconds"]):
        report["status"] = "FAILED"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
