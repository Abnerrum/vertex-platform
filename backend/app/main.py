from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import get_current_user, router as auth_router
from app.api.clients import router as clients_router
from app.database.session import Base, engine
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vertex Platform API",
    version="0.3.0",
    description="API de gestão da Vertex Tech Solutions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(clients_router)

@app.get("/")
def root():
    return {"name": "Vertex Platform API", "version": "0.3.0", "status": "development"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/dashboard")
def dashboard(_=Depends(get_current_user)):
    return {
        "phase": "MVP - Fase 1",
        "version": "0.3.0",
        "authentication": "enabled",
    }
