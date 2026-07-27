import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
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
"""

class Store:
    def __init__(self, database_path: str):
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = str(path)
        with self.connection() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
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
