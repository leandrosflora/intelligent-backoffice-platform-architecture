package intelligent_backoffice.authorization_test

import rego.v1
import data.intelligent_backoffice.authorization

base_input := {
    "subject": {
        "id": "user-1",
        "type": "HUMAN",
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "roles": ["case-reader"],
    },
    "action": "case.read",
    "resource": {
        "type": "CASE",
        "id": "case-1",
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "state": "CREATED",
    },
    "purpose": "CASE_PROCESSING",
    "correlation_id": "22222222-2222-2222-2222-222222222222",
    "context": {},
}

test_case_read_same_tenant if {
    authorization.allow with input as base_input
}

test_cross_tenant_is_denied if {
    modified := object.union(base_input, {
        "resource": object.union(base_input.resource, {"tenant_id": "33333333-3333-3333-3333-333333333333"}),
    })
    not authorization.allow with input as modified
}

test_recommendation_with_evidence_is_allowed if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"type": "WORKLOAD", "roles": ["decision-agent"]}),
        "action": "recommendation.create",
        "resource": object.union(base_input.resource, {"state": "UNDER_INVESTIGATION"}),
        "context": {
            "case_version": 4,
            "evidence_references": ["44444444-4444-4444-4444-444444444444"],
        },
    })
    authorization.allow with input as modified
}

test_recommendation_without_evidence_is_denied if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"type": "WORKLOAD", "roles": ["decision-agent"]}),
        "action": "recommendation.create",
        "resource": object.union(base_input.resource, {"state": "UNDER_INVESTIGATION"}),
        "context": {"case_version": 4, "evidence_references": []},
    })
    not authorization.allow with input as modified
}

test_self_approval_is_denied if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"id": "same-actor", "roles": ["approver"]}),
        "action": "approval.decide",
        "resource": object.union(base_input.resource, {"state": "AWAITING_APPROVAL"}),
        "purpose": "APPROVAL",
        "context": {
            "case_version": 5,
            "recommendation_actor_id": "same-actor",
            "recommendation_version": 2,
            "approved_recommendation_version": 2,
            "amount": 100.0,
            "authority_limit": 1000.0,
        },
    })
    not authorization.allow with input as modified
}

test_approval_with_segregation_and_authority_is_allowed if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"id": "approver-1", "roles": ["approver"]}),
        "action": "approval.decide",
        "resource": object.union(base_input.resource, {"state": "AWAITING_APPROVAL"}),
        "purpose": "APPROVAL",
        "context": {
            "case_version": 5,
            "recommendation_actor_id": "agent-1",
            "recommendation_version": 2,
            "approved_recommendation_version": 2,
            "amount": 100.0,
            "authority_limit": 1000.0,
        },
    })
    authorization.allow with input as modified
}

test_approval_over_authority_is_denied if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"id": "approver-1", "roles": ["approver"]}),
        "action": "approval.decide",
        "resource": object.union(base_input.resource, {"state": "AWAITING_APPROVAL"}),
        "purpose": "APPROVAL",
        "context": {
            "case_version": 5,
            "recommendation_actor_id": "agent-1",
            "recommendation_version": 2,
            "approved_recommendation_version": 2,
            "amount": 2000.0,
            "authority_limit": 1000.0,
        },
    })
    not authorization.allow with input as modified
}

test_execution_service_with_valid_approval_is_allowed if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"id": "execution-service", "type": "WORKLOAD", "roles": ["execution-service"]}),
        "action": "execution.request",
        "resource": object.union(base_input.resource, {"state": "APPROVED"}),
        "purpose": "EXECUTION",
        "context": {
            "approval_status": "APPROVED",
            "approval_valid": true,
            "recommendation_version": 2,
            "approved_recommendation_version": 2,
            "idempotency_key": "idem-12345678",
            "command_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "evidence_references": ["44444444-4444-4444-4444-444444444444"],
        },
    })
    authorization.allow with input as modified
}

test_execution_without_idempotency_is_denied if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"id": "execution-service", "type": "WORKLOAD", "roles": ["execution-service"]}),
        "action": "execution.request",
        "resource": object.union(base_input.resource, {"state": "APPROVED"}),
        "purpose": "EXECUTION",
        "context": {
            "approval_status": "APPROVED",
            "approval_valid": true,
            "recommendation_version": 2,
            "approved_recommendation_version": 2,
            "idempotency_key": "",
            "command_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "evidence_references": ["44444444-4444-4444-4444-444444444444"],
        },
    })
    not authorization.allow with input as modified
}

test_analyst_cannot_execute if {
    modified := object.union(base_input, {
        "subject": object.union(base_input.subject, {"roles": ["operations-analyst"]}),
        "action": "execution.request",
        "resource": object.union(base_input.resource, {"state": "APPROVED"}),
        "purpose": "EXECUTION",
        "context": {
            "approval_status": "APPROVED",
            "approval_valid": true,
            "recommendation_version": 2,
            "approved_recommendation_version": 2,
            "idempotency_key": "idem-12345678",
            "command_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "evidence_references": ["44444444-4444-4444-4444-444444444444"],
        },
    })
    not authorization.allow with input as modified
}
