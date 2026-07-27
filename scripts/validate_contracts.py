from __future__ import annotations

import sys

from contract_validation.common import CONTRACTS, ContractValidationError, known_identifiers
from contract_validation.event_policy_validator import (
    validate_asyncapi,
    validate_catalog,
    validate_json_schemas,
    validate_policy_contract,
)
from contract_validation.openapi_validator import validate_openapi


def main() -> int:
    try:
        known_rules, known_capabilities = known_identifiers()
        schema_count = validate_json_schemas()
        api_ids, policy_actions = validate_openapi(
            CONTRACTS / "openapi/platform-api.yaml", known_rules, known_capabilities
        )
        event_ids = validate_asyncapi(
            CONTRACTS / "asyncapi/platform-events.yaml", known_rules, known_capabilities
        )
        policy_ids = validate_policy_contract(
            CONTRACTS / "policy/authorization.yaml", known_rules, policy_actions
        )
        all_ids = api_ids | event_ids | policy_ids
        if len(all_ids) != len(api_ids) + len(event_ids) + len(policy_ids):
            raise ContractValidationError("Contract IDs colidem entre HTTP, eventos e policies")
        validate_catalog(api_ids, event_ids, policy_ids)
    except ContractValidationError as exc:
        print(f"Contract validation failed: {exc}", file=sys.stderr)
        return 1
    print(
        "Contracts valid: "
        f"{len(api_ids)} HTTP operations, {len(event_ids)} events, "
        f"{len(policy_ids)} policies and {schema_count} schema documents."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
