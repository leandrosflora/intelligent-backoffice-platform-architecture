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
