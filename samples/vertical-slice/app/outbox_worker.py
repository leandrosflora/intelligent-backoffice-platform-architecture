from __future__ import annotations

import json
import logging
import time

from kafka import KafkaProducer

from .config import Settings
from .eventing import build_envelope, claim_outbox, fail_outbox, mark_outbox_published
from .store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("outbox-worker")


def create_producer(settings: Settings) -> KafkaProducer:
    while True:
        try:
            return KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                key_serializer=lambda value: value.encode("utf-8"),
                acks="all",
                retries=5,
                client_id="backoffice-outbox-publisher",
            )
        except Exception:
            LOGGER.exception("Kafka producer unavailable; retrying")
            time.sleep(2)


def run() -> None:
    settings = Settings(eventing_enabled=True)
    store = Store(settings.database_path, eventing_enabled=True)
    producer = create_producer(settings)
    LOGGER.info("Outbox worker started")
    while True:
        rows = claim_outbox(store)
        if not rows:
            time.sleep(settings.worker_poll_seconds)
            continue
        for row in rows:
            try:
                envelope = build_envelope(row)
                producer.send(row["topic"], key=row["message_key"], value=envelope).get(timeout=10)
                mark_outbox_published(store, row["id"])
                LOGGER.info("Published event %s (%s)", row["event_id"], row["event_type"])
            except Exception as exc:  # pragma: no cover - exercised by container integration
                status = fail_outbox(store, row, str(exc), settings.worker_max_attempts)
                LOGGER.exception("Outbox event %s moved to %s", row["event_id"], status)


if __name__ == "__main__":
    run()
