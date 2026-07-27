from __future__ import annotations

from pathlib import Path
import re
import sys

ADR_DIR = Path(__file__).resolve().parents[1] / "docs" / "decisions"
ADR_FILENAME = re.compile(r"adr-(?P<id>\d{3})-[a-z0-9-]+\.md$")
EXPECTED_IDS = {f"{number:03d}" for number in range(1, 14)}
ALLOWED_STATUSES = {
    "Proposto",
    "Aceito",
    "Rejeitado",
    "Depreciado",
}
REQUIRED_SECTIONS = (
    "## Contexto",
    "## Decisão",
    "## Alternativas consideradas",
    "## Consequências",
    "## Critérios de revisão",
    "## Evidências e links",
)
REQUIRED_METADATA = (
    "- **Status:**",
    "- **Data:**",
    "- **Decisores:**",
    "- **Escopo:**",
)


def validate_adr(path: Path, adr_id: str) -> list[str]:
    errors: list[str] = []
    content = path.read_text(encoding="utf-8")

    if not content.startswith(f"# ADR-{adr_id} — "):
        errors.append(f"{path}: title must start with '# ADR-{adr_id} — '")

    for metadata in REQUIRED_METADATA:
        if metadata not in content:
            errors.append(f"{path}: missing metadata field {metadata}")

    status_match = re.search(r"^- \*\*Status:\*\* (.+)$", content, re.MULTILINE)
    if not status_match:
        errors.append(f"{path}: status could not be parsed")
    else:
        status = status_match.group(1).strip()
        if status not in ALLOWED_STATUSES and not status.startswith("Substituído por ADR-"):
            errors.append(f"{path}: unsupported status '{status}'")

    date_match = re.search(r"^- \*\*Data:\*\* (\d{4}-\d{2}-\d{2})$", content, re.MULTILINE)
    if not date_match:
        errors.append(f"{path}: date must use YYYY-MM-DD")

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"{path}: missing section {section}")

    return errors


def main() -> int:
    errors: list[str] = []
    if not ADR_DIR.is_dir():
        print(f"ADR directory not found: {ADR_DIR}")
        return 1

    index_path = ADR_DIR / "index.md"
    template_path = ADR_DIR / "template.md"
    for required in (index_path, template_path):
        if not required.is_file():
            errors.append(f"Missing ADR support file: {required}")

    ids: dict[str, Path] = {}
    adr_files = sorted(ADR_DIR.glob("adr-*.md"))
    for path in adr_files:
        match = ADR_FILENAME.fullmatch(path.name)
        if not match:
            errors.append(f"Invalid ADR filename: {path.name}")
            continue
        adr_id = match.group("id")
        if adr_id in ids:
            errors.append(f"Duplicate ADR id {adr_id}: {ids[adr_id].name}, {path.name}")
            continue
        ids[adr_id] = path
        errors.extend(validate_adr(path, adr_id))

    actual_ids = set(ids)
    missing = sorted(EXPECTED_IDS - actual_ids)
    unexpected = sorted(actual_ids - EXPECTED_IDS)
    if missing:
        errors.append("Missing ADR ids: " + ", ".join(missing))
    if unexpected:
        errors.append("Unexpected ADR ids: " + ", ".join(unexpected))

    if index_path.is_file():
        index_content = index_path.read_text(encoding="utf-8")
        for path in ids.values():
            if f"({path.name})" not in index_content:
                errors.append(f"ADR index does not link to {path.name}")

    if errors:
        print("ADR validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"ADR catalog is valid: {len(adr_files)} decisions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
