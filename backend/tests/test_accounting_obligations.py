from datetime import date, timedelta


def create_client(api, headers):
    response = api.post(
        "/api/v1/clients",
        headers=headers,
        json={"company_name": "Escritório Cliente", "responsible_name": "Ana"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_obligations_require_authentication(api):
    assert api.get("/api/v1/accounting-obligations").status_code == 401


def test_create_filter_and_complete_obligation(api, admin_headers):
    client_id = create_client(api, admin_headers)
    created = api.post(
        "/api/v1/accounting-obligations",
        headers=admin_headers,
        json={
            "client_id": client_id,
            "title": "Apuração de impostos",
            "department": "fiscal",
            "competence": "2026-08",
            "due_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    assert created.status_code == 201, created.text
    obligation_id = created.json()["id"]

    filtered = api.get(
        "/api/v1/accounting-obligations",
        headers=admin_headers,
        params={"competence": "2026-08", "department": "fiscal", "status": "pending"},
    )
    assert [item["id"] for item in filtered.json()] == [obligation_id]

    dashboard = api.get("/api/v1/dashboard", headers=admin_headers).json()["totals"]
    assert dashboard["open_obligations"] == 1
    assert dashboard["overdue_obligations"] == 1

    updated = api.patch(
        f"/api/v1/accounting-obligations/{obligation_id}",
        headers=admin_headers,
        json={"status": "completed"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["status"] == "completed"
    assert updated.json()["updated_at"] >= created.json()["updated_at"]
    dashboard = api.get("/api/v1/dashboard", headers=admin_headers).json()["totals"]
    assert dashboard["open_obligations"] == 0
    assert dashboard["overdue_obligations"] == 0


def test_obligation_validates_client_department_and_competence(api, admin_headers):
    payload = {
        "client_id": 999,
        "title": "Fechamento da folha",
        "department": "payroll",
        "competence": "2026-09",
        "due_date": "2026-10-05",
    }
    assert api.post("/api/v1/accounting-obligations", headers=admin_headers, json=payload).status_code == 404

    client_id = create_client(api, admin_headers)
    payload["client_id"] = client_id
    payload["department"] = "unknown"
    assert api.post("/api/v1/accounting-obligations", headers=admin_headers, json=payload).status_code == 422
    payload["department"] = "payroll"
    payload["competence"] = "2026-13"
    assert api.post("/api/v1/accounting-obligations", headers=admin_headers, json=payload).status_code == 422