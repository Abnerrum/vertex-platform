import os
from pathlib import Path

import pytest

TEST_DB = Path(__file__).resolve().parent / "test_vertex.db"

if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes-long"

from fastapi.testclient import TestClient  # noqa: E402

from app.database.session import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

ADMIN = {
    "name": "Administrador",
    "email": "admin@vertex.com.br",
    "password": "Teste1234",
}


@pytest.fixture
def admin_credentials():
    return dict(ADMIN)


@pytest.fixture
def api():
    """Cliente HTTP com banco limpo a cada teste."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_headers(api):
    """Cria o administrador inicial e devolve o header Bearer."""
    response = api.post("/api/v1/auth/bootstrap", json=ADMIN)
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()
