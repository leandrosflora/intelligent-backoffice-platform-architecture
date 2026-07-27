package intelligent_backoffice.authorization_p6_test

import rego.v1
import data.intelligent_backoffice.authorization

base := {
    "subject": {
        "id": "operator-1",
        "type": "HUMAN",
        "tenant_id": "tenant-a",
        "roles": ["platform-operator"],
    },
    "action": "event.read",
    "resource": {
        "type": "EVENT_OPERATIONS",
        "id": "resource-1",
        "tenant_id": "tenant-a",
        "state": "OPERATIONAL",
    },
    "purpose": "OPERATIONS",
    "correlation_id": "corr-1",
    "context": {},
}

test_operator_can_read_event_operations if {
    authorization.allow with input as base
}

test_case_manager_can_schedule_non_terminal_timer if {
    modified := object.union(base, {
        "subject": object.union(base.subject, {"roles": ["case-manager"]}),
        "action": "timer.schedule",
        "resource": object.union(base.resource, {"state": "CREATED"}),
        "context": {"timer_type": "CASE_EXPIRY", "delay_seconds": 10},
    })
    authorization.allow with input as modified
}

test_timer_on_terminal_case_is_denied if {
    modified := object.union(base, {
        "subject": object.union(base.subject, {"roles": ["case-manager"]}),
        "action": "timer.schedule",
        "resource": object.union(base.resource, {"state": "EXECUTED"}),
    })
    not authorization.allow with input as modified
}

test_controlled_replay_requires_reason if {
    modified := object.union(base, {
        "action": "event.replay",
        "resource": object.union(base.resource, {"state": "OPEN"}),
        "context": {"source": "DEAD_LETTER", "reason": "short"},
    })
    not authorization.allow with input as modified
}

test_operator_can_replay_open_dead_letter if {
    modified := object.union(base, {
        "action": "event.replay",
        "resource": object.union(base.resource, {"state": "OPEN"}),
        "context": {"source": "DEAD_LETTER", "reason": "validated replay after incident review"},
    })
    authorization.allow with input as modified
}
