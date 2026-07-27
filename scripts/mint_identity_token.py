from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import jwt


def mint(private_key: Path, subject: str, subject_type: str, roles: list[str], tenant: str, purpose: str, ttl: int, issuer: str, audience: str) -> str:
    if ttl < 1 or ttl > 300:
        raise ValueError("ttl must be between 1 and 300 seconds")
    now = datetime.now(timezone.utc)
    claims = {
        "iss": issuer,
        "sub": subject,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl)).timestamp()),
        "jti": str(uuid4()),
        "tenant_id": tenant,
        "roles": roles,
        "subject_type": subject_type.upper(),
        "purpose": purpose.upper(),
    }
    return jwt.encode(claims, private_key.read_text(encoding="utf-8"), algorithm="EdDSA")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mint a short-lived local token for the secure baseline.")
    parser.add_argument("--private-key", default=".local/security/identity-private.pem")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--subject-type", choices=["HUMAN", "WORKLOAD"], required=True)
    parser.add_argument("--roles", required=True, help="Comma-separated roles")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--purpose", choices=["CASE_MANAGEMENT", "OPERATIONS", "AUDIT", "EXECUTION", "APPROVAL"], required=True)
    parser.add_argument("--ttl", type=int, default=120)
    parser.add_argument("--issuer", default="https://identity.local")
    parser.add_argument("--audience", default="intelligent-backoffice-api")
    args = parser.parse_args()
    token = mint(
        Path(args.private_key),
        args.subject,
        args.subject_type,
        [item.strip() for item in args.roles.split(",") if item.strip()],
        args.tenant,
        args.purpose,
        args.ttl,
        args.issuer,
        args.audience,
    )
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
