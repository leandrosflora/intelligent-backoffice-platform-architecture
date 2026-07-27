#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import time


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria JWT HS256 para o vertical slice local.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--type", choices=["HUMAN", "WORKLOAD"], required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--roles", required=True, help="Roles separadas por vírgula.")
    parser.add_argument("--purpose", default="OPERATIONS")
    parser.add_argument("--authority-limit", default="0")
    parser.add_argument("--ttl-seconds", type=int, default=3600)
    args = parser.parse_args()

    secret = os.environ.get(
        "DEMO_JWT_SECRET",
        "local-development-secret-change-me-1234567890",
    ).encode("utf-8")

    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": "intelligent-backoffice-demo",
        "aud": "backoffice-api",
        "sub": args.subject,
        "actor_type": args.type,
        "tenant_id": args.tenant,
        "roles": [item.strip() for item in args.roles.split(",") if item.strip()],
        "purpose": args.purpose,
        "authority_limit": args.authority_limit,
        "iat": now,
        "exp": now + args.ttl_seconds,
    }

    encoded_header = b64url(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = b64url(hmac.new(secret, signing_input, hashlib.sha256).digest())
    print(f"{encoded_header}.{encoded_payload}.{signature}")


if __name__ == "__main__":
    main()
