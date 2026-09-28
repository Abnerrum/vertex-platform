from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_bootstrap_login_and_client_crud():
    bootstrap = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "name": "Abner",
            "email": "admin@vertex.com.br",
            "password": "Teste1234",
        },
    )
    assert bootstrap.status_code == 201, bootstrap.text
    token = bootstrap.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"

    denied = client.get("/api/v1/clients")
    assert denied.status_code == 401

    created = client.post(
        "/api/v1/clients",
        headers=headers,
        json={
            "company_name": "Cliente Teste",
            "responsible_name": "Pessoa Teste",
            "email": "cliente@example.com",
        },
    )
    assert created.status_code == 201, created.text
    client_id = created.json()["id"]

    updated = client.patch(
        f"/api/v1/clients/{client_id}",
        headers=headers,
        json={"status": "inactive"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "inactive"

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@vertex.com.br",
            "password": "Teste1234",
        },
    )
    assert login.status_code == 200

    deleted = client.delete(
        f"/api/v1/clients/{client_id}",
        headers=headers,
    )
    assert deleted.status_code == 204
