package intelligent_backoffice.authorization_test

import rego.v1
import data.intelligent_backoffice.authorization

signed_input := {
    "subject": {
        "id": "workload-1",
        "type": "WORKLOAD",
        "tenant_id": "tenant-a",
        "roles": ["case-reader"],
        "authentication_method": "SIGNED_JWT",
        "token_id": "jti-1",
    },
    "action": "case.read",
    "resource": {
        "type": "CASE",
        "id": "case-1",
        "tenant_id": "tenant-a",
        "state": "CREATED",
    },
    "purpose": "CASE_MANAGEMENT",
    "correlation_id": "corr-1",
    "context": {"identity_mode": "jwt"},
}

test_signed_jwt_profile_is_allowed if {
    authorization.allow with input as signed_input
}

test_header_identity_is_denied_in_jwt_profile if {
    modified := object.union(signed_input, {
        "subject": object.union(signed_input.subject, {
            "authentication_method": "HEADER",
            "token_id": "",
        }),
    })
    not authorization.allow with input as modified
}

test_wrong_purpose_is_denied if {
    modified := object.union(signed_input, {"purpose": "OPERATIONS"})
    not authorization.allow with input as modified
}

test_missing_token_identifier_is_denied if {
    modified := object.union(signed_input, {
        "subject": object.union(signed_input.subject, {"token_id": ""}),
    })
    not authorization.allow with input as modified
}

test_header_baseline_remains_supported if {
    modified := object.union(signed_input, {
        "subject": object.union(signed_input.subject, {
            "authentication_method": "HEADER",
            "token_id": "",
        }),
        "context": {"identity_mode": "headers"},
    })
    authorization.allow with input as modified
}
