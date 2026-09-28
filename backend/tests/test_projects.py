import pytest


@pytest.fixture
def client_id(api, admin_headers):
    created = api.post(
        "/api/v1/clients",
        headers=admin_headers,
        json={"company_name": "Cliente Projeto", "responsible_name": "Pessoa Teste"},
    )
    assert created.status_code == 201, created.text
    return created.json()["id"]


def test_projects_require_authentication(api):
    assert api.get("/api/v1/projects").status_code == 401


def test_project_workflow(api, admin_headers, client_id):
    created = api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={
            "client_id": client_id,
            "name": "Sistema Cliente Teste",
            "project_type": "web",
            "status": "development",
            "priority": "high",
            "progress": 30,
        },
    )
    assert created.status_code == 201, created.text
    project_id = created.json()["id"]

    updated = api.patch(
        f"/api/v1/projects/{project_id}",
        headers=admin_headers,
        json={"progress": 60, "status": "testing"},
    )
    assert updated.status_code == 200
    assert updated.json()["progress"] == 60

    dashboard = api.get("/api/v1/dashboard", headers=admin_headers)
    assert dashboard.status_code == 200
    totals = dashboard.json()["totals"]
    assert totals["users"] == 1
    assert totals["clients"] == 1
    assert totals["projects"] == 1
    assert totals["service_orders"] == 0
    assert totals["open_service_orders"] == 0

    deleted = api.delete(f"/api/v1/projects/{project_id}", headers=admin_headers)
    assert deleted.status_code == 204
    assert api.get(f"/api/v1/projects/{project_id}", headers=admin_headers).status_code == 404


def test_project_requires_existing_client(api, admin_headers):
    response = api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"client_id": 999, "name": "Projeto Órfão"},
    )
    assert response.status_code == 404


def test_project_filters(api, admin_headers, client_id):
    api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"client_id": client_id, "name": "Portal Horizonte", "status": "planning"},
    )
    api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"client_id": client_id, "name": "App AutoCar", "status": "development"},
    )

    by_term = api.get("/api/v1/projects", headers=admin_headers, params={"q": "portal"})
    assert [item["name"] for item in by_term.json()] == ["Portal Horizonte"]

    by_status = api.get(
        "/api/v1/projects", headers=admin_headers, params={"status": "development"}
    )
    assert [item["name"] for item in by_status.json()] == ["App AutoCar"]

    by_client = api.get(
        "/api/v1/projects", headers=admin_headers, params={"client_id": client_id}
    )
    assert len(by_client.json()) == 2


def test_progress_out_of_range_is_rejected(api, admin_headers, client_id):
    response = api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"client_id": client_id, "name": "Projeto Inválido", "progress": 150},
    )
    assert response.status_code == 422


def test_update_cannot_clear_client(api, admin_headers, client_id):
    created = api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"client_id": client_id, "name": "Projeto Base"},
    )
    project_id = created.json()["id"]

    response = api.patch(
        f"/api/v1/projects/{project_id}",
        headers=admin_headers,
        json={"client_id": None},
    )
    assert response.status_code == 422, response.text
