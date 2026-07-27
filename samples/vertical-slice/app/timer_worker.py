from __future__ import annotations

import logging
import time

from .config import Settings
from .eventing import claim_due_timers, fail_timer, fire_timer
from .store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("timer-worker")


def run() -> None:
    settings = Settings(eventing_enabled=True)
    store = Store(settings.database_path, eventing_enabled=True)
    LOGGER.info("Timer worker started")
    while True:
        timers = claim_due_timers(store)
        if not timers:
            time.sleep(settings.worker_poll_seconds)
            continue
        for timer in timers:
            try:
                fire_timer(store, timer)
                LOGGER.info("Timer %s fired", timer["id"])
            except Exception as exc:  # pragma: no cover - exercised by container integration
                status = fail_timer(store, timer, str(exc), settings.worker_max_attempts)
                LOGGER.exception("Timer %s moved to %s", timer["id"], status)


if __name__ == "__main__":
    run()
