from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_list_client():
    payload = {
        "company_name": "Cliente Teste",
        "responsible_name": "Responsável Teste",
        "email": "teste@example.com"
    }
    created = client.post("/api/v1/clients", json=payload)
    assert created.status_code == 201
    assert created.json()["company_name"] == "Cliente Teste"
    listed = client.get("/api/v1/clients")
    assert listed.status_code == 200
    assert any(item["company_name"] == "Cliente Teste" for item in listed.json())
