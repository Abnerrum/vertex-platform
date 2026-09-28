from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vertex Platform API",
    version="0.1.0",
    description="API inicial da Vertex Tech Solutions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "Vertex Platform API", "version": "0.1.0", "status": "development"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/dashboard")
def dashboard():
    return {
        "clients": 3,
        "projects": 3,
        "open_orders": 4,
        "phase": "MVP - Fase 1"
    }
