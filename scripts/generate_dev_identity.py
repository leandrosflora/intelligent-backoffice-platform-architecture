from __future__ import annotations

import argparse
import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an ephemeral Ed25519 key pair for the local secure profile.")
    parser.add_argument("--output-dir", default=".local/security")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    private_path = output / "identity-private.pem"
    public_path = output / "identity-public.pem"
    if not args.force and (private_path.exists() or public_path.exists()):
        raise SystemExit("identity files already exist; pass --force to replace the local-only keys")

    private = Ed25519PrivateKey.generate()
    private_path.write_bytes(
        private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    os.chmod(private_path, 0o600)
    os.chmod(public_path, 0o644)
    print(f"Generated local Ed25519 identity under {output}. Private material is gitignored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
