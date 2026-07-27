import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = r'''
CREATE TABLE IF NOT EXISTS cases (
  id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, external_id TEXT NOT NULL,
  dispute_type TEXT NOT NULL, amount_cents INTEGER NOT NULL, state TEXT NOT NULL,
  version INTEGER NOT NULL, evidence_json TEXT NOT NULL DEFAULT '[]',
  recommendation_actor_id TEXT, recommendation_version INTEGER,
  approved_recommendation_version INTEGER, approval_status TEXT,
  UNIQUE(tenant_id, external_id)
);
CREATE TABLE IF NOT EXISTS timeline (
  id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, tenant_id TEXT NOT NULL,
  event_type TEXT NOT NULL, actor_id TEXT NOT NULL, correlation_id TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}', occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS idempotency (
  key TEXT NOT NULL, tenant_id TEXT NOT NULL, action TEXT NOT NULL,
  request_hash TEXT NOT NULL, response_json TEXT NOT NULL,
  PRIMARY KEY(key, tenant_id, action)
);
CREATE TABLE IF NOT EXISTS runtime_settings (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  aggregate_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  topic TEXT NOT NULL,
  message_key TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'PENDING',
  attempts INTEGER NOT NULL DEFAULT 0,
  available_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  locked_at TEXT,
  published_at TEXT,
  last_error TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_outbox_dispatch ON outbox(status, available_at, id);
CREATE TABLE IF NOT EXISTS inbox (
  consumer_name TEXT NOT NULL,
  event_id TEXT NOT NULL,
  processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  result_json TEXT NOT NULL DEFAULT '{}',
  PRIMARY KEY(consumer_name, event_id)
);
CREATE TABLE IF NOT EXISTS event_projection (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  consumer_name TEXT NOT NULL,
  event_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  replay_count INTEGER NOT NULL DEFAULT 0,
  processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(consumer_name, event_id)
);
CREATE TABLE IF NOT EXISTS timers (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  timer_type TEXT NOT NULL,
  due_at TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'SCHEDULED',
  attempts INTEGER NOT NULL DEFAULT 0,
  locked_at TEXT,
  fired_at TEXT,
  last_error TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_timers_due ON timers(status, due_at);
CREATE TABLE IF NOT EXISTS dead_letters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  source_topic TEXT NOT NULL,
  event_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  envelope_json TEXT NOT NULL,
  error TEXT NOT NULL,
  attempts INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'OPEN',
  failed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  replayed_at TEXT,
  replay_event_id TEXT,
  replay_reason TEXT
);
CREATE INDEX IF NOT EXISTS ix_dead_letters_status ON dead_letters(status, failed_at);
CREATE TABLE IF NOT EXISTS replay_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dead_letter_id INTEGER NOT NULL,
  original_event_id TEXT NOT NULL,
  replay_event_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER IF NOT EXISTS timeline_to_outbox
AFTER INSERT ON timeline
WHEN COALESCE((SELECT value FROM runtime_settings WHERE key='eventing_enabled'), 'false') = 'true'
BEGIN
  INSERT INTO outbox(
    event_id, aggregate_id, tenant_id, event_type, topic, message_key,
    correlation_id, payload_json, metadata_json
  ) VALUES (
    lower(hex(randomblob(16))), NEW.case_id, NEW.tenant_id, NEW.event_type,
    'backoffice.events.v1', NEW.case_id, NEW.correlation_id,
    NEW.payload_json, json_object('actorId', NEW.actor_id, 'timelineId', NEW.id)
  );
END;
'''


class Store:
    def __init__(self, database_path: str, eventing_enabled: bool = False):
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = str(path)
        with self.connection() as conn:
            conn.executescript(SCHEMA)
            conn.execute(
                "INSERT INTO runtime_settings(key,value) VALUES('eventing_enabled',?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                ("true" if eventing_enabled else "false",),
            )

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.database_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def case(row):
        if not row:
            return None
        data = dict(row)
        data["evidence_references"] = json.loads(data.pop("evidence_json"))
        data["case_id"] = data.pop("id")
        return data
