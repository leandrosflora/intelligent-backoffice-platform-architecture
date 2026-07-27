from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    slo_path = ROOT / "observability" / "slos.yaml"
    alerts_path = ROOT / "observability" / "prometheus" / "alerts.yml"
    prometheus_path = ROOT / "observability" / "prometheus" / "prometheus.yml"
    collector_path = ROOT / "observability" / "otel" / "collector-config.yaml"
    dashboard_path = ROOT / "observability" / "grafana" / "dashboards" / "backoffice-overview.json"
    dataset_path = ROOT / "evals" / "datasets" / "intelligence-v1.jsonl"
    thresholds_path = ROOT / "evals" / "thresholds.yaml"

    for path in (slo_path, alerts_path, prometheus_path, collector_path, dashboard_path, dataset_path, thresholds_path):
        if not path.exists():
            fail(errors, f"missing required observability artifact: {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    slos = load_yaml(slo_path).get("slos", [])
    slo_ids = [item.get("id") for item in slos]
    if len(slo_ids) != len(set(slo_ids)):
        fail(errors, "SLO IDs must be unique")
    for item in slos:
        runbook = item.get("runbook")
        if not runbook or not (ROOT / runbook).exists():
            fail(errors, f"SLO {item.get('id')} references a missing runbook: {runbook}")
        if not item.get("owner"):
            fail(errors, f"SLO {item.get('id')} must declare an owner")

    alert_groups = load_yaml(alerts_path).get("groups", [])
    alerts = [rule for group in alert_groups for rule in group.get("rules", []) if "alert" in rule]
    alert_names = [item["alert"] for item in alerts]
    if len(alert_names) != len(set(alert_names)):
        fail(errors, "Alert names must be unique")
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        if labels.get("slo") not in slo_ids:
            fail(errors, f"alert {alert['alert']} references unknown SLO {labels.get('slo')}")
        runbook = annotations.get("runbook")
        if not runbook or not (ROOT / runbook).exists():
            fail(errors, f"alert {alert['alert']} references missing runbook {runbook}")

    prometheus = load_yaml(prometheus_path)
    required_rules = {"/etc/prometheus/recording-rules.yml", "/etc/prometheus/alerts.yml"}
    if not required_rules.issubset(set(prometheus.get("rule_files", []))):
        fail(errors, "Prometheus config must load recording and alert rules")
    jobs = {item.get("job_name") for item in prometheus.get("scrape_configs", [])}
    if "vertical-slice" not in jobs:
        fail(errors, "Prometheus must scrape the vertical-slice job")

    collector = load_yaml(collector_path)
    pipelines = collector.get("service", {}).get("pipelines", {})
    if "traces" not in pipelines:
        fail(errors, "OpenTelemetry Collector must define a traces pipeline")
    exporters = collector.get("exporters", {})
    if "otlp/jaeger" not in exporters:
        fail(errors, "OpenTelemetry Collector must export traces to Jaeger")

    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    if dashboard.get("uid") != "intelligent-backoffice-overview":
        fail(errors, "Grafana dashboard UID is not stable")
    if len(dashboard.get("panels", [])) < 5:
        fail(errors, "Grafana dashboard must contain the minimum operational panels")

    ids: list[str] = []
    for line_number, line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(errors, f"invalid eval JSONL at line {line_number}: {exc}")
            continue
        ids.append(case.get("id"))
        if not {"id", "task", "input", "expected"}.issubset(case):
            fail(errors, f"eval case at line {line_number} is incomplete")
    if len(ids) != len(set(ids)):
        fail(errors, "eval case IDs must be unique")

    thresholds = load_yaml(thresholds_path)
    if float(thresholds.get("overall_min_score", 0)) <= 0:
        fail(errors, "overall eval threshold must be positive")

    source = (ROOT / "samples" / "vertical-slice" / "app" / "observability.py").read_text(encoding="utf-8")
    required_metrics = {
        "backoffice_http_requests_total",
        "backoffice_policy_decisions_total",
        "backoffice_workflow_transitions_total",
        "backoffice_executions_total",
        "backoffice_reconciliations_total",
    }
    for metric in required_metrics:
        if metric not in source:
            fail(errors, f"runtime does not declare required metric {metric}")

    if errors:
        print("Observability validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Observability artifacts are valid: {len(slos)} SLOs, {len(alerts)} alerts, {len(ids)} eval cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
