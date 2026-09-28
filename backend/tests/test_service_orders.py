import pytest


@pytest.fixture
def base_data(api, admin_headers):
    client = api.post(
        "/api/v1/clients",
        headers=admin_headers,
        json={"company_name": "Cliente OS", "responsible_name": "Responsável"},
    )
    assert client.status_code == 201, client.text
    client_id = client.json()["id"]

    project = api.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"client_id": client_id, "name": "Projeto da OS"},
    )
    assert project.status_code == 201, project.text

    return {
        "client_id": client_id,
        "project_id": project.json()["id"],
    }


def test_service_orders_require_authentication(api):
    assert api.get("/api/v1/service-orders").status_code == 401


def test_service_order_workflow_and_history(api, admin_headers, base_data):
    created = api.post(
        "/api/v1/service-orders",
        headers=admin_headers,
        json={
            "client_id": base_data["client_id"],
            "project_id": base_data["project_id"],
            "assigned_user_id": 1,
            "title": "Ajustar dashboard",
            "description": "Corrigir os indicadores do cliente",
            "priority": "high",
            "status": "open",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["code"] == "OS-000001"
    service_order_id = body["id"]

    history = api.get(
        f"/api/v1/service-orders/{service_order_id}/history",
        headers=admin_headers,
    )
    assert history.status_code == 200
    assert history.json()[0]["new_value"] == "open"

    updated = api.patch(
        f"/api/v1/service-orders/{service_order_id}",
        headers=admin_headers,
        json={
            "status": "in_progress",
            "priority": "urgent",
            "note": "Cliente solicitou urgência",
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "in_progress"
    assert updated.json()["priority"] == "urgent"

    history = api.get(
        f"/api/v1/service-orders/{service_order_id}/history",
        headers=admin_headers,
    )
    assert history.status_code == 200
    fields = [item["field"] for item in history.json()]
    assert fields == ["status", "priority", "status"]
    assert history.json()[-1]["note"] == "Cliente solicitou urgência"

    dashboard = api.get("/api/v1/dashboard", headers=admin_headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["totals"]["service_orders"] == 1
    assert dashboard.json()["totals"]["open_service_orders"] == 1

    completed = api.patch(
        f"/api/v1/service-orders/{service_order_id}",
        headers=admin_headers,
        json={"status": "completed"},
    )
    assert completed.status_code == 200

    dashboard = api.get("/api/v1/dashboard", headers=admin_headers)
    assert dashboard.json()["totals"]["open_service_orders"] == 0


def test_service_order_filters(api, admin_headers, base_data):
    api.post(
        "/api/v1/service-orders",
        headers=admin_headers,
        json={
            "client_id": base_data["client_id"],
            "title": "OS urgente",
            "priority": "urgent",
            "status": "waiting",
        },
    )
    api.post(
        "/api/v1/service-orders",
        headers=admin_headers,
        json={
            "client_id": base_data["client_id"],
            "title": "OS normal",
            "priority": "medium",
            "status": "open",
        },
    )

    by_status = api.get(
        "/api/v1/service-orders",
        headers=admin_headers,
        params={"status": "waiting"},
    )
    assert [item["title"] for item in by_status.json()] == ["OS urgente"]

    by_priority = api.get(
        "/api/v1/service-orders",
        headers=admin_headers,
        params={"priority": "medium"},
    )
    assert [item["title"] for item in by_priority.json()] == ["OS normal"]


def test_service_order_rejects_project_from_another_client(api, admin_headers, base_data):
    other_client = api.post(
        "/api/v1/clients",
        headers=admin_headers,
        json={"company_name": "Outro cliente", "responsible_name": "Outra pessoa"},
    )
    assert other_client.status_code == 201

    response = api.post(
        "/api/v1/service-orders",
        headers=admin_headers,
        json={
            "client_id": other_client.json()["id"],
            "project_id": base_data["project_id"],
            "title": "OS inválida",
        },
    )
    assert response.status_code == 422


def test_service_order_required_fields_cannot_be_cleared(api, admin_headers, base_data):
    created = api.post(
        "/api/v1/service-orders",
        headers=admin_headers,
        json={
            "client_id": base_data["client_id"],
            "title": "OS base",
        },
    )
    service_order_id = created.json()["id"]

    response = api.patch(
        f"/api/v1/service-orders/{service_order_id}",
        headers=admin_headers,
        json={"title": None},
    )
    assert response.status_code == 422
