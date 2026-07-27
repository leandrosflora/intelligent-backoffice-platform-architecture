from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import HTTPException
from opentelemetry import trace

from .config import Settings
from .observability import POLICY_DECISIONS, POLICY_DURATION
from .security import RequestContext


class PolicyClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tracer = trace.get_tracer(settings.service_name)

    def authorize(self, ctx: RequestContext, action: str, resource: dict[str, Any], context: dict[str, Any] | None = None) -> None:
        data = {
            "subject": {"id": ctx.subject_id, "type": ctx.subject_type, "roles": ctx.roles, "tenant_id": ctx.tenant_id},
            "action": action,
            "resource": resource,
            "purpose": "AUDIT" if action == "audit.read" else "CASE_MANAGEMENT",
            "correlation_id": ctx.correlation_id,
            "context": context or {},
        }
        started = time.perf_counter()
        with self.tracer.start_as_current_span("policy.authorize") as span:
            span.set_attribute("backoffice.policy.action", action)
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
    common = bool(subject.get("id") and subject.get("roles") and subject.get("tenant_id") == resource.get("tenant_id") and i.get("correlation_id"))
    roles, action = set(subject.get("roles", [])), i.get("action")
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
    return {"allow": allow, "reason": "allowed" if allow else "default-deny"}
