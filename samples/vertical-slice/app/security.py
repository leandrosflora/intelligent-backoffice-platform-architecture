from dataclasses import dataclass
from fastapi import Header, HTTPException

@dataclass(frozen=True)
class RequestContext:
    subject_id: str
    subject_type: str
    roles: list[str]
    tenant_id: str
    correlation_id: str

def request_context(
    x_subject_id: str = Header(..., alias="X-Subject-Id"),
    x_subject_type: str = Header(..., alias="X-Subject-Type"),
    x_roles: str = Header(..., alias="X-Roles"),
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    x_correlation_id: str = Header(..., alias="X-Correlation-Id"),
) -> RequestContext:
    subject_type = x_subject_type.upper()
    if subject_type not in {"HUMAN", "WORKLOAD"}:
        raise HTTPException(400, "X-Subject-Type must be HUMAN or WORKLOAD")
    roles = [item.strip() for item in x_roles.split(",") if item.strip()]
    if not roles:
        raise HTTPException(400, "X-Roles must contain at least one role")
    return RequestContext(x_subject_id, subject_type, roles, x_tenant_id, x_correlation_id)
