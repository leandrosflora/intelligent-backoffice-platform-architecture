#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPA_IMAGE="${OPA_IMAGE:-openpolicyagent/opa:1.18.2-static}"

pull_image() {
  local attempt
  for attempt in 1 2 3; do
    if docker pull "$OPA_IMAGE"; then
      return 0
    fi
    if [ "$attempt" -lt 3 ]; then
      sleep $((attempt * 5))
    fi
  done
  echo "Falha ao baixar $OPA_IMAGE após 3 tentativas." >&2
  return 1
}

pull_image

docker run --rm \
  -v "$ROOT_DIR:/workspace:ro" \
  -w /workspace \
  "$OPA_IMAGE" \
  check --strict policies/authorization.rego policies/authorization_test.rego

docker run --rm \
  -v "$ROOT_DIR:/workspace:ro" \
  -w /workspace \
  "$OPA_IMAGE" \
  test policies --format=pretty
