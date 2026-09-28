from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.client import Client
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)],
)


REQUIRED_FIELDS = (
    "client_id",
    "name",
    "project_type",
    "status",
    "priority",
    "progress",
)


def ensure_client_exists(client_id: int, db: Session) -> None:
    if not db.get(Client, client_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")


def reject_null_required_fields(changes: dict) -> None:
    for field in REQUIRED_FIELDS:
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O campo '{field}' não pode ficar vazio",
            )


@router.get("", response_model=list[ProjectRead])
def list_projects(
    q: str | None = Query(default=None, max_length=120),
    client_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(Project)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Project.name.ilike(term),
                Project.description.ilike(term),
            )
        )
    if client_id is not None:
        query = query.filter(Project.client_id == client_id)
    if status_filter:
        query = query.filter(Project.status == status_filter)
    return query.order_by(Project.id.desc()).all()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    ensure_client_exists(payload.client_id, db)
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    changes = payload.model_dump(exclude_unset=True)
    reject_null_required_fields(changes)
    if "client_id" in changes:
        ensure_client_exists(changes["client_id"], db)

    for field, value in changes.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    db.delete(project)
    db.commit()
    return None
