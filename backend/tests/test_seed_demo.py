from app.database.session import SessionLocal
from app.seed_demo import seed_demo


def test_seed_demo_creates_sample_data_once(api, admin_headers):
    db = SessionLocal()
    try:
        first_run = seed_demo(db)
        second_run = seed_demo(db)
    finally:
        db.close()

    assert first_run == {
        "clients": 15,
        "projects": 8,
        "service_orders": 5,
        "audit_events": 11,
    }
    assert second_run == {
        "clients": 0,
        "projects": 0,
        "service_orders": 0,
        "audit_events": 0,
    }

    dashboard = api.get("/api/v1/dashboard", headers=admin_headers).json()["totals"]
    assert dashboard["clients"] == 15
    assert dashboard["active_projects"] == 8
    assert dashboard["open_service_orders"] == 5
    assert dashboard["audit_events"] == 11