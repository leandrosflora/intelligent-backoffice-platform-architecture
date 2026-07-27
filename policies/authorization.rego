package intelligent_backoffice.authorization

import rego.v1

default allow := false

decision := {
    "allow": allow,
    "reason": reason,
    "obligations": [item | obligation[item]],
}

reason := "allowed" if allow
reason := "default-deny" if not allow

operation_action if input.action in {"event.read", "event.replay", "timer.schedule"}
audit_action if input.action == "audit.read"
approval_action if input.action == "approval.decide"
execution_action if input.action == "execution.request"

purpose_matches_action if {
    operation_action
    input.purpose == "OPERATIONS"
}
purpose_matches_action if {
    audit_action
    input.purpose == "AUDIT"
}
purpose_matches_action if {
    approval_action
    input.purpose in {"CASE_MANAGEMENT", "APPROVAL"}
}
purpose_matches_action if {
    execution_action
    input.purpose in {"CASE_MANAGEMENT", "EXECUTION"}
}
purpose_matches_action if {
    not operation_action
    not audit_action
    not approval_action
    not execution_action
    input.purpose in {"CASE_MANAGEMENT", "CASE_PROCESSING"}
}

identity_profile_valid if {
    not input.context.identity_mode
}
identity_profile_valid if {
    input.context.identity_mode != "jwt"
}
identity_profile_valid if {
    input.context.identity_mode == "jwt"
    input.subject.authentication_method == "SIGNED_JWT"
    input.subject.token_id != ""
}

valid_common_context if {
    input.subject.id != ""
    input.subject.type in {"HUMAN", "WORKLOAD"}
    count(input.subject.roles) > 0
    input.subject.tenant_id != ""
    input.resource.tenant_id != ""
    input.subject.tenant_id == input.resource.tenant_id
    input.action != ""
    input.purpose != ""
    input.correlation_id != ""
    purpose_matches_action
    identity_profile_valid
}

has_role(role) if role in input.subject.roles

has_any_role(roles) if {
    some role in roles
    has_role(role)
}

case_version_present if input.context.case_version > 0

evidence_present if count(input.context.evidence_references) > 0

terminal_state(state) if state in {"EXECUTED", "CLOSED", "REJECTED", "CANCELLED", "EXPIRED", "FAILED"}

allow if {
    valid_common_context
    input.action == "case.create"
    has_role("case-manager")
}

allow if {
    valid_common_context
    input.action == "case.read"
    has_any_role({"case-reader", "case-manager", "operations-analyst", "approver", "auditor"})
}

allow if {
    valid_common_context
    input.action == "case.cancel"
    input.subject.type == "HUMAN"
    has_role("case-manager")
    input.resource.state in {"CREATED", "AWAITING_DOCUMENTS", "DOCUMENTS_RECEIVED", "DOCUMENTS_VALIDATED"}
    case_version_present
}

allow if {
    valid_common_context
    input.action == "document.register"
    has_any_role({"case-manager", "document-processor"})
    input.resource.state in {"CREATED", "AWAITING_DOCUMENTS", "DOCUMENTS_RECEIVED"}
    case_version_present
}

allow if {
    valid_common_context
    input.action == "document.read"
    has_any_role({"document-processor", "operations-analyst", "approver", "auditor"})
}

allow if {
    valid_common_context
    input.action == "evidence.read"
    has_any_role({"operations-analyst", "decision-agent", "approver", "auditor"})
}

allow if {
    valid_common_context
    input.action == "investigation.execute"
    has_any_role({"investigator", "operations-analyst"})
    input.resource.state == "DOCUMENTS_VALIDATED"
    case_version_present
    evidence_present
}

allow if {
    valid_common_context
    input.action == "recommendation.create"
    has_any_role({"decision-agent", "operations-analyst"})
    input.resource.state == "UNDER_INVESTIGATION"
    case_version_present
    evidence_present
}

allow if {
    valid_common_context
    input.action == "approval.decide"
    input.subject.type == "HUMAN"
    has_role("approver")
    input.resource.state == "AWAITING_APPROVAL"
    case_version_present
    input.context.recommendation_actor_id != input.subject.id
    input.context.recommendation_version == input.context.approved_recommendation_version
    input.context.authority_limit >= input.context.amount
}

allow if {
    valid_common_context
    input.action == "execution.request"
    input.subject.type == "WORKLOAD"
    has_role("execution-service")
    input.resource.state == "APPROVED"
    input.context.approval_status == "APPROVED"
    input.context.approval_valid == true
    input.context.recommendation_version == input.context.approved_recommendation_version
    input.context.idempotency_key != ""
    input.context.command_hash != ""
    evidence_present
}

allow if {
    valid_common_context
    input.action == "execution.read"
    has_any_role({"execution-service", "reconciler", "case-manager", "auditor"})
}

allow if {
    valid_common_context
    input.action == "reconciliation.resolve"
    has_role("reconciler")
    input.resource.state == "RECONCILIATION_REQUIRED"
    case_version_present
}

allow if {
    valid_common_context
    input.action == "audit.read"
    input.subject.type == "HUMAN"
    has_role("auditor")
    input.purpose == "AUDIT"
}

allow if {
    valid_common_context
    input.action == "event.read"
    input.subject.type == "HUMAN"
    input.purpose == "OPERATIONS"
    has_any_role({"platform-operator", "auditor"})
}

allow if {
    valid_common_context
    input.action == "timer.schedule"
    input.subject.type == "HUMAN"
    input.purpose == "OPERATIONS"
    has_any_role({"case-manager", "platform-operator"})
    not terminal_state(input.resource.state)
}

allow if {
    valid_common_context
    input.action == "event.replay"
    input.subject.type == "HUMAN"
    input.purpose == "OPERATIONS"
    has_role("platform-operator")
    input.resource.state == "OPEN"
    input.context.source == "DEAD_LETTER"
    count(input.context.reason) >= 10
}

obligation["audit-decision"] if valid_common_context
obligation["tenant-match"] if valid_common_context
obligation["verify-signed-identity"] if input.context.identity_mode == "jwt"
obligation["verify-purpose-binding"] if valid_common_context
obligation["redact-sensitive-data"] if input.action in {"case.read", "document.read", "evidence.read", "execution.read", "audit.read", "event.read"}
obligation["verify-case-version"] if input.action in {"case.cancel", "document.register", "investigation.execute", "recommendation.create", "approval.decide", "reconciliation.resolve"}
obligation["verify-segregation-of-duties"] if input.action == "approval.decide"
obligation["verify-approval"] if input.action == "execution.request"
obligation["verify-idempotency"] if input.action == "execution.request"
obligation["verify-evidence"] if input.action in {"investigation.execute", "recommendation.create", "execution.request"}
obligation["reconcile-on-ambiguous-result"] if input.action in {"execution.request", "reconciliation.resolve"}
obligation["record-replay-audit"] if input.action == "event.replay"
obligation["preserve-original-event"] if input.action == "event.replay"
