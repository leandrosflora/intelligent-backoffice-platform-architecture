from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def keypair(tmp_path):
    private = Ed25519PrivateKey.generate()
    private_pem = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_path = tmp_path / "private.pem"
    public_path = tmp_path / "public.pem"
    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)
    return private_path, public_path


def token(private_path, *, roles, audience="intelligent-backoffice-api", ttl=120, expired=False):
    now = datetime.now(timezone.utc)
    issued = now - timedelta(minutes=5) if expired else now
    expires = now - timedelta(seconds=1) if expired else issued + timedelta(seconds=ttl)
    claims = {
        "iss": "https://identity.local",
        "sub": "subject-1",
        "aud": audience,
        "iat": int(issued.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": str(uuid4()),
        "tenant_id": "tenant-a",
        "roles": roles,
        "subject_type": "HUMAN",
        "purpose": "CASE_MANAGEMENT",
    }
    return jwt.encode(claims, private_path.read_text(), algorithm="EdDSA")


def client(tmp_path):
    private_path, public_path = keypair(tmp_path)
    settings = Settings(
        database_path=str(tmp_path / "jwt.db"),
        policy_mode="embedded",
        identity_mode="jwt",
        identity_public_key_path=str(public_path),
    )
    return TestClient(create_app(settings)), private_path


def test_jwt_is_required(tmp_path):
    api, _ = client(tmp_path)
    response = api.post("/v1/cases", json={"external_id": "x", "dispute_type": "CARD", "amount_cents": 100})
    assert response.status_code == 401


def test_valid_signed_identity_and_header_spoofing_is_ignored(tmp_path):
    api, private_path = client(tmp_path)
    manager = token(private_path, roles=["case-manager"])
    created = api.post(
        "/v1/cases",
        json={"external_id": "signed-case", "dispute_type": "CARD", "amount_cents": 100},
        headers={"Authorization": f"Bearer {manager}", "X-Correlation-Id": "signed-create"},
    )
    assert created.status_code == 200

    reader = token(private_path, roles=["case-reader"])
    spoofed = api.post(
        "/v1/cases",
        json={"external_id": "spoofed", "dispute_type": "CARD", "amount_cents": 100},
        headers={
            "Authorization": f"Bearer {reader}",
            "X-Correlation-Id": "spoofed",
            "X-Roles": "case-manager",
            "X-Subject-Id": "attacker",
            "X-Subject-Type": "HUMAN",
            "X-Tenant-Id": "tenant-a",
        },
    )
    assert spoofed.status_code == 403


def test_invalid_audience_expiry_and_excessive_ttl_are_rejected(tmp_path):
    api, private_path = client(tmp_path)
    payload = {"external_id": "invalid", "dispute_type": "CARD", "amount_cents": 100}
    for invalid in (
        token(private_path, roles=["case-manager"], audience="wrong"),
        token(private_path, roles=["case-manager"], expired=True),
        token(private_path, roles=["case-manager"], ttl=301),
    ):
        response = api.post(
            "/v1/cases",
            json=payload,
            headers={"Authorization": f"Bearer {invalid}", "X-Correlation-Id": str(uuid4())},
        )
        assert response.status_code == 401


def test_tampered_signature_is_rejected(tmp_path):
    api, private_path = client(tmp_path)
    signed = token(private_path, roles=["case-manager"])
    tampered = signed[:-2] + ("aa" if signed[-2:] != "aa" else "bb")
    response = api.post(
        "/v1/cases",
        json={"external_id": "tampered", "dispute_type": "CARD", "amount_cents": 100},
        headers={"Authorization": f"Bearer {tampered}", "X-Correlation-Id": "tampered"},
    )
    assert response.status_code == 401
