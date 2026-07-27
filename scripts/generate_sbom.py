from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


PINNED = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?==([A-Za-z0-9_.+-]+)$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic dependency SBOM for the executable baseline.")
    parser.add_argument("--requirements", default="samples/vertical-slice/requirements.txt")
    parser.add_argument("--output", default="artifacts/sbom.cdx.json")
    args = parser.parse_args()

    components = []
    for raw in Path(args.requirements).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = PINNED.match(line)
        if not match:
            raise SystemExit(f"dependency is not pinned: {line}")
        name, version = match.groups()
        components.append(
            {
                "type": "library",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{name.lower()}@{version}",
            }
        )
    components.sort(key=lambda item: item["name"].lower())
    document = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "application",
                "name": "intelligent-backoffice-vertical-slice",
                "version": "0.7.0",
            },
            "tools": [{"vendor": "repository", "name": "scripts/generate_sbom.py"}],
        },
        "components": components,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Generated CycloneDX SBOM with {len(components)} pinned components at {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
