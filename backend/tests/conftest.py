import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="silo-test-")
os.environ["SILO_DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["SILO_RATE_LIMIT_PER_MINUTE"] = "1000"
os.environ["SILO_LIVE_DATA_ENABLED"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    from app.core.database import SessionLocal
    with SessionLocal() as s:
        yield s
