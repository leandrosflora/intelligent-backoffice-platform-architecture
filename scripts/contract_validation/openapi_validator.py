from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .common import (
    ContractValidationError,
    HTTP_METHODS,
    ID_PATTERN,
    load_yaml,
    resolve_pointer,
    resolve_ref,
    validate_id_references,
    validate_refs,
)


def operation_parameter_names(operation: dict[str, Any], document: dict[str, Any], path: Path) -> set[str]:
    names: set[str] = set()
    for parameter in operation.get("parameters", []):
        if "$ref" in parameter:
            ref = parameter["$ref"]
            if ref.startswith("#"):
                resolved = resolve_pointer(document, ref.split("#", 1)[1], path)
            else:
                resolved, _ = resolve_ref(ref, path)
            names.add(resolved["name"])
        elif "name" in parameter:
            names.add(parameter["name"])
    return names


def iter_operations(path: Path, document: dict[str, Any]):
    for route, raw_path_item in document.get("paths", {}).items():
        path_item = raw_path_item
        if isinstance(raw_path_item, dict) and "$ref" in raw_path_item:
            path_item, source_path = resolve_ref(raw_path_item["$ref"], path)
        else:
            source_path = path
        for method, operation in path_item.items():
            if method in HTTP_METHODS:
                yield route, method, operation, source_path


def validate_openapi(
    path: Path, known_rules: set[str], known_capabilities: set[str]
) -> tuple[set[str], set[str]]:
    document = load_yaml(path)
    validate_refs(path, document)
    for fragment in sorted((path.parent / "paths").glob("*.yaml")):
        validate_refs(fragment, load_yaml(fragment))
    if document.get("openapi") != "3.1.0":
        raise ContractValidationError("OpenAPI deve usar versão 3.1.0")

    try:
        from openapi_spec_validator import validate_spec
        validate_spec(document, base_uri=path.resolve().as_uri())
    except ImportError as exc:
        if os.getenv("CI"):
            raise ContractValidationError("Dependência openapi-spec-validator não instalada") from exc
        print("Warning: openapi-spec-validator não instalado; validação estrutural continuará.", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        raise ContractValidationError(f"OpenAPI inválido: {exc}") from exc

    operation_ids: set[str] = set()
    contract_ids: set[str] = set()
    policy_actions: set[str] = set()
    for route, method, operation, source_path in iter_operations(path, document):
        source = f"{method.upper()} {route}"
        operation_id = operation.get("operationId")
        if not operation_id or operation_id in operation_ids:
            raise ContractValidationError(f"operationId ausente ou duplicado em {source}: {operation_id}")
        operation_ids.add(operation_id)

        contract_id = operation.get("x-contract-id")
        if not isinstance(contract_id, str) or not ID_PATTERN.match(contract_id):
            raise ContractValidationError(f"x-contract-id inválido em {source}: {contract_id}")
        if contract_id in contract_ids:
            raise ContractValidationError(f"x-contract-id duplicado: {contract_id}")
        contract_ids.add(contract_id)

        rules = operation.get("x-business-rules")
        capabilities = operation.get("x-capabilities")
        action = operation.get("x-policy-action")
        if not isinstance(rules, list) or not isinstance(capabilities, list) or not isinstance(action, str):
            raise ContractValidationError(f"Extensões de rastreabilidade ausentes em {source}")
        validate_id_references(source, rules, capabilities, known_rules, known_capabilities)
        policy_actions.add(action)

        if route != "/health":
            if not operation.get("security") and not document.get("security"):
                raise ContractValidationError(f"Security ausente em {source}")
            parameters = operation_parameter_names(operation, document, source_path)
            required = {"X-Tenant-Id", "X-Correlation-Id"}
            if not required.issubset(parameters):
                raise ContractValidationError(f"Headers obrigatórios ausentes em {source}: {sorted(required - parameters)}")
            if method in {"post", "put", "patch", "delete"}:
                if operation.get("x-idempotent") is not True:
                    raise ContractValidationError(f"Operação mutável sem x-idempotent=true: {source}")
                if "Idempotency-Key" not in parameters:
                    raise ContractValidationError(f"Idempotency-Key ausente em {source}")
                if route != "/v1/cases" and "If-Match" not in parameters:
                    raise ContractValidationError(f"If-Match ausente em transição de estado: {source}")
            response_codes = {str(code) for code in operation.get("responses", {})}
            if not {"401", "403"}.issubset(response_codes):
                raise ContractValidationError(f"Respostas 401/403 ausentes em {source}")
    if len(operation_ids) < 10:
        raise ContractValidationError("OpenAPI deve conter o conjunto mínimo de operações do lifecycle")
    return contract_ids, policy_actions
