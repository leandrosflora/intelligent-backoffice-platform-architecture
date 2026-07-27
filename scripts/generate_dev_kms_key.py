from __future__ import annotations

import argparse
import base64
import os
import secrets
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an ephemeral AES-256 key for the local backup drill.")
    parser.add_argument("--output", default=".local/security/backup-aes256.key")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not args.force:
        raise SystemExit("key already exists; pass --force to rotate the local-only key")
    path.write_text(base64.b64encode(secrets.token_bytes(32)).decode() + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    print(f"Generated ephemeral local backup key at {path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
