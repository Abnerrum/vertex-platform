def test_bootstrap_login_and_client_crud(api, admin_headers, admin_credentials):
    me = api.get("/api/v1/auth/me", headers=admin_headers)
    assert me.status_code == 200
    assert me.json()["role"] == "admin"

    denied = api.get("/api/v1/clients")
    assert denied.status_code == 401

    created = api.post(
        "/api/v1/clients",
        headers=admin_headers,
        json={
            "company_name": "Cliente Teste",
            "responsible_name": "Pessoa Teste",
            "email": "cliente@example.com",
        },
    )
    assert created.status_code == 201, created.text
    client_id = created.json()["id"]

    updated = api.patch(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers,
        json={"status": "inactive"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "inactive"

    login = api.post(
        "/api/v1/auth/login",
        json={
            "email": admin_credentials["email"],
            "password": admin_credentials["password"],
        },
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == admin_credentials["email"]

    deleted = api.delete(f"/api/v1/clients/{client_id}", headers=admin_headers)
    assert deleted.status_code == 204


def test_bootstrap_runs_only_once(api, admin_headers, admin_credentials):
    again = api.post("/api/v1/auth/bootstrap", json=admin_credentials)
    assert again.status_code == 409


def test_login_with_wrong_password(api, admin_headers, admin_credentials):
    response = api.post(
        "/api/v1/auth/login",
        json={"email": admin_credentials["email"], "password": "senha-errada"},
    )
    assert response.status_code == 401


def test_invalid_token_is_rejected(api, admin_headers):
    response = api.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert response.status_code == 401


def test_only_admin_manages_users(api, admin_headers):
    created = api.post(
        "/api/v1/auth/users",
        headers=admin_headers,
        json={
            "name": "Comercial",
            "email": "comercial@vertex.com.br",
            "password": "Teste1234",
            "role": "commercial",
        },
    )
    assert created.status_code == 201, created.text

    duplicated = api.post(
        "/api/v1/auth/users",
        headers=admin_headers,
        json={
            "name": "Comercial",
            "email": "comercial@vertex.com.br",
            "password": "Teste1234",
            "role": "commercial",
        },
    )
    assert duplicated.status_code == 409

    login = api.post(
        "/api/v1/auth/login",
        json={"email": "comercial@vertex.com.br", "password": "Teste1234"},
    )
    commercial_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert api.get("/api/v1/auth/users", headers=commercial_headers).status_code == 403
    assert api.get("/api/v1/auth/users", headers=admin_headers).status_code == 200
