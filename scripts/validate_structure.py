from pathlib import Path
import sys

REQUIRED_PATHS = (
    Path(".github/workflows"),
    Path("C4/_theme.iuml"),
    Path("C4/c4-context-current.puml"),
    Path("C4/c4-context-target.puml"),
    Path("C4/c4-container-current.puml"),
    Path("C4/c4-container-target.puml"),
    Path("C4/c4-component-workflow-orchestrator.puml"),
    Path("C4/c4-component-document-intelligence.puml"),
    Path("C4/c4-deployment-local.puml"),
    Path("C4/c4-trust-boundaries.puml"),
    Path("C4/sequence-case-intake.puml"),
    Path("C4/sequence-investigation-approval.puml"),
    Path("C4/sequence-governed-execution.puml"),
    Path("C4/sequence-missing-evidence.puml"),
    Path("contracts/openapi"),
    Path("contracts/asyncapi"),
    Path("contracts/policy"),
    Path("docs/assets/diagrams/README.md"),
    Path("docs/architecture/index.md"),
    Path("docs/architecture/c4-context-current.md"),
    Path("docs/architecture/c4-context-target.md"),
    Path("docs/architecture/c4-container-current.md"),
    Path("docs/architecture/c4-container-target.md"),
    Path("docs/architecture/component-workflow-orchestrator.md"),
    Path("docs/architecture/component-document-intelligence.md"),
    Path("docs/architecture/deployment-local.md"),
    Path("docs/architecture/trust-boundaries.md"),
    Path("docs/architecture/sequence-diagrams.md"),
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
    Path("scripts/render-diagrams.sh"),
    Path("scripts/validate_diagrams.py"),
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
