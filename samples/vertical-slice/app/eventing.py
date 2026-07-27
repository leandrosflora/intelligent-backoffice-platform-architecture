from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .store import Store

TERMINAL_STATES = {"EXECUTED", "CLOSED", "REJECTED", "CANCELLED", "EXPIRED", "FAILED"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat().replace("+00:00", "Z")


def build_envelope(row) -> dict:
    metadata = json.loads(row["metadata_json"] or "{}")
    return {
        "eventId": row["event_id"],
        "eventType": row["event_type"],
        "eventVersion": 1,
        "occurredAt": metadata.get("occurredAt", row["created_at"]),
        "tenantId": row["tenant_id"],
        "caseId": row["aggregate_id"],
        "correlationId": row["correlation_id"],
        "causationId": metadata.get("causationId", row["correlation_id"]),
        "producer": metadata.get("producer", "intelligent-backoffice-vertical-slice"),
        "dataClassification": "INTERNAL",
        "replayCount": int(metadata.get("replayCount", 0)),
        "replayOf": metadata.get("replayOf"),
        "payload": json.loads(row["payload_json"] or "{}"),
    }


def claim_outbox(store: Store, limit: int = 20) -> list[dict]:
    with store.connection() as conn:
        conn.execute(
            "UPDATE outbox SET status='RETRY', locked_at=NULL "
            "WHERE status='IN_FLIGHT' AND locked_at < datetime('now','-2 minutes')"
        )
        rows = conn.execute(
            "SELECT * FROM outbox WHERE status IN ('PENDING','RETRY') "
            "AND available_at <= CURRENT_TIMESTAMP ORDER BY id LIMIT ?",
            (limit,),
        ).fetchall()
        result = []
        for row in rows:
            updated = conn.execute(
                "UPDATE outbox SET status='IN_FLIGHT', locked_at=CURRENT_TIMESTAMP "
                "WHERE id=? AND status IN ('PENDING','RETRY')",
                (row["id"],),
            ).rowcount
            if updated:
                result.append(dict(row))
        return result


def mark_outbox_published(store: Store, outbox_id: int) -> None:
    with store.connection() as conn:
        conn.execute(
            "UPDATE outbox SET status='PUBLISHED', published_at=CURRENT_TIMESTAMP, "
            "locked_at=NULL, last_error=NULL WHERE id=?",
            (outbox_id,),
        )


def fail_outbox(store: Store, row: dict, error: str, max_attempts: int) -> str:
    attempts = int(row["attempts"]) + 1
    envelope = build_envelope(row)
    with store.connection() as conn:
        if attempts >= max_attempts:
            conn.execute(
                "INSERT INTO dead_letters(source,source_topic,event_id,tenant_id,aggregate_id,event_type,envelope_json,error,attempts) "
                "VALUES('outbox',?,?,?,?,?,?,?,?)",
                (
                    row["topic"], row["event_id"], row["tenant_id"], row["aggregate_id"],
                    row["event_type"], json.dumps(envelope), error[:2000], attempts,
                ),
            )
            conn.execute(
                "UPDATE outbox SET status='DEAD_LETTER', attempts=?, last_error=?, locked_at=NULL WHERE id=?",
                (attempts, error[:2000], row["id"]),
            )
            return "DEAD_LETTER"
        delay = min(60, 2 ** attempts)
        conn.execute(
            "UPDATE outbox SET status='RETRY', attempts=?, last_error=?, locked_at=NULL, "
            "available_at=datetime('now', ?) WHERE id=?",
            (attempts, error[:2000], f"+{delay} seconds", row["id"]),
        )
        return "RETRY"


def schedule_timer(store: Store, tenant_id: str, aggregate_id: str, timer_type: str, delay_seconds: int, payload: dict) -> dict:
    timer_id = str(uuid4())
    due_at = utc_now() + timedelta(seconds=delay_seconds)
    with store.connection() as conn:
        conn.execute(
            "INSERT INTO timers(id,tenant_id,aggregate_id,timer_type,due_at,payload_json) VALUES(?,?,?,?,?,?)",
            (timer_id, tenant_id, aggregate_id, timer_type, iso(due_at), json.dumps(payload)),
        )
        row = conn.execute("SELECT * FROM timers WHERE id=?", (timer_id,)).fetchone()
        return _timer(row)


def claim_due_timers(store: Store, limit: int = 20) -> list[dict]:
    with store.connection() as conn:
        conn.execute(
            "UPDATE timers SET status='SCHEDULED', locked_at=NULL "
            "WHERE status='IN_FLIGHT' AND locked_at < datetime('now','-2 minutes')"
        )
        rows = conn.execute(
            "SELECT * FROM timers WHERE status IN ('SCHEDULED','RETRY') "
            "AND due_at <= ? ORDER BY due_at LIMIT ?",
            (iso(), limit),
        ).fetchall()
        claimed = []
        for row in rows:
            if conn.execute(
                "UPDATE timers SET status='IN_FLIGHT', locked_at=CURRENT_TIMESTAMP "
                "WHERE id=? AND status IN ('SCHEDULED','RETRY')", (row["id"],)
            ).rowcount:
                claimed.append(dict(row))
        return claimed


def fire_timer(store: Store, timer: dict) -> None:
    payload = json.loads(timer["payload_json"] or "{}")
    timeline_payload = {
        "timerId": timer["id"],
        "timerType": timer["timer_type"],
        "payload": payload,
    }
    with store.connection() as conn:
        conn.execute(
            "INSERT INTO timeline(case_id,tenant_id,event_type,actor_id,correlation_id,payload_json) "
            "VALUES(?,?,?,?,?,?)",
            (
                timer["aggregate_id"], timer["tenant_id"], "backoffice.timer.fired.v1",
                "timer-worker", f"timer:{timer['id']}", json.dumps(timeline_payload),
            ),
        )
        conn.execute(
            "UPDATE timers SET status='FIRED', fired_at=CURRENT_TIMESTAMP, locked_at=NULL, last_error=NULL WHERE id=?",
            (timer["id"],),
        )


def fail_timer(store: Store, timer: dict, error: str, max_attempts: int) -> str:
    attempts = int(timer["attempts"]) + 1
    with store.connection() as conn:
        if attempts >= max_attempts:
            envelope = {
                "eventId": str(uuid4()),
                "eventType": "backoffice.timer.failed.v1",
                "eventVersion": 1,
                "occurredAt": iso(),
                "tenantId": timer["tenant_id"],
                "caseId": timer["aggregate_id"],
                "correlationId": f"timer:{timer['id']}",
                "producer": "timer-worker",
                "dataClassification": "INTERNAL",
                "replayCount": 0,
                "payload": {"timerId": timer["id"], "timerType": timer["timer_type"]},
            }
            conn.execute(
                "INSERT INTO dead_letters(source,source_topic,event_id,tenant_id,aggregate_id,event_type,envelope_json,error,attempts) "
                "VALUES('timer','backoffice.events.v1',?,?,?,?,?,?,?)",
                (
                    envelope["eventId"], timer["tenant_id"], timer["aggregate_id"], envelope["eventType"],
                    json.dumps(envelope), error[:2000], attempts,
                ),
            )
            conn.execute(
                "UPDATE timers SET status='DEAD_LETTER', attempts=?, last_error=?, locked_at=NULL WHERE id=?",
                (attempts, error[:2000], timer["id"]),
            )
            return "DEAD_LETTER"
        delay = min(60, 2 ** attempts)
        conn.execute(
            "UPDATE timers SET status='RETRY', attempts=?, last_error=?, locked_at=NULL, "
            "due_at=? WHERE id=?",
            (attempts, error[:2000], iso(utc_now() + timedelta(seconds=delay)), timer["id"]),
        )
        return "RETRY"


def process_envelope(store: Store, consumer_name: str, envelope: dict) -> str:
    event_id = envelope["eventId"]
    with store.connection() as conn:
        if conn.execute(
            "SELECT 1 FROM inbox WHERE consumer_name=? AND event_id=?",
            (consumer_name, event_id),
        ).fetchone():
            return "DUPLICATE"

        payload = envelope.get("payload") or {}
        timer_payload = payload.get("payload") or {}
        if timer_payload.get("simulateFailureOnce") and int(envelope.get("replayCount", 0)) < 1:
            raise RuntimeError("simulated one-time consumer failure")

        if envelope["eventType"] == "backoffice.timer.fired.v1" and payload.get("timerType") == "CASE_EXPIRY":
            case = conn.execute(
                "SELECT * FROM cases WHERE id=? AND tenant_id=?",
                (envelope["caseId"], envelope["tenantId"]),
            ).fetchone()
            if case and case["state"] not in TERMINAL_STATES:
                before = case["state"]
                conn.execute("UPDATE cases SET state='EXPIRED',version=version+1 WHERE id=?", (case["id"],))
                conn.execute(
                    "INSERT INTO timeline(case_id,tenant_id,event_type,actor_id,correlation_id,payload_json) "
                    "VALUES(?,?,?,?,?,?)",
                    (
                        case["id"], case["tenant_id"], "backoffice.case.expired.v1",
                        consumer_name, envelope["correlationId"], json.dumps({"fromState": before, "timerId": payload.get("timerId")}),
                    ),
                )

        conn.execute(
            "INSERT INTO event_projection(consumer_name,event_id,tenant_id,aggregate_id,event_type,replay_count) "
            "VALUES(?,?,?,?,?,?)",
            (
                consumer_name, event_id, envelope["tenantId"], envelope["caseId"],
                envelope["eventType"], int(envelope.get("replayCount", 0)),
            ),
        )
        conn.execute(
            "INSERT INTO inbox(consumer_name,event_id,result_json) VALUES(?,?,?)",
            (consumer_name, event_id, json.dumps({"status": "PROCESSED"})),
        )
    return "PROCESSED"


def record_consumer_dead_letter(store: Store, source_topic: str, envelope: dict, error: str, attempts: int) -> int:
    with store.connection() as conn:
        cursor = conn.execute(
            "INSERT INTO dead_letters(source,source_topic,event_id,tenant_id,aggregate_id,event_type,envelope_json,error,attempts) "
            "VALUES('consumer',?,?,?,?,?,?,?,?)",
            (
                source_topic, envelope["eventId"], envelope["tenantId"], envelope["caseId"],
                envelope["eventType"], json.dumps(envelope), error[:2000], attempts,
            ),
        )
        return int(cursor.lastrowid)


def replay_dead_letter(store: Store, dead_letter_id: int, actor_id: str, reason: str, correlation_id: str) -> dict:
    with store.connection() as conn:
        row = conn.execute("SELECT * FROM dead_letters WHERE id=?", (dead_letter_id,)).fetchone()
        if not row:
            raise KeyError("dead-letter-not-found")
        if row["status"] != "OPEN":
            raise ValueError("dead-letter-already-replayed")
        original = json.loads(row["envelope_json"])
        replay_event_id = str(uuid4())
        metadata = {
            "replayOf": original["eventId"],
            "replayCount": int(original.get("replayCount", 0)) + 1,
            "causationId": original.get("eventId"),
            "producer": "controlled-replay-api",
            "occurredAt": iso(),
        }
        conn.execute(
            "INSERT INTO outbox(event_id,aggregate_id,tenant_id,event_type,topic,message_key,correlation_id,payload_json,metadata_json) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                replay_event_id, original["caseId"], original["tenantId"], original["eventType"],
                row["source_topic"], original["caseId"], correlation_id,
                json.dumps(original.get("payload") or {}), json.dumps(metadata),
            ),
        )
        conn.execute(
            "UPDATE dead_letters SET status='REPLAYED', replayed_at=CURRENT_TIMESTAMP, replay_event_id=?, replay_reason=? WHERE id=?",
            (replay_event_id, reason, dead_letter_id),
        )
        conn.execute(
            "INSERT INTO replay_audit(dead_letter_id,original_event_id,replay_event_id,tenant_id,actor_id,reason,correlation_id) "
            "VALUES(?,?,?,?,?,?,?)",
            (dead_letter_id, original["eventId"], replay_event_id, original["tenantId"], actor_id, reason, correlation_id),
        )
        return {"deadLetterId": dead_letter_id, "replayEventId": replay_event_id, "status": "REPLAYED"}


def list_rows(store: Store, table: str, tenant_id: str, limit: int = 100) -> list[dict]:
    allowed = {"outbox", "dead_letters", "timers", "event_projection", "replay_audit"}
    if table not in allowed:
        raise ValueError("unsupported-table")
    with store.connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM {table} WHERE tenant_id=? ORDER BY id DESC LIMIT ?",  # noqa: S608 - allowlist above
            (tenant_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def eventing_counts(store: Store) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {"outbox": {}, "timers": {}, "deadLetters": {}, "inbox": {}}
    with store.connection() as conn:
        for row in conn.execute("SELECT status,COUNT(*) count FROM outbox GROUP BY status"):
            result["outbox"][row["status"]] = row["count"]
        for row in conn.execute("SELECT status,COUNT(*) count FROM timers GROUP BY status"):
            result["timers"][row["status"]] = row["count"]
        for row in conn.execute("SELECT status,COUNT(*) count FROM dead_letters GROUP BY status"):
            result["deadLetters"][row["status"]] = row["count"]
        result["inbox"]["PROCESSED"] = conn.execute("SELECT COUNT(*) count FROM inbox").fetchone()["count"]
    return result


def _timer(row) -> dict:
    data = dict(row)
    data["payload"] = json.loads(data.pop("payload_json") or "{}")
    return data


def wait_until(predicate, timeout_seconds: float = 20.0, interval_seconds: float = 0.1):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(interval_seconds)
    raise TimeoutError("condition not reached before timeout")
