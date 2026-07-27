from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def error(errors, message):
    errors.append(message)


def find_kind(documents, kind):
    for document in documents:
        if document and document.get("kind") == kind:
            return document
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-evidence", action="store_true")
    args = parser.parse_args()
    errors = []

    identity = load_yaml("security/workload-identity.yaml")
    if identity.get("algorithm") != "EdDSA":
        error(errors, "workload identity must use EdDSA in the executable baseline")
    if int(identity.get("maxTokenTtlSeconds", 9999)) > 300:
        error(errors, "workload identity token TTL must be at most 300 seconds")
    required_claims = {"iss", "sub", "aud", "iat", "exp", "jti", "tenant_id", "roles", "subject_type", "purpose"}
    if not required_claims.issubset(set(identity.get("requiredClaims", []))):
        error(errors, "workload identity contract is missing required claims")

    inventory = load_yaml("security/secrets/inventory.yaml")
    for item in inventory.get("secrets", []):
        if "value" in item:
            error(errors, f"secret inventory must not include values: {item.get('id')}")
        if int(item.get("rotationDays", 999)) > 90:
            error(errors, f"secret rotation exceeds 90 days: {item.get('id')}")

    supply = load_yaml("security/supply-chain/policy.yaml")
    if supply.get("allowMutableTags") is not False:
        error(errors, "supply-chain policy must prohibit mutable tags")
    if not {"sbom", "provenance", "digestPinnedImage"}.issubset(set(supply.get("requiredEvidence", []))):
        error(errors, "supply-chain policy is missing mandatory evidence")

    readiness = load_yaml("governance/production-readiness.yaml")
    if readiness.get("status") != "NOT_PRODUCTION_READY":
        error(errors, "repository must not claim production readiness while target gates remain open")
    gates = readiness.get("gates", [])
    ids = [gate.get("id") for gate in gates]
    if len(ids) != len(set(ids)):
        error(errors, "production readiness gate IDs must be unique")
    if not readiness.get("blockers"):
        error(errors, "production readiness must list unresolved blockers")
    for gate in gates:
        if not gate.get("owner") or not gate.get("evidence"):
            error(errors, f"gate is incomplete: {gate.get('id')}")
        for evidence in gate.get("evidence", []):
            if evidence.startswith("repo:") and not (ROOT / evidence.removeprefix("repo:")).exists():
                error(errors, f"gate {gate.get('id')} references missing evidence {evidence}")

    requirements = (ROOT / "samples/vertical-slice/requirements.txt").read_text(encoding="utf-8").splitlines()
    pin = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[^\]]+\])?==[A-Za-z0-9_.+-]+$")
    for line in requirements:
        line = line.strip()
        if line and not line.startswith("#") and not pin.match(line):
            error(errors, f"dependency is not pinned: {line}")

    dockerfile = (ROOT / "samples/vertical-slice/Dockerfile").read_text(encoding="utf-8")
    if "USER 10001:10001" not in dockerfile:
        error(errors, "runtime image must run as the non-root UID/GID 10001")
    if "FROM " not in dockerfile or ":latest" in dockerfile:
        error(errors, "runtime image must use an explicit non-latest base tag")

    kubernetes_files = sorted((ROOT / "deploy/kubernetes/base").glob("*.yaml"))
    documents = []
    for path in kubernetes_files:
        documents.extend(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    deployment = find_kind(documents, "Deployment")
    pdb = find_kind(documents, "PodDisruptionBudget")
    hpa = find_kind(documents, "HorizontalPodAutoscaler")
    network_policy = find_kind(documents, "NetworkPolicy")
    if not deployment or int(deployment.get("spec", {}).get("replicas", 0)) < 3:
        error(errors, "production target Deployment must define at least three replicas")
    else:
        pod = deployment["spec"]["template"]["spec"]
        container = pod["containers"][0]
        security = container.get("securityContext", {})
        if security.get("runAsNonRoot") is not True or security.get("readOnlyRootFilesystem") is not True:
            error(errors, "production target container securityContext is incomplete")
        if "requests" not in container.get("resources", {}) or "limits" not in container.get("resources", {}):
            error(errors, "production target must define resource requests and limits")
        if "@sha256:" not in container.get("image", ""):
            error(errors, "production target image must be digest pinned")
        if pod.get("automountServiceAccountToken") is not False:
            error(errors, "service account token automount must be disabled")
    if not pdb or int(pdb.get("spec", {}).get("minAvailable", 0)) < 2:
        error(errors, "PDB must keep at least two replicas available")
    if not hpa or int(hpa.get("spec", {}).get("minReplicas", 0)) < 3:
        error(errors, "HPA must preserve at least three replicas")
    if not network_policy:
        error(errors, "production target must define a NetworkPolicy")

    capacity = load_yaml("capacity/profile.yaml")
    if int(capacity.get("requests", 0)) < 50 or int(capacity.get("concurrency", 0)) < 4:
        error(errors, "capacity profile is too small to be meaningful")
    if float(capacity.get("thresholds", {}).get("p95Seconds", 99)) > 2:
        error(errors, "capacity p95 threshold must be at most two seconds")

    local_ignore = ROOT / ".local/.gitignore"
    if not local_ignore.exists() or "*" not in local_ignore.read_text(encoding="utf-8"):
        error(errors, ".local/.gitignore must exclude local identity and KMS material")

    if args.require_evidence:
        sbom_path = ROOT / "artifacts/sbom.cdx.json"
        provenance_path = ROOT / "artifacts/provenance.json"
        backup_report = ROOT / "artifacts/backup-drill/report.json"
        capacity_report = ROOT / "artifacts/capacity-report.json"
        for path in (sbom_path, provenance_path, backup_report, capacity_report):
            if not path.exists():
                error(errors, f"required generated evidence is missing: {path.relative_to(ROOT)}")
        if sbom_path.exists():
            sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
            if sbom.get("bomFormat") != "CycloneDX" or len(sbom.get("components", [])) < 5:
                error(errors, "generated SBOM is invalid")
        if provenance_path.exists():
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            if provenance.get("predicateType") != "https://slsa.dev/provenance/v1":
                error(errors, "generated provenance is invalid")
        if backup_report.exists() and json.loads(backup_report.read_text()).get("status") != "PASSED":
            error(errors, "backup/restore drill did not pass")
        if capacity_report.exists() and json.loads(capacity_report.read_text()).get("status") != "PASSED":
            error(errors, "capacity gate did not pass")

    if errors:
        print("P7 validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"P7 production-readiness baseline is valid: {len(gates)} gates, {len(kubernetes_files)} Kubernetes manifests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
