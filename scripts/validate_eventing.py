from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    topology_path = ROOT / "contracts/messaging/topology.yaml"
    topology = yaml.safe_load(topology_path.read_text(encoding="utf-8"))
    topics = {item["name"]: item for item in topology.get("topics", [])}
    require(topology.get("status") == "EXECUTABLE_BASELINE", "topology status must be EXECUTABLE_BASELINE", errors)
    require(topology.get("semantics", {}).get("delivery") == "at-least-once", "delivery must be at-least-once", errors)
    require(topology.get("semantics", {}).get("producerAtomicity") == "sqlite-transactional-outbox", "transactional outbox declaration missing", errors)
    require(topology.get("semantics", {}).get("consumerIdempotency") == "durable-inbox", "durable inbox declaration missing", errors)
    require({"backoffice.events.v1", "backoffice.dlq.v1"}.issubset(topics), "required topics missing", errors)
    require(topology["semantics"]["retry"]["maxAttempts"] >= 3, "retry attempts must be at least three", errors)
    replay = topology["components"]["controlledReplay"]
    require(replay.get("requiredRole") == "platform-operator", "controlled replay role missing", errors)
    require("reason" in " ".join(replay.get("auditFields", [])).lower(), "replay audit reason missing", errors)

    operational_api = yaml.safe_load((ROOT / "contracts/openapi/eventing-operations-api.yaml").read_text(encoding="utf-8"))
    require(operational_api.get("openapi") == "3.1.0", "eventing operations API must use OpenAPI 3.1.0", errors)
    paths = operational_api.get("paths", {})
    require(any("replay" in path for path in paths), "controlled replay endpoint missing", errors)
    require(any("timers" in path for path in paths), "timer endpoint missing", errors)

    store_source = (ROOT / "samples/vertical-slice/app/store.py").read_text(encoding="utf-8")
    for table in ("outbox", "inbox", "timers", "dead_letters", "replay_audit"):
        require(f"CREATE TABLE IF NOT EXISTS {table}" in store_source, f"durable table missing: {table}", errors)
    require("CREATE TRIGGER IF NOT EXISTS timeline_to_outbox" in store_source, "transactional outbox trigger missing", errors)

    worker_sources = {
        "outbox": ROOT / "samples/vertical-slice/app/outbox_worker.py",
        "workflow": ROOT / "samples/vertical-slice/app/workflow_worker.py",
        "timer": ROOT / "samples/vertical-slice/app/timer_worker.py",
    }
    for name, path in worker_sources.items():
        require(path.exists(), f"{name} worker missing", errors)

    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("redpanda:", "outbox-publisher:", "workflow-worker:", "timer-worker:", "distributed-api:"):
        require(service in compose, f"Compose service missing: {service}", errors)

    if errors:
        print("P6 eventing validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(json.dumps({"topics": len(topics), "workers": len(worker_sources), "status": "valid"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
