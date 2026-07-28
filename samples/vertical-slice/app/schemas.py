from typing import Literal

from pydantic import BaseModel, Field


class CreateCaseRequest(BaseModel):
    external_id: str = Field(min_length=1, max_length=128)
    dispute_type: str = Field(min_length=1, max_length=64)
    amount_cents: int = Field(ge=1)


class RegisterDocumentRequest(BaseModel):
    document_id: str
    filename: str
    content_type: Literal["application/pdf", "image/png", "image/jpeg"] = "application/pdf"


class RecommendationRequest(BaseModel):
    outcome: Literal["APPROVE", "REJECT"]
    rationale: str = Field(min_length=3)
    evidence_references: list[str] = Field(min_length=1)


class ApprovalRequest(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    authority_limit_cents: int = Field(ge=0)
    reason: str = Field(min_length=3)


class ExecutionRequest(BaseModel):
    result_mode: Literal["SUCCESS", "AMBIGUOUS"] = "SUCCESS"


class ReconciliationResolutionRequest(BaseModel):
    case_version: int = Field(ge=1)
    resolution: Literal["CONFIRMED_SUCCEEDED", "CONFIRMED_FAILED", "ESCALATED"]
    reason: str = Field(min_length=10, max_length=500)
