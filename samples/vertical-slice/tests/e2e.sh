#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8080}"
TENANT_ID="${TENANT_ID:-11111111-1111-4111-8111-111111111111}"
OTHER_TENANT_ID="22222222-2222-4222-8222-222222222222"
export DEMO_JWT_SECRET="${DEMO_JWT_SECRET:-local-development-secret-change-me-1234567890}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TOKEN_SCRIPT="$ROOT_DIR/samples/vertical-slice/scripts/create-demo-token.py"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

token() {
  python "$TOKEN_SCRIPT" "$@"
}

uuid() {
  python -c "import uuid; print(uuid.uuid4())"
}

MANAGER_TOKEN="$(token --subject manager-1 --type HUMAN --tenant "$TENANT_ID" \
  --roles case-manager,case-reader --purpose OPERATIONS)"
ANALYST_TOKEN="$(token --subject analyst-1 --type HUMAN --tenant "$TENANT_ID" \
  --roles operations-analyst,investigator,decision-agent --purpose OPERATIONS)"
APPROVER_TOKEN="$(token --subject approver-1 --type HUMAN --tenant "$TENANT_ID" \
  --roles approver --purpose OPERATIONS --authority-limit 10000.00)"
EXECUTION_TOKEN="$(token --subject execution-service --type WORKLOAD --tenant "$TENANT_ID" \
  --roles execution-service --purpose OPERATIONS)"
AUDITOR_TOKEN="$(token --subject auditor-1 --type HUMAN --tenant "$TENANT_ID" \
  --roles auditor --purpose AUDIT)"
OTHER_TOKEN="$(token --subject other-manager --type HUMAN --tenant "$OTHER_TENANT_ID" \
  --roles case-manager,case-reader --purpose OPERATIONS)"

wait_for_health() {
  for attempt in $(seq 1 60); do
    if curl --fail --silent "$API_URL/health" | jq -e '.status == "ok"' >/dev/null; then
      return 0
    fi
    sleep 2
  done

  echo "API não ficou saudável." >&2
  docker compose --profile vertical-slice logs api opa postgres >&2 || true
  return 1
}

request() {
  local method="$1"
  local path="$2"
  local token_value="$3"
  local tenant="$4"
  local correlation="$5"
  local body="${6:-}"
  local idempotency="${7:-}"
  local if_match="${8:-}"
  local output="$9"

  local args=(
    --silent --show-error
    --request "$method"
    --url "$API_URL$path"
    --header "Authorization: Bearer $token_value"
    --header "X-Tenant-Id: $tenant"
    --header "X-Correlation-Id: $correlation"
    --header "Accept: application/json"
    --output "$output"
    --write-out "%{http_code}"
  )

  if [[ -n "$body" ]]; then
    args+=(--header "Content-Type: application/json" --data "$body")
  fi
  if [[ -n "$idempotency" ]]; then
    args+=(--header "Idempotency-Key: $idempotency")
  fi
  if [[ -n "$if_match" ]]; then
    args+=(--header "If-Match: \"$if_match\"")
  fi

  curl "${args[@]}"
}

get_case_version() {
  local case_id="$1"
  local output="$TMP_DIR/case.json"
  local status
  status="$(request GET "/v1/cases/$case_id" "$MANAGER_TOKEN" "$TENANT_ID" \
    "$(uuid)" "" "" "" "$output")"
  [[ "$status" == "200" ]] || { cat "$output" >&2; return 1; }
  jq -r '.caseVersion' "$output"
}

wait_for_health

CREATE_BODY='{
  "externalReference": "E2E-CASE-001",
  "disputeType": "CARD_PURCHASE",
  "channel": "API",
  "disputedAmount": {"currency": "BRL", "amount": "150.00"},
  "customerReference": "customer-token-001"
}'
CREATE_OUTPUT="$TMP_DIR/create.json"
CREATE_STATUS="$(request POST "/v1/cases" "$MANAGER_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$CREATE_BODY" "create-case-001" "" "$CREATE_OUTPUT")"
[[ "$CREATE_STATUS" == "201" || "$CREATE_STATUS" == "200" ]] || {
  cat "$CREATE_OUTPUT" >&2
  exit 1
}
CASE_ID="$(jq -r '.caseId' "$CREATE_OUTPUT")"
VERSION="$(jq -r '.caseVersion' "$CREATE_OUTPUT")"

DOCUMENT_BODY='{
  "documentType": "TRANSACTION_PROOF",
  "mediaType": "application/pdf",
  "checksum": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "storageReference": "quarantine://synthetic/e2e-proof.pdf"
}'
DOCUMENT_OUTPUT="$TMP_DIR/document.json"
DOCUMENT_STATUS="$(request POST "/v1/cases/$CASE_ID/documents" "$MANAGER_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$DOCUMENT_BODY" "register-document-001" "$VERSION" "$DOCUMENT_OUTPUT")"
[[ "$DOCUMENT_STATUS" == "202" ]] || { cat "$DOCUMENT_OUTPUT" >&2; exit 1; }
VERSION="$(get_case_version "$CASE_ID")"

EVIDENCE_OUTPUT="$TMP_DIR/evidence.json"
EVIDENCE_STATUS="$(request GET "/v1/cases/$CASE_ID/evidence" "$ANALYST_TOKEN" "$TENANT_ID" \
  "$(uuid)" "" "" "" "$EVIDENCE_OUTPUT")"
[[ "$EVIDENCE_STATUS" == "200" ]] || { cat "$EVIDENCE_OUTPUT" >&2; exit 1; }
EVIDENCE_ID="$(jq -r '.[0].evidenceId' "$EVIDENCE_OUTPUT")"

INVESTIGATION_BODY="$(jq -nc --argjson version "$VERSION" '{
  caseVersion: $version,
  requestedChecks: ["TRANSACTION_LOOKUP", "DOCUMENT_CONSISTENCY"]
}')"
INVESTIGATION_OUTPUT="$TMP_DIR/investigation.json"
INVESTIGATION_STATUS="$(request POST "/v1/cases/$CASE_ID/investigations" "$ANALYST_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$INVESTIGATION_BODY" "investigation-001" "$VERSION" "$INVESTIGATION_OUTPUT")"
[[ "$INVESTIGATION_STATUS" == "202" ]] || { cat "$INVESTIGATION_OUTPUT" >&2; exit 1; }
INVESTIGATION_ID="$(jq -r '.investigationId' "$INVESTIGATION_OUTPUT")"
VERSION="$(get_case_version "$CASE_ID")"

RECOMMENDATION_BODY="$(jq -nc --argjson version "$VERSION" --arg investigation "$INVESTIGATION_ID" '{
  caseVersion: $version,
  investigationId: $investigation
}')"
RECOMMENDATION_OUTPUT="$TMP_DIR/recommendation.json"
RECOMMENDATION_STATUS="$(request POST "/v1/cases/$CASE_ID/recommendations" "$ANALYST_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$RECOMMENDATION_BODY" "recommendation-001" "$VERSION" "$RECOMMENDATION_OUTPUT")"
[[ "$RECOMMENDATION_STATUS" == "201" ]] || { cat "$RECOMMENDATION_OUTPUT" >&2; exit 1; }
RECOMMENDATION_ID="$(jq -r '.recommendationId' "$RECOMMENDATION_OUTPUT")"
RECOMMENDATION_VERSION="$(jq -r '.recommendationVersion' "$RECOMMENDATION_OUTPUT")"
VERSION="$(get_case_version "$CASE_ID")"

APPROVAL_BODY="$(jq -nc \
  --argjson version "$VERSION" \
  --arg recommendation "$RECOMMENDATION_ID" \
  --argjson recommendationVersion "$RECOMMENDATION_VERSION" \
  --arg evidence "$EVIDENCE_ID" '{
    caseVersion: $version,
    recommendationId: $recommendation,
    recommendationVersion: $recommendationVersion,
    decision: "APPROVE",
    reason: "Aprovação humana do cenário E2E.",
    evidenceReferences: [$evidence]
  }')"
APPROVAL_OUTPUT="$TMP_DIR/approval.json"
APPROVAL_STATUS="$(request POST "/v1/cases/$CASE_ID/approvals" "$APPROVER_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$APPROVAL_BODY" "approval-001" "$VERSION" "$APPROVAL_OUTPUT")"
[[ "$APPROVAL_STATUS" == "201" ]] || { cat "$APPROVAL_OUTPUT" >&2; exit 1; }
APPROVAL_ID="$(jq -r '.approvalId' "$APPROVAL_OUTPUT")"
VERSION="$(get_case_version "$CASE_ID")"

EXECUTION_BODY="$(jq -nc \
  --argjson version "$VERSION" \
  --arg approval "$APPROVAL_ID" \
  --argjson recommendationVersion "$RECOMMENDATION_VERSION" \
  --arg evidence "$EVIDENCE_ID" '{
    caseVersion: $version,
    approvalId: $approval,
    recommendationVersion: $recommendationVersion,
    commandType: "MOCK_REFUND",
    commandHash: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    evidenceReferences: [$evidence]
  }')"
EXECUTION_OUTPUT="$TMP_DIR/execution.json"
EXECUTION_STATUS="$(request POST "/v1/cases/$CASE_ID/executions" "$EXECUTION_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$EXECUTION_BODY" "execution-001" "$VERSION" "$EXECUTION_OUTPUT")"
[[ "$EXECUTION_STATUS" == "202" ]] || { cat "$EXECUTION_OUTPUT" >&2; exit 1; }
jq -e '.status == "SUCCEEDED"' "$EXECUTION_OUTPUT" >/dev/null
EXECUTION_ID="$(jq -r '.executionId' "$EXECUTION_OUTPUT")"

REPLAY_OUTPUT="$TMP_DIR/execution-replay.json"
REPLAY_STATUS="$(request POST "/v1/cases/$CASE_ID/executions" "$EXECUTION_TOKEN" "$TENANT_ID" \
  "$(uuid)" "$EXECUTION_BODY" "execution-001" "$VERSION" "$REPLAY_OUTPUT")"
[[ "$REPLAY_STATUS" == "202" ]] || { cat "$REPLAY_OUTPUT" >&2; exit 1; }
[[ "$(jq -r '.executionId' "$REPLAY_OUTPUT")" == "$EXECUTION_ID" ]]

FINAL_CASE_OUTPUT="$TMP_DIR/final-case.json"
FINAL_CASE_STATUS="$(request GET "/v1/cases/$CASE_ID" "$MANAGER_TOKEN" "$TENANT_ID" \
  "$(uuid)" "" "" "" "$FINAL_CASE_OUTPUT")"
[[ "$FINAL_CASE_STATUS" == "200" ]] || { cat "$FINAL_CASE_OUTPUT" >&2; exit 1; }
jq -e '.state == "EXECUTED"' "$FINAL_CASE_OUTPUT" >/dev/null

TIMELINE_OUTPUT="$TMP_DIR/timeline.json"
TIMELINE_STATUS="$(request GET "/v1/cases/$CASE_ID/timeline" "$AUDITOR_TOKEN" "$TENANT_ID" \
  "$(uuid)" "" "" "" "$TIMELINE_OUTPUT")"
[[ "$TIMELINE_STATUS" == "200" ]] || { cat "$TIMELINE_OUTPUT" >&2; exit 1; }
jq -e 'length >= 8' "$TIMELINE_OUTPUT" >/dev/null

DENIED_OUTPUT="$TMP_DIR/timeline-denied.json"
DENIED_STATUS="$(request GET "/v1/cases/$CASE_ID/timeline" "$MANAGER_TOKEN" "$TENANT_ID" \
  "$(uuid)" "" "" "" "$DENIED_OUTPUT")"
[[ "$DENIED_STATUS" == "403" ]] || { cat "$DENIED_OUTPUT" >&2; exit 1; }

CROSS_TENANT_OUTPUT="$TMP_DIR/cross-tenant.json"
CROSS_TENANT_STATUS="$(request GET "/v1/cases/$CASE_ID" "$OTHER_TOKEN" "$OTHER_TENANT_ID" \
  "$(uuid)" "" "" "" "$CROSS_TENANT_OUTPUT")"
[[ "$CROSS_TENANT_STATUS" == "404" ]] || {
  cat "$CROSS_TENANT_OUTPUT" >&2
  exit 1
}

echo "Vertical slice E2E concluído: case=$CASE_ID execution=$EXECUTION_ID"
