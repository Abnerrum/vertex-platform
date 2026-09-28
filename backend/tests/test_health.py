def test_root(api):
    response = api.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Vertex Platform API"


def test_health(api):
    response = api.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_requires_authentication(api):
    assert api.get("/api/v1/dashboard").status_code == 401
