from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_source(root: Path) -> str:
    digest = hashlib.sha256()
    paths = sorted(
        [p for p in (root / "samples/vertical-slice/app").rglob("*.py")]
        + [root / "samples/vertical-slice/requirements.txt", root / "samples/vertical-slice/Dockerfile"]
    )
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an in-toto/SLSA-style provenance statement.")
    parser.add_argument("--sbom", default="artifacts/sbom.cdx.json")
    parser.add_argument("--output", default="artifacts/provenance.json")
    parser.add_argument("--commit", default=os.getenv("GITHUB_SHA", "local"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sbom = root / args.sbom
    statement = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [
            {"name": "intelligent-backoffice-vertical-slice-source", "digest": {"sha256": digest_source(root)}},
            {"name": args.sbom, "digest": {"sha256": digest_file(sbom)}},
        ],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://github.com/leandrosflora/intelligent-backoffice-platform-architecture/p7-baseline",
                "externalParameters": {"commit": args.commit},
                "internalParameters": {"workflow": "p7-production-readiness.yml"},
                "resolvedDependencies": [{"uri": "git+repository", "digest": {"gitCommit": args.commit}}],
            },
            "runDetails": {
                "builder": {"id": "github-actions:p7-production-readiness"},
                "metadata": {"invocationId": os.getenv("GITHUB_RUN_ID", "local"), "startedOn": datetime.now(timezone.utc).isoformat()},
            },
        },
    }
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(statement, indent=2) + "\n", encoding="utf-8")
    print(f"Generated provenance statement at {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
