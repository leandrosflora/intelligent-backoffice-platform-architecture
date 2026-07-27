from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jwt
from fastapi import Header, HTTPException
from jwt import InvalidTokenError

from .config import Settings


@dataclass(frozen=True)
class RequestContext:
    subject_id: str
    subject_type: str
    roles: list[str]
    tenant_id: str
    correlation_id: str
    purpose: str = "CASE_MANAGEMENT"
    authentication_method: str = "HEADER"
    token_id: str = ""


_SECURITY: dict[str, Any] = {
    "identity_mode": "headers",
    "identity_public_key_path": "/run/identity/identity-public.pem",
    "identity_issuer": "https://identity.local",
    "identity_audience": "intelligent-backoffice-api",
    "identity_algorithm": "EdDSA",
    "identity_max_ttl_seconds": 300,
}


def configure_security(settings: Settings) -> None:
    _SECURITY.update(
        {
            "identity_mode": settings.identity_mode.lower(),
            "identity_public_key_path": settings.identity_public_key_path,
            "identity_issuer": settings.identity_issuer,
            "identity_audience": settings.identity_audience,
            "identity_algorithm": settings.identity_algorithm,
            "identity_max_ttl_seconds": settings.identity_max_ttl_seconds,
        }
    )


def _unauthorized(reason: str) -> HTTPException:
    return HTTPException(status_code=401, detail={"reason": reason})


def _jwt_context(authorization: str | None, correlation_id: str | None) -> RequestContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauthorized("bearer-token-required")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        public_key = Path(_SECURITY["identity_public_key_path"]).read_text(encoding="utf-8")
        claims = jwt.decode(
            token,
            public_key,
            algorithms=[_SECURITY["identity_algorithm"]],
            audience=_SECURITY["identity_audience"],
            issuer=_SECURITY["identity_issuer"],
            options={"require": ["iss", "sub", "aud", "iat", "exp", "jti", "tenant_id", "roles", "subject_type", "purpose"]},
        )
    except (OSError, InvalidTokenError, ValueError, TypeError) as exc:
        raise _unauthorized("invalid-workload-token") from exc

    issued_at = int(claims["iat"])
    expires_at = int(claims["exp"])
    ttl = expires_at - issued_at
    if ttl <= 0 or ttl > int(_SECURITY["identity_max_ttl_seconds"]):
        raise _unauthorized("invalid-token-ttl")

    subject_type = str(claims["subject_type"]).upper()
    if subject_type not in {"HUMAN", "WORKLOAD"}:
        raise _unauthorized("invalid-subject-type")
    roles = claims["roles"]
    if not isinstance(roles, list) or not roles or not all(isinstance(role, str) and role for role in roles):
        raise _unauthorized("invalid-roles")
    tenant_id = str(claims["tenant_id"])
    purpose = str(claims["purpose"]).upper()
    if not tenant_id or purpose not in {"CASE_MANAGEMENT", "OPERATIONS", "AUDIT", "EXECUTION", "APPROVAL"}:
        raise _unauthorized("invalid-token-context")

    token_id = str(claims["jti"])
    return RequestContext(
        subject_id=str(claims["sub"]),
        subject_type=subject_type,
        roles=roles,
        tenant_id=tenant_id,
        correlation_id=correlation_id or token_id,
        purpose=purpose,
        authentication_method="SIGNED_JWT",
        token_id=token_id,
    )


def request_context(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_subject_id: str | None = Header(default=None, alias="X-Subject-Id"),
    x_subject_type: str | None = Header(default=None, alias="X-Subject-Type"),
    x_roles: str | None = Header(default=None, alias="X-Roles"),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-Id"),
) -> RequestContext:
    if _SECURITY["identity_mode"] == "jwt":
        return _jwt_context(authorization, x_correlation_id)

    required = {
        "X-Subject-Id": x_subject_id,
        "X-Subject-Type": x_subject_type,
        "X-Roles": x_roles,
        "X-Tenant-Id": x_tenant_id,
        "X-Correlation-Id": x_correlation_id,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise HTTPException(400, detail={"reason": "missing-identity-headers", "headers": missing})
    subject_type = str(x_subject_type).upper()
    if subject_type not in {"HUMAN", "WORKLOAD"}:
        raise HTTPException(400, "X-Subject-Type must be HUMAN or WORKLOAD")
    roles = [item.strip() for item in str(x_roles).split(",") if item.strip()]
    if not roles:
        raise HTTPException(400, "X-Roles must contain at least one role")
    return RequestContext(
        str(x_subject_id),
        subject_type,
        roles,
        str(x_tenant_id),
        str(x_correlation_id),
    )
