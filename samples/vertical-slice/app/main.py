from fastapi import Depends, FastAPI, Header

from .config import Settings
from .eventing_metrics import refresh_eventing_metrics
from .observability import install_http_observability, metrics_response
from .operations import create_operations_router
from .policy import PolicyClient
from .schemas import ApprovalRequest, CreateCaseRequest, ExecutionRequest, RecommendationRequest, RegisterDocumentRequest
from .security import RequestContext, request_context
from .service import BackofficeService
from .store import Store


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    store = Store(settings.database_path, eventing_enabled=settings.eventing_enabled)
    policy = PolicyClient(settings)
    service = BackofficeService(store, policy, settings.service_name)
    app = FastAPI(title="Intelligent Backoffice Vertical Slice", version="0.3.0")
    app.state.store = store
    app.state.policy = policy
    install_http_observability(app, settings)
    app.include_router(create_operations_router(store, policy))

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "policyMode": settings.policy_mode,
            "metricsEnabled": settings.metrics_enabled,
            "tracingEnabled": settings.tracing_enabled,
            "eventingEnabled": settings.eventing_enabled,
        }

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        refresh_eventing_metrics(store)
        return metrics_response()

    @app.post("/v1/cases")
    def create_case(req: CreateCaseRequest, ctx: RequestContext = Depends(request_context)):
        return service.create_case(ctx, req)

    @app.get("/v1/cases/{case_id}")
    def get_case(case_id: str, ctx: RequestContext = Depends(request_context)):
        return service.get_case(ctx, case_id)

    @app.post("/v1/cases/{case_id}/documents")
    def document(case_id: str, req: RegisterDocumentRequest, if_match: int = Header(..., alias="If-Match"), ctx: RequestContext = Depends(request_context)):
        return service.register_document(ctx, case_id, if_match, req)

    @app.post("/v1/cases/{case_id}/investigations")
    def investigate(case_id: str, if_match: int = Header(..., alias="If-Match"), ctx: RequestContext = Depends(request_context)):
        return service.investigate(ctx, case_id, if_match)

    @app.post("/v1/cases/{case_id}/recommendations")
    def recommend(case_id: str, req: RecommendationRequest, if_match: int = Header(..., alias="If-Match"), ctx: RequestContext = Depends(request_context)):
        return service.recommend(ctx, case_id, if_match, req)

    @app.post("/v1/cases/{case_id}/approvals")
    def approve(case_id: str, req: ApprovalRequest, if_match: int = Header(..., alias="If-Match"), ctx: RequestContext = Depends(request_context)):
        return service.approve(ctx, case_id, if_match, req)

    @app.post("/v1/cases/{case_id}/executions")
    def execute(case_id: str, req: ExecutionRequest, idempotency_key: str = Header(..., alias="Idempotency-Key"), ctx: RequestContext = Depends(request_context)):
        return service.execute(ctx, case_id, idempotency_key, req)

    @app.get("/v1/cases/{case_id}/timeline")
    def timeline(case_id: str, ctx: RequestContext = Depends(request_context)):
        return service.get_timeline(ctx, case_id)

    return app


app = create_app()
