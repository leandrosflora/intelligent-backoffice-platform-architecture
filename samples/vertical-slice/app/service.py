from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from fastapi import HTTPException
from opentelemetry import trace

from .intelligence import classify_document, investigate_case, propose_recommendation
from .observability import (
    CASES_CREATED,
    EXECUTIONS,
    IDEMPOTENCY,
    RECONCILIATIONS,
    operation_span,
    record_transition,
)
from .policy import PolicyClient
from .schemas import (
    ApprovalRequest,
    CreateCaseRequest,
    ExecutionRequest,
    RecommendationRequest,
    ReconciliationResolutionRequest,
    RegisterDocumentRequest,
)
from .security import RequestContext
from .store import Store


class BackofficeService:
    def __init__(self, store: Store, policy: PolicyClient, service_name: str = "intelligent-backoffice-vertical-slice"):
        self.store, self.policy = store, policy
        self.tracer = trace.get_tracer(service_name)

    @staticmethod
    def resource(case):
        return {"id": case["case_id"], "tenant_id": case["tenant_id"], "state": case["state"]}

    def load(self, conn, case_id, tenant_id):
        row = conn.execute("SELECT * FROM cases WHERE id=? AND tenant_id=?", (case_id, tenant_id)).fetchone()
        case = self.store.case(row)
        if not case:
            raise HTTPException(404, "Case not found")
        return case

    @staticmethod
    def version(case, expected):
        if case["version"] != expected:
            raise HTTPException(409, detail={"reason": "case-version-conflict", "currentVersion": case["version"]})

    @staticmethod
    def timeline(conn, case, event, ctx, payload=None):
        conn.execute(
            "INSERT INTO timeline(case_id,tenant_id,event_type,actor_id,correlation_id,payload_json) VALUES(?,?,?,?,?,?)",
            (case["case_id"], case["tenant_id"], event, ctx.subject_id, ctx.correlation_id, json.dumps(payload or {})),
        )

    def create_case(self, ctx: RequestContext, req: CreateCaseRequest):
        with operation_span(self.tracer, "backoffice.case.create", correlation_id=ctx.correlation_id):
            self.policy.authorize(ctx, "case.create", {"id": "new", "tenant_id": ctx.tenant_id, "state": "CREATED"})
            with self.store.connection() as conn:
                existing = conn.execute("SELECT * FROM cases WHERE tenant_id=? AND external_id=?", (ctx.tenant_id, req.external_id)).fetchone()
                if existing:
                    IDEMPOTENCY.labels("case.create", "replay").inc()
                    return self.store.case(existing)
                case_id = str(uuid4())
                conn.execute(
                    "INSERT INTO cases(id,tenant_id,external_id,dispute_type,amount_cents,state,version) VALUES(?,?,?,?,?,?,1)",
                    (case_id, ctx.tenant_id, req.external_id, req.dispute_type, req.amount_cents, "CREATED"),
                )
                case = self.load(conn, case_id, ctx.tenant_id)
                self.timeline(conn, case, "backoffice.case.created.v1", ctx)
                CASES_CREATED.inc()
                return case

    def get_case(self, ctx, case_id):
        with operation_span(self.tracer, "backoffice.case.read", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                self.policy.authorize(ctx, "case.read", self.resource(case))
                return case

    def register_document(self, ctx, case_id, expected, req: RegisterDocumentRequest):
        with operation_span(self.tracer, "backoffice.document.register", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                before = case["state"]
                self.version(case, expected)
                self.policy.authorize(ctx, "document.register", self.resource(case), {"case_version": case["version"]})
                classification = classify_document(req.filename, req.content_type)
                evidence = case["evidence_references"]
                reference = f"evidence:{req.document_id}:v1"
                if reference not in evidence:
                    evidence.append(reference)
                conn.execute(
                    "UPDATE cases SET evidence_json=?,state='DOCUMENTS_VALIDATED',version=version+1 WHERE id=?",
                    (json.dumps(evidence), case_id),
                )
                case = self.load(conn, case_id, ctx.tenant_id)
                self.timeline(
                    conn,
                    case,
                    "backoffice.document.validated.v1",
                    ctx,
                    {"documentId": req.document_id, "classification": classification, "mock": True},
                )
                record_transition("document.register", before, case["state"])
                return case

    def investigate(self, ctx, case_id, expected):
        with operation_span(self.tracer, "backoffice.investigation.execute", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                before = case["state"]
                self.version(case, expected)
                self.policy.authorize(
                    ctx,
                    "investigation.execute",
                    self.resource(case),
                    {"case_version": case["version"], "evidence_references": case["evidence_references"]},
                )
                finding = investigate_case(case["evidence_references"])
                conn.execute("UPDATE cases SET state='UNDER_INVESTIGATION',version=version+1 WHERE id=?", (case_id,))
                case = self.load(conn, case_id, ctx.tenant_id)
                self.timeline(conn, case, "backoffice.investigation.completed.v1", ctx, finding | {"mock": True})
                record_transition("investigation.execute", before, case["state"])
                return case

    def recommend(self, ctx, case_id, expected, req: RecommendationRequest):
        with operation_span(self.tracer, "backoffice.recommendation.create", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                before = case["state"]
                self.version(case, expected)
                self.policy.authorize(
                    ctx,
                    "recommendation.create",
                    self.resource(case),
                    {"case_version": case["version"], "evidence_references": req.evidence_references},
                )
                generated = propose_recommendation("transaction-confirmed", req.evidence_references)
                if generated["outcome"] != "ABSTAIN" and req.outcome != generated["outcome"]:
                    raise HTTPException(422, detail={"reason": "recommendation-conflicts-with-grounded-mock", "generated": generated})
                recommendation_version = (case["recommendation_version"] or 0) + 1
                conn.execute(
                    "UPDATE cases SET state='AWAITING_APPROVAL',version=version+1,recommendation_actor_id=?,recommendation_version=? WHERE id=?",
                    (ctx.subject_id, recommendation_version, case_id),
                )
                case = self.load(conn, case_id, ctx.tenant_id)
                self.timeline(
                    conn,
                    case,
                    "backoffice.decision.proposed.v1",
                    ctx,
                    {"outcome": req.outcome, "recommendationVersion": recommendation_version, "generated": generated},
                )
                record_transition("recommendation.create", before, case["state"])
                return case

    def approve(self, ctx, case_id, expected, req: ApprovalRequest):
        with operation_span(self.tracer, "backoffice.approval.decide", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                before = case["state"]
                self.version(case, expected)
                policy_context = {
                    "case_version": case["version"],
                    "recommendation_actor_id": case["recommendation_actor_id"],
                    "recommendation_version": case["recommendation_version"],
                    "approved_recommendation_version": case["recommendation_version"],
                    "authority_limit": req.authority_limit_cents,
                    "amount": case["amount_cents"],
                }
                self.policy.authorize(ctx, "approval.decide", self.resource(case), policy_context)
                state = "APPROVED" if req.decision == "APPROVED" else "REJECTED"
                conn.execute(
                    "UPDATE cases SET state=?,version=version+1,approval_status=?,approved_recommendation_version=recommendation_version WHERE id=?",
                    (state, req.decision, case_id),
                )
                case = self.load(conn, case_id, ctx.tenant_id)
                event = "backoffice.decision.approved.v1" if state == "APPROVED" else "backoffice.decision.rejected.v1"
                self.timeline(conn, case, event, ctx, {"reason": req.reason})
                record_transition("approval.decide", before, case["state"])
                return case

    def execute(self, ctx, case_id, key, req: ExecutionRequest):
        request_hash = hashlib.sha256(json.dumps({"case_id": case_id, **req.model_dump()}, sort_keys=True).encode()).hexdigest()
        with operation_span(self.tracer, "backoffice.execution.request", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                previous = conn.execute(
                    "SELECT * FROM idempotency WHERE key=? AND tenant_id=? AND action='execution.request'",
                    (key, ctx.tenant_id),
                ).fetchone()
                if previous:
                    if previous["request_hash"] != request_hash:
                        IDEMPOTENCY.labels("execution.request", "conflict").inc()
                        EXECUTIONS.labels("idempotency-conflict").inc()
                        raise HTTPException(409, "Idempotency key reused with different payload")
                    IDEMPOTENCY.labels("execution.request", "replay").inc()
                    EXECUTIONS.labels("replay").inc()
                    return json.loads(previous["response_json"])
                case = self.load(conn, case_id, ctx.tenant_id)
                before = case["state"]
                policy_context = {
                    "approval_status": case["approval_status"],
                    "approval_valid": True,
                    "recommendation_version": case["recommendation_version"],
                    "approved_recommendation_version": case["approved_recommendation_version"],
                    "idempotency_key": key,
                    "command_hash": request_hash,
                    "evidence_references": case["evidence_references"],
                }
                self.policy.authorize(ctx, "execution.request", self.resource(case), policy_context)
                execution_id = str(uuid4())
                state = "RECONCILIATION_REQUIRED" if req.result_mode == "AMBIGUOUS" else "EXECUTED"
                execution_status = "RECONCILIATION_REQUIRED" if req.result_mode == "AMBIGUOUS" else "SUCCEEDED"
                conn.execute("UPDATE cases SET state=?,version=version+1 WHERE id=?", (state, case_id))
                conn.execute(
                    "INSERT INTO executions(id,case_id,tenant_id,status,idempotency_key,request_hash,result_mode,completed_at) "
                    "VALUES(?,?,?,?,?,?,?,CASE WHEN ?='SUCCEEDED' THEN CURRENT_TIMESTAMP ELSE NULL END)",
                    (execution_id, case_id, ctx.tenant_id, execution_status, key, request_hash, req.result_mode, execution_status),
                )
                case = self.load(conn, case_id, ctx.tenant_id)
                case["execution_id"] = execution_id
                case["execution_status"] = execution_status
                event = "backoffice.execution.ambiguous.v1" if state == "RECONCILIATION_REQUIRED" else "backoffice.execution.completed.v1"
                self.timeline(conn, case, event, ctx, {"executionId": execution_id, "status": execution_status, "mock": True})
                conn.execute(
                    "INSERT INTO idempotency(key,tenant_id,action,request_hash,response_json) VALUES(?,?,?,?,?)",
                    (key, ctx.tenant_id, "execution.request", request_hash, json.dumps(case)),
                )
                result = "ambiguous" if state == "RECONCILIATION_REQUIRED" else "success"
                EXECUTIONS.labels(result).inc()
                IDEMPOTENCY.labels("execution.request", "stored").inc()
                if state == "RECONCILIATION_REQUIRED":
                    RECONCILIATIONS.inc()
                record_transition("execution.request", before, case["state"])
                return case

    def get_execution(self, ctx, case_id, execution_id):
        with operation_span(self.tracer, "backoffice.execution.read", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                self.policy.authorize(ctx, "execution.read", self.resource(case))
                row = conn.execute(
                    "SELECT * FROM executions WHERE id=? AND case_id=? AND tenant_id=?",
                    (execution_id, case_id, ctx.tenant_id),
                ).fetchone()
                execution = self.store.execution(row)
                if not execution:
                    raise HTTPException(404, "Execution not found")
                return execution

    def reconcile(self, ctx, case_id, execution_id, key, expected, req: ReconciliationResolutionRequest):
        request_hash = hashlib.sha256(
            json.dumps({"case_id": case_id, "execution_id": execution_id, **req.model_dump()}, sort_keys=True).encode()
        ).hexdigest()
        with operation_span(self.tracer, "backoffice.reconciliation.resolve", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                previous = conn.execute(
                    "SELECT * FROM idempotency WHERE key=? AND tenant_id=? AND action='reconciliation.resolve'",
                    (key, ctx.tenant_id),
                ).fetchone()
                if previous:
                    if previous["request_hash"] != request_hash:
                        IDEMPOTENCY.labels("reconciliation.resolve", "conflict").inc()
                        raise HTTPException(409, "Idempotency key reused with different payload")
                    IDEMPOTENCY.labels("reconciliation.resolve", "replay").inc()
                    return json.loads(previous["response_json"])

                case = self.load(conn, case_id, ctx.tenant_id)
                before = case["state"]
                self.version(case, expected)
                execution_row = conn.execute(
                    "SELECT * FROM executions WHERE id=? AND case_id=? AND tenant_id=?",
                    (execution_id, case_id, ctx.tenant_id),
                ).fetchone()
                execution = self.store.execution(execution_row)
                if not execution:
                    raise HTTPException(404, "Execution not found")
                if execution["status"] != "RECONCILIATION_REQUIRED":
                    raise HTTPException(409, detail={"reason": "execution-not-awaiting-reconciliation", "status": execution["status"]})

                self.policy.authorize(
                    ctx,
                    "reconciliation.resolve",
                    self.resource(case),
                    {"case_version": case["version"]},
                )

                outcomes = {
                    "CONFIRMED_SUCCEEDED": ("EXECUTED", "RECONCILED", "backoffice.reconciliation.succeeded.v1"),
                    "CONFIRMED_FAILED": ("FAILED", "RECONCILED", "backoffice.reconciliation.failed.v1"),
                    "ESCALATED": ("RECONCILIATION_REQUIRED", "RECONCILIATION_REQUIRED", "backoffice.reconciliation.escalated.v1"),
                }
                state, execution_status, event = outcomes[req.resolution]
                conn.execute("UPDATE cases SET state=?,version=version+1 WHERE id=?", (state, case_id))
                conn.execute(
                    "UPDATE executions SET status=?,resolution=?,external_reference=?,"
                    "completed_at=CASE WHEN ?='RECONCILED' THEN CURRENT_TIMESTAMP ELSE completed_at END WHERE id=?",
                    (execution_status, req.resolution, f"reconciliation:{req.resolution.lower()}", execution_status, execution_id),
                )
                case = self.load(conn, case_id, ctx.tenant_id)
                case["execution_id"] = execution_id
                case["execution_status"] = execution_status
                case["reconciliation_resolution"] = req.resolution
                self.timeline(
                    conn,
                    case,
                    event,
                    ctx,
                    {"executionId": execution_id, "resolution": req.resolution, "reason": req.reason},
                )
                conn.execute(
                    "INSERT INTO idempotency(key,tenant_id,action,request_hash,response_json) VALUES(?,?,?,?,?)",
                    (key, ctx.tenant_id, "reconciliation.resolve", request_hash, json.dumps(case)),
                )
                IDEMPOTENCY.labels("reconciliation.resolve", "stored").inc()
                record_transition("reconciliation.resolve", before, case["state"])
                return case

    def get_timeline(self, ctx, case_id):
        with operation_span(self.tracer, "backoffice.timeline.read", correlation_id=ctx.correlation_id):
            with self.store.connection() as conn:
                case = self.load(conn, case_id, ctx.tenant_id)
                self.policy.authorize(ctx, "case.read", self.resource(case))
                rows = conn.execute("SELECT * FROM timeline WHERE case_id=? ORDER BY id", (case_id,)).fetchall()
                return [
                    {
                        "eventType": row["event_type"],
                        "actorId": row["actor_id"],
                        "correlationId": row["correlation_id"],
                        "occurredAt": row["occurred_at"],
                        "payload": json.loads(row["payload_json"]),
                    }
                    for row in rows
                ]
