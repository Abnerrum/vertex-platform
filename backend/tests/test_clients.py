NEW_CLIENT = {
    "company_name": "Cliente Teste",
    "responsible_name": "Responsável Teste",
    "email": "teste@example.com",
}


def test_clients_require_authentication(api):
    assert api.get("/api/v1/clients").status_code == 401
    assert api.post("/api/v1/clients", json=NEW_CLIENT).status_code == 401


def test_create_and_list_client(api, admin_headers):
    created = api.post("/api/v1/clients", headers=admin_headers, json=NEW_CLIENT)
    assert created.status_code == 201, created.text
    assert created.json()["company_name"] == "Cliente Teste"

    listed = api.get("/api/v1/clients", headers=admin_headers)
    assert listed.status_code == 200
    assert any(item["company_name"] == "Cliente Teste" for item in listed.json())


def test_filter_clients_by_term_and_status(api, admin_headers):
    api.post("/api/v1/clients", headers=admin_headers, json=NEW_CLIENT)
    api.post(
        "/api/v1/clients",
        headers=admin_headers,
        json={
            "company_name": "Loja Horizonte",
            "responsible_name": "Mariana",
            "status": "inactive",
        },
    )

    by_term = api.get("/api/v1/clients", headers=admin_headers, params={"q": "horizonte"})
    assert [item["company_name"] for item in by_term.json()] == ["Loja Horizonte"]

    by_status = api.get("/api/v1/clients", headers=admin_headers, params={"status": "active"})
    assert [item["company_name"] for item in by_status.json()] == ["Cliente Teste"]


def test_client_not_found(api, admin_headers):
    assert api.get("/api/v1/clients/999", headers=admin_headers).status_code == 404
    assert api.delete("/api/v1/clients/999", headers=admin_headers).status_code == 404


def test_update_cannot_clear_required_field(api, admin_headers):
    created = api.post("/api/v1/clients", headers=admin_headers, json=NEW_CLIENT)
    client_id = created.json()["id"]

    rejected = api.patch(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers,
        json={"company_name": None},
    )
    assert rejected.status_code == 422, rejected.text

    cleared = api.patch(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers,
        json={"phone": None},
    )
    assert cleared.status_code == 200
    assert cleared.json()["phone"] is None
