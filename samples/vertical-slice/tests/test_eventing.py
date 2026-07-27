import json

from app.eventing import (
    build_envelope,
    claim_due_timers,
    claim_outbox,
    fire_timer,
    process_envelope,
    record_consumer_dead_letter,
    replay_dead_letter,
    schedule_timer,
    utc_now,
)
from app.store import Store


def seed_case(store: Store, state="CREATED"):
    with store.connection() as conn:
        conn.execute(
            "INSERT INTO cases(id,tenant_id,external_id,dispute_type,amount_cents,state,version) VALUES(?,?,?,?,?,?,1)",
            ("case-1", "tenant-a", "external-1", "CARD_PURCHASE", 1000, state),
        )


def test_timeline_creates_transactional_outbox(tmp_path):
    store = Store(str(tmp_path / "db.sqlite"), eventing_enabled=True)
    seed_case(store)
    with store.connection() as conn:
        conn.execute(
            "INSERT INTO timeline(case_id,tenant_id,event_type,actor_id,correlation_id,payload_json) VALUES(?,?,?,?,?,?)",
            ("case-1", "tenant-a", "backoffice.case.created.v1", "user-1", "corr-1", json.dumps({"x": 1})),
        )
    rows = claim_outbox(store)
    assert len(rows) == 1
    envelope = build_envelope(rows[0])
    assert envelope["eventType"] == "backoffice.case.created.v1"
    assert envelope["payload"] == {"x": 1}
    assert envelope["tenantId"] == "tenant-a"


def test_disabled_eventing_does_not_create_outbox(tmp_path):
    store = Store(str(tmp_path / "db.sqlite"), eventing_enabled=False)
    seed_case(store)
    with store.connection() as conn:
        conn.execute(
            "INSERT INTO timeline(case_id,tenant_id,event_type,actor_id,correlation_id,payload_json) VALUES(?,?,?,?,?,?)",
            ("case-1", "tenant-a", "event", "actor", "corr", "{}"),
        )
    assert claim_outbox(store) == []


def test_timer_event_expires_case_and_inbox_is_idempotent(tmp_path):
    store = Store(str(tmp_path / "db.sqlite"), eventing_enabled=True)
    seed_case(store)
    timer = schedule_timer(store, "tenant-a", "case-1", "CASE_EXPIRY", 0, {})
    due = claim_due_timers(store)
    assert due[0]["id"] == timer["id"]
    fire_timer(store, due[0])
    row = claim_outbox(store)[0]
    envelope = build_envelope(row)
    assert process_envelope(store, "workflow-v1", envelope) == "PROCESSED"
    assert process_envelope(store, "workflow-v1", envelope) == "DUPLICATE"
    with store.connection() as conn:
        case = conn.execute("SELECT state FROM cases WHERE id='case-1'").fetchone()
        assert case["state"] == "EXPIRED"
        assert conn.execute("SELECT COUNT(*) count FROM inbox").fetchone()["count"] == 1


def test_dead_letter_controlled_replay_succeeds_once(tmp_path):
    store = Store(str(tmp_path / "db.sqlite"), eventing_enabled=True)
    seed_case(store)
    envelope = {
        "eventId": "original-event",
        "eventType": "backoffice.timer.fired.v1",
        "eventVersion": 1,
        "occurredAt": utc_now().isoformat(),
        "tenantId": "tenant-a",
        "caseId": "case-1",
        "correlationId": "corr-1",
        "producer": "timer-worker",
        "dataClassification": "INTERNAL",
        "replayCount": 0,
        "payload": {"timerType": "NOOP", "payload": {"simulateFailureOnce": True}},
    }
    try:
        process_envelope(store, "workflow-v1", envelope)
        raise AssertionError("expected simulated failure")
    except RuntimeError:
        pass
    dead_id = record_consumer_dead_letter(store, "backoffice.events.v1", envelope, "simulated", 3)
    result = replay_dead_letter(store, dead_id, "operator-1", "approved replay after investigation", "corr-replay")
    assert result["status"] == "REPLAYED"
    replay_row = claim_outbox(store)[0]
    replay_envelope = build_envelope(replay_row)
    assert replay_envelope["replayCount"] == 1
    assert replay_envelope["replayOf"] == "original-event"
    assert process_envelope(store, "workflow-v1", replay_envelope) == "PROCESSED"
