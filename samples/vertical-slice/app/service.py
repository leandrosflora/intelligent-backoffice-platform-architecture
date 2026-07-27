import hashlib
import json
from uuid import uuid4
from fastapi import HTTPException
from .policy import PolicyClient
from .schemas import ApprovalRequest, CreateCaseRequest, ExecutionRequest, RecommendationRequest, RegisterDocumentRequest
from .security import RequestContext
from .store import Store

class BackofficeService:
    def __init__(self, store: Store, policy: PolicyClient):
        self.store, self.policy = store, policy

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
        self.policy.authorize(ctx, "case.create", {"id": "new", "tenant_id": ctx.tenant_id, "state": "CREATED"})
        with self.store.connection() as conn:
            existing = conn.execute("SELECT * FROM cases WHERE tenant_id=? AND external_id=?", (ctx.tenant_id, req.external_id)).fetchone()
            if existing:
                return self.store.case(existing)
            case_id = str(uuid4())
            conn.execute(
                "INSERT INTO cases(id,tenant_id,external_id,dispute_type,amount_cents,state,version) VALUES(?,?,?,?,?,?,1)",
                (case_id, ctx.tenant_id, req.external_id, req.dispute_type, req.amount_cents, "CREATED"),
            )
            case = self.load(conn, case_id, ctx.tenant_id)
            self.timeline(conn, case, "backoffice.case.created.v1", ctx)
            return case

    def get_case(self, ctx, case_id):
        with self.store.connection() as conn:
            case = self.load(conn, case_id, ctx.tenant_id)
            self.policy.authorize(ctx, "case.read", self.resource(case))
            return case

    def register_document(self, ctx, case_id, expected, req: RegisterDocumentRequest):
        with self.store.connection() as conn:
            case = self.load(conn, case_id, ctx.tenant_id)
            self.version(case, expected)
            self.policy.authorize(ctx, "document.register", self.resource(case), {"case_version": case["version"]})
            evidence = case["evidence_references"]
            reference = f"evidence:{req.document_id}:v1"
            if reference not in evidence:
                evidence.append(reference)
            conn.execute(
                "UPDATE cases SET evidence_json=?,state='DOCUMENTS_VALIDATED',version=version+1 WHERE id=?",
                (json.dumps(evidence), case_id),
            )
            case = self.load(conn, case_id, ctx.tenant_id)
            self.timeline(conn, case, "backoffice.document.validated.v1", ctx, {"documentId": req.document_id, "mock": True})
            return case

    def investigate(self, ctx, case_id, expected):
        with self.store.connection() as conn:
            case = self.load(conn, case_id, ctx.tenant_id)
            self.version(case, expected)
            self.policy.authorize(
                ctx,
                "investigation.execute",
                self.resource(case),
                {"case_version": case["version"], "evidence_references": case["evidence_references"]},
            )
            conn.execute("UPDATE cases SET state='UNDER_INVESTIGATION',version=version+1 WHERE id=?", (case_id,))
            case = self.load(conn, case_id, ctx.tenant_id)
            self.timeline(conn, case, "backoffice.investigation.completed.v1", ctx, {"finding": "transaction-confirmed", "mock": True})
            return case

    def recommend(self, ctx, case_id, expected, req: RecommendationRequest):
        with self.store.connection() as conn:
            case = self.load(conn, case_id, ctx.tenant_id)
            self.version(case, expected)
            self.policy.authorize(
                ctx,
                "recommendation.create",
                self.resource(case),
                {"case_version": case["version"], "evidence_references": req.evidence_references},
            )
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
                {"outcome": req.outcome, "recommendationVersion": recommendation_version},
            )
            return case

    def approve(self, ctx, case_id, expected, req: ApprovalRequest):
        with self.store.connection() as conn:
            case = self.load(conn, case_id, ctx.tenant_id)
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
            return case

    def execute(self, ctx, case_id, key, req: ExecutionRequest):
        request_hash = hashlib.sha256(json.dumps(req.model_dump(), sort_keys=True).encode()).hexdigest()
        with self.store.connection() as conn:
            previous = conn.execute(
                "SELECT * FROM idempotency WHERE key=? AND tenant_id=? AND action='execution.request'",
                (key, ctx.tenant_id),
            ).fetchone()
            if previous:
                if previous["request_hash"] != request_hash:
                    raise HTTPException(409, "Idempotency key reused with different payload")
                return json.loads(previous["response_json"])
            case = self.load(conn, case_id, ctx.tenant_id)
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
            state = "RECONCILIATION_REQUIRED" if req.result_mode == "AMBIGUOUS" else "EXECUTED"
            conn.execute("UPDATE cases SET state=?,version=version+1 WHERE id=?", (state, case_id))
            case = self.load(conn, case_id, ctx.tenant_id)
            event = "backoffice.execution.ambiguous.v1" if state == "RECONCILIATION_REQUIRED" else "backoffice.execution.completed.v1"
            self.timeline(conn, case, event, ctx, {"mock": True})
            conn.execute(
                "INSERT INTO idempotency(key,tenant_id,action,request_hash,response_json) VALUES(?,?,?,?,?)",
                (key, ctx.tenant_id, "execution.request", request_hash, json.dumps(case)),
            )
            return case

    def get_timeline(self, ctx, case_id):
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
