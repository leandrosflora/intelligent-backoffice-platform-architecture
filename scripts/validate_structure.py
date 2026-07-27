from pathlib import Path
import sys

REQUIRED_PATHS = (
    Path(".github/workflows"),
    Path("C4"),
    Path("contracts/openapi"),
    Path("contracts/asyncapi"),
    Path("contracts/policy"),
    Path("docs/architecture"),
    Path("docs/case-study"),
    Path("docs/context/business-context.md"),
    Path("docs/functional/index.md"),
    Path("docs/functional/capability-map.md"),
    Path("docs/functional/domain-map.md"),
    Path("docs/functional/case-lifecycle.md"),
    Path("docs/functional/business-rules.md"),
    Path("docs/functional/roles-and-responsibilities.md"),
    Path("docs/functional/outcome-card.md"),
    Path("docs/functional/risk-classification.md"),
    Path("docs/functional/non-functional-requirements.md"),
    Path("docs/functional/traceability-matrix.md"),
    Path("docs/governance"),
    Path("docs/operations"),
    Path("docs/security"),
    Path("docs/services"),
    Path("policies"),
    Path("scripts"),
    Path("samples"),
    Path("mkdocs.yml"),
    Path("docker-compose.yml"),
    Path("README.md"),
    Path("IntelligentBackofficePlatformArchitecture.sln"),
)

missing = [str(path) for path in REQUIRED_PATHS if not path.exists()]

if missing:
    print("Required repository paths are missing:")
    for path in missing:
        print(f"- {path}")
    sys.exit(1)

print(f"Repository structure is valid: {len(REQUIRED_PATHS)} required paths found.")
