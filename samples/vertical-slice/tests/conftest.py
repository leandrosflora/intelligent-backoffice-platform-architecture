from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app

@pytest.fixture()
def client(tmp_path: Path):
    app = create_app(Settings(database_path=str(tmp_path / "test.db"), policy_mode="embedded"))
    with TestClient(app) as test_client:
        yield test_client

def headers(role, subject="user-1", tenant="tenant-a", subject_type="HUMAN", correlation="corr-1"):
    return {
        "X-Subject-Id": subject,
        "X-Subject-Type": subject_type,
        "X-Roles": role,
        "X-Tenant-Id": tenant,
        "X-Correlation-Id": correlation,
    }
