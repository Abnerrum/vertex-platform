from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import __version__
from app.api.accounting_obligations import router as accounting_obligations_router
from app.api.auth import get_current_user, router as auth_router
from app.api.clients import router as clients_router
from app.api.projects import router as projects_router
from app.api.service_orders import router as service_orders_router
from app.database.session import Base, engine, get_db
from app.models.accounting_obligation import AccountingObligation
from app.models.client import Client
from app.models.project import Project
from app.models.service_order import ServiceOrder, ServiceOrderHistory
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vertex Platform API",
    version=__version__,
    description="API do Vertex Core — base de operações da Vertex Tech Solutions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(accounting_obligations_router)
app.include_router(clients_router)
app.include_router(projects_router)
app.include_router(service_orders_router)


@app.get("/")
def root():
    return {
        "name": "Vertex Platform API",
        "version": __version__,
        "status": "development",
        "demo": "/app/",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/dashboard")
def dashboard(
    _=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "module": "Vertex Core",
        "phase": "MVP - Fase 1",
        "version": __version__,
        "authentication": "enabled",
        "totals": {
            "users": db.query(User).count(),
            "clients": db.query(Client).count(),
            "projects": db.query(Project).count(),
            "active_projects": db.query(Project)
            .filter(Project.status.notin_(["completed", "cancelled"]))
            .count(),
            "service_orders": db.query(ServiceOrder).count(),
            "open_service_orders": db.query(ServiceOrder)
            .filter(ServiceOrder.status.notin_(["completed", "cancelled"]))
            .count(),
            "audit_events": db.query(ServiceOrderHistory).count(),
            "open_obligations": db.query(AccountingObligation)
            .filter(AccountingObligation.status != "completed")
            .count(),
            "overdue_obligations": db.query(AccountingObligation)
            .filter(
                AccountingObligation.status != "completed",
                AccountingObligation.due_date < date.today(),
            )
            .count(),
        },
    }


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "docs"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
