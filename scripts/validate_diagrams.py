from __future__ import annotations

import argparse
from pathlib import Path
import sys

EXPECTED_SOURCES = (
    "c4-context-current.puml",
    "c4-context-target.puml",
    "c4-container-current.puml",
    "c4-container-target.puml",
    "c4-component-workflow-orchestrator.puml",
    "c4-component-document-intelligence.puml",
    "c4-deployment-local.puml",
    "c4-deployment-observed-baseline.puml",
    "c4-deployment-distributed-baseline.puml",
    "c4-deployment-production-target.puml",
    "c4-trust-boundaries.puml",
    "sequence-case-intake.puml",
    "sequence-investigation-approval.puml",
    "sequence-governed-execution.puml",
    "sequence-missing-evidence.puml",
    "sequence-outbox-delivery.puml",
    "sequence-retry-dlq-replay.puml",
)

REQUIRED_C4_INCLUDES = {
    "c4-context-current.puml": "!include <C4/C4_Context>",
    "c4-context-target.puml": "!include <C4/C4_Context>",
    "c4-container-current.puml": "!include <C4/C4_Container>",
    "c4-container-target.puml": "!include <C4/C4_Container>",
}

LEGACY_C4_MACROS = (
    "C4Person(",
    "C4System(",
    "C4External(",
    "C4Container(",
    "C4ContainerDb(",
    "C4Queue(",
)


def validate_source(path: Path) -> list[str]:
    errors: list[str] = []
    content = path.read_text(encoding="utf-8")
    if "@startuml" not in content:
        errors.append(f"{path}: missing @startuml")
    if "@enduml" not in content:
        errors.append(f"{path}: missing @enduml")
    if content.count("@startuml") != content.count("@enduml"):
        errors.append(f"{path}: unbalanced @startuml/@enduml")
    if "!includeurl" in content.lower():
        errors.append(f"{path}: remote includes are not allowed")
    if "http://" in content.lower() or "https://" in content.lower():
        errors.append(f"{path}: external URLs are not allowed in diagram sources")

    required_include = REQUIRED_C4_INCLUDES.get(path.name)
    if required_include and required_include not in content:
        errors.append(f"{path}: missing required C4-PlantUML include: {required_include}")

    if required_include:
        for macro in LEGACY_C4_MACROS:
            if macro in content:
                errors.append(f"{path}: legacy macro is not allowed: {macro}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-generated", action="store_true", help="Require SVG and PNG output for every PlantUML source.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source_dir = root / "C4"
    output_dir = root / "docs" / "assets" / "diagrams"
    errors: list[str] = []
    for filename in EXPECTED_SOURCES:
        path = source_dir / filename
        if not path.exists():
            errors.append(f"Missing diagram source: C4/{filename}")
            continue
        errors.extend(validate_source(path))
        if args.require_generated:
            stem = path.stem
            for extension in ("svg", "png"):
                generated = output_dir / f"{stem}.{extension}"
                if not generated.exists() or generated.stat().st_size == 0:
                    errors.append(f"Missing generated diagram: docs/assets/diagrams/{stem}.{extension}")
    unexpected = sorted(path.name for path in source_dir.glob("*.puml") if path.name not in EXPECTED_SOURCES)
    if unexpected:
        errors.append("PlantUML sources are not registered in validate_diagrams.py: " + ", ".join(unexpected))
    if errors:
        print("Diagram validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    suffix = " with generated artifacts" if args.require_generated else ""
    print(f"Diagram sources are valid{suffix}: {len(EXPECTED_SOURCES)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
