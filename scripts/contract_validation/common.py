from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
ID_PATTERN = re.compile(r"^(API|EVT|POL)-[A-Z]+(?:-[A-Z]+)*-[0-9]{3}$")
BUSINESS_RULE_PATTERN = re.compile(r"\bBR-[0-9]{3}\b")
CAPABILITY_PATTERN = re.compile(r"\b(?:CAP|PLT)-[0-9]{3}\b")


class ContractValidationError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ContractValidationError(f"YAML inválido em {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractValidationError(f"{path.relative_to(ROOT)} deve conter um objeto YAML no topo")
    return data


def resolve_pointer(document: Any, fragment: str, source: Path) -> Any:
    if not fragment:
        return document
    if not fragment.startswith("/"):
        raise ContractValidationError(f"Fragmento inválido em {source.relative_to(ROOT)}: #{fragment}")
    current = document
    for raw_part in fragment.lstrip("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as exc:
                raise ContractValidationError(f"JSON Pointer inexistente em {source.relative_to(ROOT)}: #{fragment}") from exc
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise ContractValidationError(f"JSON Pointer inexistente em {source.relative_to(ROOT)}: #{fragment}")
    return current


def resolve_ref(ref: str, source: Path) -> tuple[Any, Path]:
    file_part, separator, fragment = ref.partition("#")
    target_path = source if not file_part else (source.parent / file_part).resolve()
    try:
        target_path.relative_to(ROOT)
    except ValueError as exc:
        raise ContractValidationError(f"Referência escapa do repositório: {ref}") from exc
    if not target_path.exists():
        raise ContractValidationError(f"Arquivo referenciado não existe em {source.relative_to(ROOT)}: {ref}")
    document = load_yaml(target_path)
    return (resolve_pointer(document, fragment, target_path) if separator else document), target_path


def walk_refs(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref
        for child in value.values():
            yield from walk_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_refs(child)


def validate_refs(path: Path, document: dict[str, Any]) -> None:
    for ref in walk_refs(document):
        if ref.startswith(("http://", "https://")):
            raise ContractValidationError(f"Referência remota não permitida em {path.relative_to(ROOT)}: {ref}")
        resolve_ref(ref, path)


def known_identifiers() -> tuple[set[str], set[str]]:
    rules_text = (ROOT / "docs/functional/business-rules.md").read_text(encoding="utf-8")
    capabilities_text = (ROOT / "docs/functional/capability-map.md").read_text(encoding="utf-8")
    return set(BUSINESS_RULE_PATTERN.findall(rules_text)), set(CAPABILITY_PATTERN.findall(capabilities_text))


def validate_id_references(
    source: str,
    business_rules: list[Any],
    capabilities: list[Any],
    known_rules: set[str],
    known_capabilities: set[str],
) -> None:
    invalid_rules = sorted({str(item) for item in business_rules} - known_rules)
    invalid_capabilities = sorted({str(item) for item in capabilities} - known_capabilities)
    if invalid_rules:
        raise ContractValidationError(f"{source} referencia regras inexistentes: {invalid_rules}")
    if invalid_capabilities:
        raise ContractValidationError(f"{source} referencia capacidades inexistentes: {invalid_capabilities}")
