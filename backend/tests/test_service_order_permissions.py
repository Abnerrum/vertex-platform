def test_only_admin_can_delete_service_orders(api, admin_headers):
    client = api.post(
        "/api/v1/clients",
        headers=admin_headers,
        json={"company_name": "Cliente segurança", "responsible_name": "Responsável"},
    )
    assert client.status_code == 201, client.text
    created = api.post(
        "/api/v1/service-orders",
        headers=admin_headers,
        json={"client_id": client.json()["id"], "title": "OS protegida"},
    )
    assert created.status_code == 201, created.text
    order_id = created.json()["id"]

    user = api.post(
        "/api/v1/auth/users",
        headers=admin_headers,
        json={
            "name": "Técnico",
            "email": "tecnico-seguranca@vertex.com.br",
            "password": "Teste1234",
            "role": "technical",
        },
    )
    assert user.status_code == 201, user.text
    login = api.post(
        "/api/v1/auth/login",
        json={"email": "tecnico-seguranca@vertex.com.br", "password": "Teste1234"},
    )
    assert login.status_code == 200, login.text
    technician_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert api.delete(f"/api/v1/service-orders/{order_id}").status_code == 401
    assert api.delete(
        f"/api/v1/service-orders/{order_id}", headers=technician_headers
    ).status_code == 403
    assert api.get(
        f"/api/v1/service-orders/{order_id}", headers=technician_headers
    ).status_code == 200
    assert api.delete(
        f"/api/v1/service-orders/{order_id}", headers=admin_headers
    ).status_code == 204
    assert api.get(
        f"/api/v1/service-orders/{order_id}", headers=admin_headers
    ).status_code == 404
