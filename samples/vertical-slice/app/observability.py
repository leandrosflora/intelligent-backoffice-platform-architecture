from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from .config import Settings

LOGGER = logging.getLogger(__name__)

HTTP_REQUESTS = Counter(
    "backoffice_http_requests_total",
    "HTTP requests handled by the vertical slice.",
    ("method", "route", "status"),
)
HTTP_DURATION = Histogram(
    "backoffice_http_request_duration_seconds",
    "HTTP request latency by route.",
    ("method", "route"),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
POLICY_DECISIONS = Counter(
    "backoffice_policy_decisions_total",
    "Policy decisions by action and result.",
    ("action", "decision"),
)
POLICY_DURATION = Histogram(
    "backoffice_policy_decision_duration_seconds",
    "Policy decision latency by action.",
    ("action",),
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 3),
)
WORKFLOW_TRANSITIONS = Counter(
    "backoffice_workflow_transitions_total",
    "Workflow transitions by source and target state.",
    ("operation", "from_state", "to_state"),
)
CASES_CREATED = Counter(
    "backoffice_cases_created_total",
    "Cases created by the runtime.",
)
EXECUTIONS = Counter(
    "backoffice_executions_total",
    "Execution attempts by result.",
    ("result",),
)
RECONCILIATIONS = Counter(
    "backoffice_reconciliations_total",
    "Cases routed to reconciliation.",
)
IDEMPOTENCY = Counter(
    "backoffice_idempotency_total",
    "Idempotency outcomes by action.",
    ("action", "result"),
)
INTELLIGENCE_OUTCOMES = Counter(
    "backoffice_intelligence_outcomes_total",
    "Deterministic intelligence outcomes used by the baseline.",
    ("capability", "outcome"),
)

_TRACE_LOCK = Lock()
_TRACE_CONFIGURED = False


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def configure_tracing(settings: Settings):
    global _TRACE_CONFIGURED
    from opentelemetry import trace

    if not settings.tracing_enabled:
        return trace.get_tracer(settings.service_name)

    with _TRACE_LOCK:
        if not _TRACE_CONFIGURED:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                from opentelemetry.sdk.resources import Resource
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import BatchSpanProcessor

                provider = TracerProvider(
                    resource=Resource.create(
                        {
                            "service.name": settings.service_name,
                            "deployment.environment.name": settings.environment,
                        }
                    )
                )
                exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, insecure=True)
                provider.add_span_processor(BatchSpanProcessor(exporter))
                trace.set_tracer_provider(provider)
                _TRACE_CONFIGURED = True
            except Exception:  # pragma: no cover - defensive startup path
                LOGGER.exception("OpenTelemetry exporter could not be configured; tracing is disabled.")
    return trace.get_tracer(settings.service_name)


def install_http_observability(app, settings: Settings) -> None:
    tracer = configure_tracing(settings)

    @app.middleware("http")
    async def observe_request(request, call_next):
        started = time.perf_counter()
        correlation_id = request.headers.get("X-Correlation-Id", "")
        with tracer.start_as_current_span(f"HTTP {request.method}") as span:
            span.set_attribute("http.request.method", request.method)
            span.set_attribute("backoffice.correlation_id", correlation_id)
            try:
                response = await call_next(request)
            except Exception:
                route = _route_name(request)
                HTTP_REQUESTS.labels(request.method, route, "500").inc()
                HTTP_DURATION.labels(request.method, route).observe(time.perf_counter() - started)
                span.set_attribute("http.response.status_code", 500)
                raise
            route = _route_name(request)
            status = str(response.status_code)
            HTTP_REQUESTS.labels(request.method, route, status).inc()
            HTTP_DURATION.labels(request.method, route).observe(time.perf_counter() - started)
            span.update_name(f"{request.method} {route}")
            span.set_attribute("http.route", route)
            span.set_attribute("http.response.status_code", response.status_code)
            return response


def _route_name(request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


@contextmanager
def operation_span(tracer, name: str, **attributes) -> Iterator[None]:
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, value)
        yield


def record_transition(operation: str, before: str, after: str) -> None:
    WORKFLOW_TRANSITIONS.labels(operation, before, after).inc()
