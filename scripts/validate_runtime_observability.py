from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


def get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def wait_for(url: str, predicate, attempts: int = 40, interval: float = 2.0) -> str:
    last = ""
    for _ in range(attempts):
        try:
            status, body = get(url)
            last = f"status={status} body={body[:500]}"
            if predicate(status, body):
                return body
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
        time.sleep(interval)
    raise RuntimeError(f"Timed out waiting for {url}: {last}")


def main() -> int:
    metrics = wait_for(
        "http://localhost:8080/metrics",
        lambda status, body: status == 200 and "backoffice_workflow_transitions_total" in body,
    )
    required_metrics = (
        "backoffice_http_requests_total",
        "backoffice_policy_decisions_total",
        "backoffice_workflow_transitions_total",
        "backoffice_executions_total",
        "backoffice_cases_created_total",
    )
    missing = [metric for metric in required_metrics if metric not in metrics]
    if missing:
        raise RuntimeError(f"Missing runtime metrics: {missing}")

    wait_for("http://localhost:9090/-/ready", lambda status, body: status == 200)
    wait_for("http://localhost:3000/api/health", lambda status, body: status == 200 and json.loads(body).get("database") == "ok")

    services_body = wait_for(
        "http://localhost:16686/api/services",
        lambda status, body: status == 200 and "intelligent-backoffice-vertical-slice" in body,
        attempts=50,
    )
    services = json.loads(services_body).get("data", [])
    if "intelligent-backoffice-vertical-slice" not in services:
        raise RuntimeError(f"Expected traced service was not registered in Jaeger: {services}")

    print(json.dumps({"metrics": list(required_metrics), "jaegerServices": services}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
