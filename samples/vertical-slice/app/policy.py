from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import HTTPException
from opentelemetry import trace

from .config import Settings
from .observability import POLICY_DECISIONS, POLICY_DURATION
from .security import RequestContext


_OPERATION_ACTIONS = {"event.read", "event.replay", "timer.schedule"}


class PolicyClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tracer = trace.get_tracer(settings.service_name)

    def authorize(self, ctx: RequestContext, action: str, resource: dict[str, Any], context: dict[str, Any] | None = None) -> None:
        derived_purpose = "AUDIT" if action == "audit.read" else "OPERATIONS" if action in _OPERATION_ACTIONS else "CASE_MANAGEMENT"
        purpose = ctx.purpose if ctx.authentication_method == "SIGNED_JWT" else derived_purpose
        policy_context = dict(context or {})
        policy_context["identity_mode"] = self.settings.identity_mode.lower()
        data = {
            "subject": {
                "id": ctx.subject_id,
                "type": ctx.subject_type,
                "roles": ctx.roles,
                "tenant_id": ctx.tenant_id,
                "authentication_method": ctx.authentication_method,
                "token_id": ctx.token_id,
            },
            "action": action,
            "resource": resource,
            "purpose": purpose,
            "correlation_id": ctx.correlation_id,
            "context": policy_context,
        }
        started = time.perf_counter()
        with self.tracer.start_as_current_span("policy.authorize") as span:
            span.set_attribute("backoffice.policy.action", action)
            span.set_attribute("backoffice.identity.method", ctx.authentication_method)
            try:
                if self.settings.policy_mode == "opa":
                    response = httpx.post(
                        f"{self.settings.opa_url}/v1/data/intelligent_backoffice/authorization/decision",
                        json={"input": data},
                        timeout=3.0,
                    )
                    response.raise_for_status()
                    decision = response.json().get("result", {})
                else:
                    decision = embedded_decision(data)
            except Exception as exc:
                POLICY_DECISIONS.labels(action, "unavailable").inc()
                span.set_attribute("backoffice.policy.decision", "unavailable")
                raise HTTPException(503, f"Policy decision unavailable: {exc}") from exc
            finally:
                POLICY_DURATION.labels(action).observe(time.perf_counter() - started)

            allowed = bool(decision.get("allow", False))
            outcome = "allow" if allowed else "deny"
            POLICY_DECISIONS.labels(action, outcome).inc()
            span.set_attribute("backoffice.policy.decision", outcome)
            if not allowed:
                raise HTTPException(403, detail={"reason": decision.get("reason", "default-deny")})


def embedded_decision(i: dict[str, Any]) -> dict[str, Any]:
    subject, resource, context = i["subject"], i["resource"], i.get("context", {})
    action = i.get("action")
    expected_purpose = "AUDIT" if action == "audit.read" else "OPERATIONS" if action in _OPERATION_ACTIONS else "CASE_MANAGEMENT"
    identity_valid = context.get("identity_mode") != "jwt" or (
        subject.get("authentication_method") == "SIGNED_JWT" and bool(subject.get("token_id"))
    )
    common = bool(
        subject.get("id")
        and subject.get("roles")
        and subject.get("tenant_id") == resource.get("tenant_id")
        and i.get("correlation_id")
        and i.get("purpose") == expected_purpose
        and identity_valid
    )
    roles = set(subject.get("roles", []))
    allow = False
    if common and action == "case.create":
        allow = "case-manager" in roles
    elif common and action == "case.read":
        allow = bool(roles & {"case-reader", "case-manager", "operations-analyst", "approver", "auditor"})
    elif common and action == "document.register":
        allow = bool(roles & {"case-manager", "document-processor"}) and resource.get("state") in {"CREATED", "AWAITING_DOCUMENTS", "DOCUMENTS_RECEIVED"} and context.get("case_version", 0) > 0
    elif common and action == "investigation.execute":
        allow = bool(roles & {"investigator", "operations-analyst"}) and resource.get("state") == "DOCUMENTS_VALIDATED" and bool(context.get("evidence_references"))
    elif common and action == "recommendation.create":
        allow = bool(roles & {"decision-agent", "operations-analyst"}) and resource.get("state") == "UNDER_INVESTIGATION" and bool(context.get("evidence_references"))
    elif common and action == "approval.decide":
        allow = subject.get("type") == "HUMAN" and "approver" in roles and resource.get("state") == "AWAITING_APPROVAL" and context.get("recommendation_actor_id") != subject.get("id") and context.get("recommendation_version") == context.get("approved_recommendation_version") and context.get("authority_limit", 0) >= context.get("amount", 1)
    elif common and action == "execution.request":
        allow = subject.get("type") == "WORKLOAD" and "execution-service" in roles and resource.get("state") == "APPROVED" and context.get("approval_status") == "APPROVED" and context.get("approval_valid") is True and context.get("recommendation_version") == context.get("approved_recommendation_version") and bool(context.get("idempotency_key")) and bool(context.get("command_hash")) and bool(context.get("evidence_references"))
    elif common and action == "execution.read":
        allow = bool(roles & {"execution-service", "reconciler", "case-manager", "auditor"})
    elif common and action == "reconciliation.resolve":
        allow = "reconciler" in roles and resource.get("state") == "RECONCILIATION_REQUIRED" and context.get("case_version", 0) > 0
    elif common and action == "event.read":
        allow = subject.get("type") == "HUMAN" and bool(roles & {"platform-operator", "auditor"})
    elif common and action == "timer.schedule":
        allow = subject.get("type") == "HUMAN" and bool(roles & {"case-manager", "platform-operator"}) and resource.get("state") not in {"EXECUTED", "CLOSED", "REJECTED", "CANCELLED", "EXPIRED", "FAILED"}
    elif common and action == "event.replay":
        allow = subject.get("type") == "HUMAN" and "platform-operator" in roles and resource.get("state") == "OPEN" and context.get("source") == "DEAD_LETTER" and len(context.get("reason", "")) >= 10
    return {"allow": allow, "reason": "allowed" if allow else "default-deny"}
