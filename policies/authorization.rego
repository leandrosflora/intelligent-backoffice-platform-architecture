package intelligent_backoffice.authorization

default allow = false

allow {
  input.subject != ""
  input.tenant_id != ""
  input.action == "case.read"
  input.subject_tenant_id == input.tenant_id
}

allow {
  input.subject != ""
  input.tenant_id != ""
  input.action == "financial.execute"
  input.approval.status == "APPROVED"
  input.approval.evidence_reference != ""
  input.idempotency_key != ""
}
