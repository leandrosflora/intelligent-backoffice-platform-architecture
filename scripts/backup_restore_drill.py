from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def load_key(path: Path) -> bytes:
    key = base64.b64decode(path.read_text(encoding="utf-8").strip())
    if len(key) != 32:
        raise ValueError("backup key must decode to 32 bytes")
    return key


def sqlite_backup(source: Path, destination: Path) -> None:
    with sqlite3.connect(source) as src, sqlite3.connect(destination) as dst:
        src.execute("PRAGMA wal_checkpoint(FULL)")
        src.backup(dst)


def integrity(path: Path) -> tuple[str, dict[str, int]]:
    with sqlite3.connect(path) as conn:
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {result}")
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        counts = {name: conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0] for name in tables}
    return result, counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an encrypted SQLite backup and prove restore integrity.")
    parser.add_argument("--database", required=True)
    parser.add_argument("--key-file", required=True)
    parser.add_argument("--output-dir", default="artifacts/backup-drill")
    args = parser.parse_args()

    database = Path(args.database)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    key = load_key(Path(args.key_file))
    aad = b"intelligent-backoffice-backup-v1"

    with tempfile.TemporaryDirectory() as temp_dir:
        plain = Path(temp_dir) / "snapshot.db"
        sqlite_backup(database, plain)
        plain_bytes = plain.read_bytes()
        digest = hashlib.sha256(plain_bytes).hexdigest()
        nonce = os.urandom(12)
        encrypted = AESGCM(key).encrypt(nonce, plain_bytes, aad)
        encrypted_path = output / "snapshot.db.aesgcm"
        encrypted_path.write_bytes(nonce + encrypted)

        restored_bytes = AESGCM(key).decrypt(encrypted_path.read_bytes()[:12], encrypted_path.read_bytes()[12:], aad)
        restored = output / "restored.db"
        restored.write_bytes(restored_bytes)
        restored_digest = hashlib.sha256(restored_bytes).hexdigest()
        check, counts = integrity(restored)
        if digest != restored_digest:
            raise RuntimeError("restored digest differs from the backup snapshot")

    report = {
        "status": "PASSED",
        "algorithm": "AES-256-GCM",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": str(database),
        "encryptedBackup": str(encrypted_path),
        "restoredDatabase": str(restored),
        "sha256": digest,
        "integrityCheck": check,
        "tableCounts": counts,
        "unencryptedBackupArtifactPersisted": False,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
