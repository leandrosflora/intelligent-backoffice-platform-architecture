from __future__ import annotations

import re
from pathlib import Path

from jsonschema import Draft202012Validator

from .common import (
    CONTRACTS,
    ROOT,
    ContractValidationError,
    ID_PATTERN,
    load_yaml,
    validate_id_references,
    validate_refs,
)


def validate_asyncapi(path: Path, known_rules: set[str], known_capabilities: set[str]) -> set[str]:
    document = load_yaml(path)
    validate_refs(path, document)
    if document.get("asyncapi") != "3.0.0":
        raise ContractValidationError("AsyncAPI deve usar versão 3.0.0")
    channels = document.get("channels", {})
    messages = document.get("components", {}).get("messages", {})
    operations = document.get("operations", {})
    if not (len(channels) == len(messages) == len(operations)):
        raise ContractValidationError("Cada evento deve possuir channel, message e operation")

    addresses: set[str] = set()
    contract_ids: set[str] = set()
    for channel_name, channel in channels.items():
        address = channel.get("address")
        if not isinstance(address, str) or not address.endswith(".v1"):
            raise ContractValidationError(f"Channel sem versionamento explícito: {channel_name}")
        if address in addresses:
            raise ContractValidationError(f"Endereço AsyncAPI duplicado: {address}")
        addresses.add(address)

    for message_name, message in messages.items():
        source = f"message {message_name}"
        contract_id = message.get("x-contract-id")
        if not isinstance(contract_id, str) or not ID_PATTERN.match(contract_id):
            raise ContractValidationError(f"x-contract-id inválido em {source}: {contract_id}")
        if contract_id in contract_ids:
            raise ContractValidationError(f"x-contract-id duplicado: {contract_id}")
        contract_ids.add(contract_id)
        rules = message.get("x-business-rules")
        capabilities = message.get("x-capabilities")
        if not isinstance(rules, list) or not isinstance(capabilities, list):
            raise ContractValidationError(f"Rastreabilidade ausente em {source}")
        validate_id_references(source, rules, capabilities, known_rules, known_capabilities)
        payload = message.get("payload", {})
        if not isinstance(payload, dict) or "$ref" not in payload:
            raise ContractValidationError(f"Payload canônico ausente em {source}")
        if message.get("correlationId", {}).get("location") != "$message.payload#/correlationId":
            raise ContractValidationError(f"correlationId inválido em {source}")
    if len(messages) < 10:
        raise ContractValidationError("AsyncAPI deve cobrir os eventos críticos do lifecycle")
    return contract_ids


def validate_json_schemas() -> int:
    schema_ids: set[str] = set()
    schema_files = sorted((CONTRACTS / "schemas").rglob("*.yaml"))
    if len(schema_files) < 3:
        raise ContractValidationError("Catálogo mínimo de schemas canônicos ausente")
    for path in schema_files:
        document = load_yaml(path)
        validate_refs(path, document)
        try:
            Draft202012Validator.check_schema(document)
        except Exception as exc:  # noqa: BLE001
            raise ContractValidationError(f"JSON Schema inválido em {path.relative_to(ROOT)}: {exc}") from exc
        schema_id = document.get("$id")
        if not schema_id or schema_id in schema_ids:
            raise ContractValidationError(f"$id ausente ou duplicado em {path.relative_to(ROOT)}")
        schema_ids.add(schema_id)
    return len(schema_files)


def validate_policy_contract(path: Path, known_rules: set[str], policy_actions_from_api: set[str]) -> set[str]:
    document = load_yaml(path)
    validate_refs(path, document)
    if document.get("defaultDecision") != "DENY":
        raise ContractValidationError("Policy contract deve usar defaultDecision=DENY")
    rule_ids: set[str] = set()
    actions: set[str] = set()
    for rule in document.get("rules", []):
        rule_id = rule.get("id")
        action = rule.get("action")
        if not isinstance(rule_id, str) or not ID_PATTERN.match(rule_id):
            raise ContractValidationError(f"Policy id inválido: {rule_id}")
        if rule_id in rule_ids or action in actions:
            raise ContractValidationError(f"Policy id ou action duplicado: {rule_id}/{action}")
        rule_ids.add(rule_id)
        actions.add(action)
        if not rule.get("allowedRoles") or not rule.get("subjectTypes"):
            raise ContractValidationError(f"Policy sem papéis ou subjectTypes: {rule_id}")
        if "tenant-match" not in rule.get("conditions", []):
            raise ContractValidationError(f"Policy sem isolamento por tenant: {rule_id}")
        if "audit-decision" not in rule.get("obligations", []):
            raise ContractValidationError(f"Policy sem obrigação de auditoria: {rule_id}")
        unknown = set(rule.get("businessRules", [])) - known_rules
        if unknown:
            raise ContractValidationError(f"Policy {rule_id} referencia regras inexistentes: {sorted(unknown)}")

    expected_actions = policy_actions_from_api - {"public.health"}
    if actions != expected_actions:
        raise ContractValidationError(
            f"Actions OpenAPI e policy divergem. Ausentes={sorted(expected_actions - actions)}, "
            f"extras={sorted(actions - expected_actions)}"
        )
    rego = (ROOT / "policies/authorization.rego").read_text(encoding="utf-8")
    if "default allow := false" not in rego:
        raise ContractValidationError("Rego deve declarar default allow := false")
    for action in actions:
        if f'input.action == "{action}"' not in rego:
            raise ContractValidationError(f"Action não implementada no Rego: {action}")
    tests = (ROOT / "policies/authorization_test.rego").read_text(encoding="utf-8")
    if len(re.findall(r"(?m)^test_[a-z0-9_]+ if", tests)) < 8:
        raise ContractValidationError("Suite Rego deve possuir ao menos oito testes")
    return rule_ids


def validate_catalog(api_ids: set[str], event_ids: set[str], policy_ids: set[str]) -> None:
    catalog = load_yaml(CONTRACTS / "catalog.yaml")
    contracts = catalog.get("contracts", {})
    expected = {"httpOperations": api_ids, "domainEvents": event_ids, "policyRules": policy_ids}
    for kind, expected_ids in expected.items():
        values = contracts.get(kind, [])
        actual_ids = set(values)
        if len(actual_ids) != len(values):
            raise ContractValidationError(f"Catálogo possui IDs duplicados em {kind}")
        if actual_ids != expected_ids:
            raise ContractValidationError(
                f"Catálogo {kind} diverge. Ausentes={sorted(expected_ids - actual_ids)}, "
                f"extras={sorted(actual_ids - expected_ids)}"
            )
    for source in catalog.get("sources", {}).values():
        if not (ROOT / source).exists():
            raise ContractValidationError(f"Fonte inexistente no catálogo: {source}")
