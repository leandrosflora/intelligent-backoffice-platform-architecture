from pathlib import Path
import sys

REQUIRED_PATHS = (
    Path(".github/workflows/quality.yml"),
    Path(".github/workflows/docs.yml"),
    Path(".github/workflows/vertical-slice.yml"),
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
    Path("contracts/README.md"),
    Path("contracts/catalog.yaml"),
    Path("contracts/openapi/platform-api.yaml"),
    Path("contracts/asyncapi/platform-events.yaml"),
    Path("contracts/policy/authorization.yaml"),
    Path("contracts/schemas/canonical-models.yaml"),
    Path("contracts/schemas/event-envelope.yaml"),
    Path("contracts/schemas/policy-contracts.yaml"),
    Path("policies/authorization.rego"),
    Path("policies/authorization_test.rego"),
    Path("docs/assets/diagrams/README.md"),
    Path("docs/architecture/index.md"),
    Path("docs/contracts/index.md"),
    Path("docs/implementation/index.md"),
    Path("docs/implementation/test-scenarios.md"),
    Path("docs/implementation/runbook.md"),
    Path("docs/case-study/index.md"),
    Path("docs/context/business-context.md"),
    Path("docs/functional/index.md"),
    Path("docs/governance/index.md"),
    Path("docs/operations/index.md"),
    Path("docs/security/index.md"),
    Path("docs/services/index.md"),
    Path("scripts/render-diagrams.sh"),
    Path("scripts/validate_diagrams.py"),
    Path("scripts/validate_contracts.py"),
    Path("scripts/test-policies.sh"),
    Path("scripts/run_vertical_slice_e2e.py"),
    Path("samples/vertical-slice/Dockerfile"),
    Path("samples/vertical-slice/README.md"),
    Path("samples/vertical-slice/app/main.py"),
    Path("samples/vertical-slice/tests/test_e2e.py"),
    Path("samples/vertical-slice/requirements.txt"),
    Path("samples/vertical-slice/requirements-dev.txt"),
    Path("requirements-docs.txt"),
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
