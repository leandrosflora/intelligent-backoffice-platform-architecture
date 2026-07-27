from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .eventing import list_rows, replay_dead_letter, schedule_timer
from .policy import PolicyClient
from .security import RequestContext, request_context
from .store import Store


class TimerScheduleRequest(BaseModel):
    timer_type: str = Field(min_length=3, max_length=64)
    delay_seconds: int = Field(ge=0, le=86400)
    payload: dict = Field(default_factory=dict)


class ReplayRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=500)


def create_operations_router(store: Store, policy: PolicyClient) -> APIRouter:
    router = APIRouter(prefix="/v1/operations", tags=["operations"])

    @router.post("/cases/{case_id}/timers")
    def create_timer(case_id: str, req: TimerScheduleRequest, ctx: RequestContext = Depends(request_context)):
        with store.connection() as conn:
            row = conn.execute("SELECT * FROM cases WHERE id=? AND tenant_id=?", (case_id, ctx.tenant_id)).fetchone()
            if not row:
                raise HTTPException(404, "Case not found")
            resource = {"id": case_id, "tenant_id": ctx.tenant_id, "state": row["state"]}
        policy.authorize(
            ctx,
            "timer.schedule",
            resource,
            {"timer_type": req.timer_type, "delay_seconds": req.delay_seconds},
        )
        return schedule_timer(store, ctx.tenant_id, case_id, req.timer_type, req.delay_seconds, req.payload)

    @router.get("/outbox")
    def outbox(limit: int = Query(100, ge=1, le=500), ctx: RequestContext = Depends(request_context)):
        policy.authorize(ctx, "event.read", {"id": "outbox", "tenant_id": ctx.tenant_id, "state": "OPERATIONAL"})
        return list_rows(store, "outbox", ctx.tenant_id, limit)

    @router.get("/dead-letters")
    def dead_letters(limit: int = Query(100, ge=1, le=500), ctx: RequestContext = Depends(request_context)):
        policy.authorize(ctx, "event.read", {"id": "dead-letters", "tenant_id": ctx.tenant_id, "state": "OPERATIONAL"})
        return list_rows(store, "dead_letters", ctx.tenant_id, limit)

    @router.get("/timers")
    def timers(limit: int = Query(100, ge=1, le=500), ctx: RequestContext = Depends(request_context)):
        policy.authorize(ctx, "event.read", {"id": "timers", "tenant_id": ctx.tenant_id, "state": "OPERATIONAL"})
        return list_rows(store, "timers", ctx.tenant_id, limit)

    @router.get("/event-projections")
    def projections(limit: int = Query(100, ge=1, le=500), ctx: RequestContext = Depends(request_context)):
        policy.authorize(ctx, "event.read", {"id": "event-projections", "tenant_id": ctx.tenant_id, "state": "OPERATIONAL"})
        return list_rows(store, "event_projection", ctx.tenant_id, limit)

    @router.post("/dead-letters/{dead_letter_id}/replay")
    def replay(dead_letter_id: int, req: ReplayRequest, ctx: RequestContext = Depends(request_context)):
        with store.connection() as conn:
            row = conn.execute("SELECT * FROM dead_letters WHERE id=?", (dead_letter_id,)).fetchone()
            if not row or row["tenant_id"] != ctx.tenant_id:
                raise HTTPException(404, "Dead letter not found")
        policy.authorize(
            ctx,
            "event.replay",
            {"id": str(dead_letter_id), "tenant_id": ctx.tenant_id, "state": row["status"]},
            {"reason": req.reason, "source": "DEAD_LETTER"},
        )
        try:
            return replay_dead_letter(store, dead_letter_id, ctx.subject_id, req.reason, ctx.correlation_id)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    return router
