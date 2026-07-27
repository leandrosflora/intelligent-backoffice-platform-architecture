from prometheus_client import Gauge

from .eventing import eventing_counts
from .store import Store

OUTBOX_MESSAGES = Gauge(
    "backoffice_outbox_messages",
    "Transactional outbox messages by status.",
    ("status",),
)
TIMERS = Gauge(
    "backoffice_timers",
    "Workflow timers by status.",
    ("status",),
)
DEAD_LETTERS = Gauge(
    "backoffice_dead_letters",
    "Dead letters by status.",
    ("status",),
)
INBOX_MESSAGES = Gauge(
    "backoffice_inbox_messages",
    "Messages processed through the idempotent inbox.",
)


def refresh_eventing_metrics(store: Store) -> dict:
    counts = eventing_counts(store)
    for status in ("PENDING", "IN_FLIGHT", "RETRY", "PUBLISHED", "DEAD_LETTER"):
        OUTBOX_MESSAGES.labels(status).set(counts["outbox"].get(status, 0))
    for status in ("SCHEDULED", "IN_FLIGHT", "RETRY", "FIRED", "DEAD_LETTER"):
        TIMERS.labels(status).set(counts["timers"].get(status, 0))
    for status in ("OPEN", "REPLAYED"):
        DEAD_LETTERS.labels(status).set(counts["deadLetters"].get(status, 0))
    INBOX_MESSAGES.set(counts["inbox"].get("PROCESSED", 0))
    return counts
