from __future__ import annotations

from pathlib import Path

from .observability import INTELLIGENCE_OUTCOMES


def classify_document(filename: str, content_type: str = "application/pdf") -> dict:
    normalized = Path(filename).name.lower()
    allowed_type = content_type in {"application/pdf", "image/png", "image/jpeg"}
    mapping = (
        ({"proof", "receipt", "comprovante"}, "TRANSACTION_PROOF"),
        ({"statement", "extrato"}, "ACCOUNT_STATEMENT"),
        ({"identity", "identidade", "cnh", "rg"}, "IDENTITY_DOCUMENT"),
    )
    for keywords, document_type in mapping:
        if allowed_type and any(keyword in normalized for keyword in keywords):
            result = {"document_type": document_type, "confidence": 0.99, "abstained": False}
            INTELLIGENCE_OUTCOMES.labels("document-classification", document_type).inc()
            return result
    result = {"document_type": "UNKNOWN", "confidence": 0.0, "abstained": True}
    INTELLIGENCE_OUTCOMES.labels("document-classification", "ABSTAIN").inc()
    return result


def investigate_case(evidence_references: list[str]) -> dict:
    if evidence_references:
        result = {
            "finding": "transaction-confirmed",
            "grounded": True,
            "source_count": len(evidence_references),
            "abstained": False,
        }
    else:
        result = {
            "finding": "insufficient-evidence",
            "grounded": False,
            "source_count": 0,
            "abstained": True,
        }
    INTELLIGENCE_OUTCOMES.labels("investigation", result["finding"]).inc()
    return result


def propose_recommendation(finding: str, evidence_references: list[str]) -> dict:
    if finding == "transaction-confirmed" and evidence_references:
        result = {
            "outcome": "APPROVE",
            "rationale_code": "EVIDENCE_CONFIRMS_TRANSACTION",
            "grounded": True,
            "abstained": False,
        }
    else:
        result = {
            "outcome": "ABSTAIN",
            "rationale_code": "INSUFFICIENT_GROUNDED_EVIDENCE",
            "grounded": False,
            "abstained": True,
        }
    INTELLIGENCE_OUTCOMES.labels("recommendation", result["outcome"]).inc()
    return result
