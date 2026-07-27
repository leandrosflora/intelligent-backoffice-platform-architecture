from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "samples" / "vertical-slice"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.intelligence import classify_document, investigate_case, propose_recommendation  # noqa: E402


def execute_case(case: dict[str, Any]) -> dict[str, Any]:
    task = case["task"]
    payload = case["input"]
    functions: dict[str, Callable[..., dict[str, Any]]] = {
        "document_classification": classify_document,
        "investigation": investigate_case,
        "recommendation": propose_recommendation,
    }
    if task not in functions:
        raise ValueError(f"Unsupported eval task: {task}")
    return functions[task](**payload)


def case_score(expected: dict[str, Any], actual: dict[str, Any]) -> float:
    if not expected:
        return 1.0
    matched = sum(1 for key, value in expected.items() if actual.get(key) == value)
    return matched / len(expected)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def percentage(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def evaluate(dataset: Path, thresholds_path: Path) -> dict[str, Any]:
    thresholds = yaml.safe_load(thresholds_path.read_text(encoding="utf-8"))
    rows = []
    by_task: dict[str, list[float]] = defaultdict(list)
    for case in load_jsonl(dataset):
        actual = execute_case(case)
        score = case_score(case["expected"], actual)
        by_task[case["task"]].append(score)
        rows.append({
            "id": case["id"],
            "task": case["task"],
            "score": score,
            "expected": case["expected"],
            "actual": actual,
            "passed": score == 1.0,
        })

    task_scores = {task: sum(scores) / len(scores) for task, scores in sorted(by_task.items())}
    overall = sum(row["score"] for row in rows) / len(rows)

    unknown_cases = [row for row in rows if row["task"] == "document_classification" and row["expected"].get("document_type") == "UNKNOWN"]
    ungrounded_recommendations = [row for row in rows if row["task"] == "recommendation" and row["expected"].get("grounded") is False]
    guardrails = {
        "unknown_document_abstention_rate": percentage(sum(row["actual"].get("abstained") is True for row in unknown_cases), len(unknown_cases)),
        "ungrounded_recommendation_abstention_rate": percentage(sum(row["actual"].get("abstained") is True for row in ungrounded_recommendations), len(ungrounded_recommendations)),
    }

    failures: list[str] = []
    if overall < float(thresholds["overall_min_score"]):
        failures.append(f"overall score {overall:.4f} below {thresholds['overall_min_score']}")
    for task, config in thresholds.get("tasks", {}).items():
        actual = task_scores.get(task, 0.0)
        if actual < float(config["min_score"]):
            failures.append(f"task {task} score {actual:.4f} below {config['min_score']}")
    for name, config in thresholds.get("guardrails", {}).items():
        actual = guardrails.get(name, 0.0)
        if actual < float(config["min"]):
            failures.append(f"guardrail {name} {actual:.4f} below {config['min']}")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(dataset.relative_to(ROOT)),
        "thresholds": str(thresholds_path.relative_to(ROOT)),
        "case_count": len(rows),
        "overall_score": overall,
        "task_scores": task_scores,
        "guardrails": guardrails,
        "passed": not failures,
        "failures": failures,
        "cases": rows,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Eval report",
        "",
        f"- Status: **{'PASS' if report['passed'] else 'FAIL'}**",
        f"- Dataset: `{report['dataset']}`",
        f"- Cases: {report['case_count']}",
        f"- Overall score: {report['overall_score']:.2%}",
        "",
        "## Scores por capacidade",
        "",
        "| Capacidade | Score |",
        "|---|---:|",
    ]
    lines.extend(f"| `{task}` | {score:.2%} |" for task, score in report["task_scores"].items())
    lines.extend(["", "## Guardrails", "", "| Guardrail | Resultado |", "|---|---:|"])
    lines.extend(f"| `{name}` | {value:.2%} |" for name, value in report["guardrails"].items())
    lines.extend(["", "## Casos", "", "| ID | Task | Score |", "|---|---|---:|"])
    lines.extend(f"| `{row['id']}` | `{row['task']}` | {row['score']:.2%} |" for row in report["cases"])
    if report["failures"]:
        lines.extend(["", "## Falhas", ""])
        lines.extend(f"- {item}" for item in report["failures"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=ROOT / "evals" / "datasets" / "intelligence-v1.jsonl")
    parser.add_argument("--thresholds", type=Path, default=ROOT / "evals" / "thresholds.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evals" / "reports")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = evaluate(args.dataset.resolve(), args.thresholds.resolve())
    (args.output_dir / "latest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output_dir / "latest.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("passed", "case_count", "overall_score", "task_scores", "guardrails", "failures")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
