from __future__ import annotations

import json
import logging
import time

from kafka import KafkaConsumer, KafkaProducer

from .config import Settings
from .eventing import process_envelope, record_consumer_dead_letter
from .store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("workflow-worker")


def create_consumer(settings: Settings) -> KafkaConsumer:
    while True:
        try:
            return KafkaConsumer(
                settings.events_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
                group_id=settings.consumer_group,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda value: json.loads(value.decode("utf-8")),
                client_id="backoffice-workflow-worker",
                max_poll_records=20,
            )
        except Exception:
            LOGGER.exception("Kafka consumer unavailable; retrying")
            time.sleep(2)


def create_producer(settings: Settings) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8"),
        acks="all",
        retries=5,
        client_id="backoffice-dlq-publisher",
    )


def run() -> None:
    settings = Settings(eventing_enabled=True)
    store = Store(settings.database_path, eventing_enabled=True)
    consumer = create_consumer(settings)
    producer = create_producer(settings)
    LOGGER.info("Workflow worker started")
    for message in consumer:
        envelope = message.value
        processed = False
        last_error = ""
        for attempt in range(1, settings.worker_max_attempts + 1):
            try:
                outcome = process_envelope(store, settings.consumer_group, envelope)
                LOGGER.info("Event %s processed as %s", envelope.get("eventId"), outcome)
                processed = True
                break
            except Exception as exc:  # pragma: no cover - exercised by container integration
                last_error = str(exc)
                LOGGER.warning(
                    "Event %s failed on attempt %s/%s: %s",
                    envelope.get("eventId"), attempt, settings.worker_max_attempts, exc,
                )
                if attempt < settings.worker_max_attempts:
                    time.sleep(min(10, 2 ** attempt))
        if not processed:
            dead_letter_id = record_consumer_dead_letter(
                store, settings.events_topic, envelope, last_error, settings.worker_max_attempts
            )
            try:
                producer.send(
                    settings.dlq_topic,
                    key=envelope.get("caseId", "unknown"),
                    value={"deadLetterId": dead_letter_id, "sourceTopic": settings.events_topic, "envelope": envelope},
                ).get(timeout=10)
            except Exception:
                LOGGER.exception("DLQ topic publication failed; durable dead letter remains in SQLite")
            LOGGER.error("Event %s moved to dead letter %s", envelope.get("eventId"), dead_letter_id)
        consumer.commit()


if __name__ == "__main__":
    run()
