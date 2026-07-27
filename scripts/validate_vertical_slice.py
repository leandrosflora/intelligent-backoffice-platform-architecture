from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ENDPOINTS = {
    '"/health"',
    '"/v1/cases"',
    '"/v1/cases/{caseId:guid}"',
    '"/v1/cases/{caseId:guid}/documents"',
    '"/v1/cases/{caseId:guid}/evidence"',
    '"/v1/cases/{caseId:guid}/investigations"',
    '"/v1/cases/{caseId:guid}/recommendations"',
    '"/v1/cases/{caseId:guid}/approvals"',
    '"/v1/cases/{caseId:guid}/executions"',
    '"/v1/cases/{caseId:guid}/timeline"',
}

errors: list[str] = []

project = (ROOT / "samples/vertical-slice/src/IntelligentBackoffice.Api/IntelligentBackoffice.Api.csproj").read_text()
if "<TargetFramework>net10.0</TargetFramework>" not in project:
    errors.append("O projeto deve usar net10.0.")
if 'PackageReference Include="Npgsql"' not in project:
    errors.append("O projeto deve referenciar Npgsql.")

endpoints = (ROOT / "samples/vertical-slice/src/IntelligentBackoffice.Api/EndpointMappings.cs").read_text()
for endpoint in sorted(REQUIRED_ENDPOINTS):
    if endpoint not in endpoints:
        errors.append(f"Endpoint ausente no vertical slice: {endpoint}")

service = "\n".join(path.read_text() for path in sorted((ROOT / "samples/vertical-slice/src/IntelligentBackoffice.Api").glob("CaseWorkflowService*.cs")))
for marker in (
    '"case.create"',
    '"document.register"',
    '"investigation.execute"',
    '"recommendation.create"',
    '"approval.decide"',
    '"execution.request"',
    '"audit.read"',
    "RECONCILIATION_REQUIRED",
):
    if marker not in service:
        errors.append(f"Controle ou action ausente no workflow: {marker}")

store = (ROOT / "samples/vertical-slice/src/IntelligentBackoffice.Api/PostgresStore.cs").read_text()
for table in (
    "backoffice_cases",
    "backoffice_idempotency",
    "backoffice_timeline",
    "backoffice_outbox",
):
    if table not in store:
        errors.append(f"Tabela obrigatória ausente: {table}")

opa = (ROOT / "samples/vertical-slice/src/IntelligentBackoffice.Api/OpaAuthorizationClient.cs").read_text()
if "/v1/data/intelligent_backoffice/authorization/decision" not in opa:
    errors.append("O client deve consultar a decision document canônica do OPA.")
if "pdp-unavailable" not in opa:
    errors.append("O client OPA deve aplicar fail-closed.")

compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
services = compose.get("services", {})
for service_name in ("api", "postgres", "opa"):
    if service_name not in services:
        errors.append(f"Serviço Docker Compose ausente: {service_name}")

api_profiles = services.get("api", {}).get("profiles", [])
if "vertical-slice" not in api_profiles:
    errors.append("O serviço api deve pertencer ao profile vertical-slice.")

solution = (ROOT / "IntelligentBackofficePlatformArchitecture.sln").read_text()
if "IntelligentBackoffice.Api.csproj" not in solution:
    errors.append("A solution deve incluir o projeto do vertical slice.")

workflow = (ROOT / ".github/workflows/quality.yml").read_text()
for marker in (
    "dotnet build",
    "docker compose --profile vertical-slice up",
    "samples/vertical-slice/tests/e2e.sh",
):
    if marker not in workflow:
        errors.append(f"Quality workflow não valida o P4: {marker}")

if errors:
    print("Vertical slice validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Vertical slice structure and control markers are valid.")
