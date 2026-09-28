from datetime import timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.client import Client
from app.models.project import Project
from app.models.service_order import ServiceOrder, ServiceOrderHistory
from app.models.user import User
from app.schemas.service_order import (
    ServiceOrderCreate,
    ServiceOrderHistoryRead,
    ServiceOrderRead,
    ServiceOrderUpdate,
)

router = APIRouter(
    prefix="/api/v1/service-orders",
    tags=["service-orders"],
    dependencies=[Depends(get_current_user)],
)

REQUIRED_FIELDS = ("client_id", "title", "priority", "status")


def stringify(value) -> str | None:
    if value is None:
        return None
    return str(value)


def ensure_client_exists(client_id: int, db: Session) -> Client:
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


def ensure_project_matches_client(project_id: int | None, client_id: int, db: Session) -> None:
    if project_id is None:
        return
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    if project.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O projeto informado não pertence ao cliente da OS",
        )


def ensure_assigned_user_exists(user_id: int | None, db: Session) -> None:
    if user_id is None:
        return
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=404,
            detail="Usuário responsável não encontrado ou inativo",
        )


def reject_null_required_fields(changes: dict) -> None:
    for field in REQUIRED_FIELDS:
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O campo '{field}' não pode ficar vazio",
            )


@router.get("", response_model=list[ServiceOrderRead])
def list_service_orders(
    q: str | None = Query(default=None, max_length=120),
    client_id: int | None = None,
    project_id: int | None = None,
    assigned_user_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(ServiceOrder)

    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                ServiceOrder.code.ilike(term),
                ServiceOrder.title.ilike(term),
                ServiceOrder.description.ilike(term),
            )
        )
    if client_id is not None:
        query = query.filter(ServiceOrder.client_id == client_id)
    if project_id is not None:
        query = query.filter(ServiceOrder.project_id == project_id)
    if assigned_user_id is not None:
        query = query.filter(ServiceOrder.assigned_user_id == assigned_user_id)
    if status_filter:
        query = query.filter(ServiceOrder.status == status_filter)
    if priority:
        query = query.filter(ServiceOrder.priority == priority)

    return query.order_by(ServiceOrder.id.desc()).all()


@router.post("", response_model=ServiceOrderRead, status_code=status.HTTP_201_CREATED)
def create_service_order(
    payload: ServiceOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_client_exists(payload.client_id, db)
    ensure_project_matches_client(payload.project_id, payload.client_id, db)
    ensure_assigned_user_exists(payload.assigned_user_id, db)

    order = ServiceOrder(
        **payload.model_dump(),
        created_by_user_id=current_user.id,
    )
    db.add(order)
    db.flush()

    order.code = f"OS-{order.id:06d}"
    history = ServiceOrderHistory(
        service_order_id=order.id,
        changed_by_user_id=current_user.id,
        field="status",
        old_value=None,
        new_value=order.status,
        note="OS criada",
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return order


@router.get("/{service_order_id}", response_model=ServiceOrderRead)
def get_service_order(service_order_id: int, db: Session = Depends(get_db)):
    order = db.get(ServiceOrder, service_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    return order


@router.get(
    "/{service_order_id}/history",
    response_model=list[ServiceOrderHistoryRead],
)
def get_service_order_history(service_order_id: int, db: Session = Depends(get_db)):
    if not db.get(ServiceOrder, service_order_id):
        raise HTTPException(status_code=404, detail="OS não encontrada")

    return (
        db.query(ServiceOrderHistory)
        .filter(ServiceOrderHistory.service_order_id == service_order_id)
        .order_by(ServiceOrderHistory.id.asc())
        .all()
    )


@router.patch("/{service_order_id}", response_model=ServiceOrderRead)
def update_service_order(
    service_order_id: int,
    payload: ServiceOrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.get(ServiceOrder, service_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    changes = payload.model_dump(exclude_unset=True)
    note = changes.pop("note", None)
    reject_null_required_fields(changes)

    target_client_id = changes.get("client_id", order.client_id)
    ensure_client_exists(target_client_id, db)

    target_project_id = changes.get("project_id", order.project_id)
    ensure_project_matches_client(target_project_id, target_client_id, db)

    if "assigned_user_id" in changes:
        ensure_assigned_user_exists(changes["assigned_user_id"], db)

    tracked_fields = (
        "client_id",
        "project_id",
        "assigned_user_id",
        "title",
        "priority",
        "status",
        "due_date",
    )

    for field, value in changes.items():
        old_value = getattr(order, field)
        if old_value == value:
            continue

        setattr(order, field, value)

        if field in tracked_fields:
            db.add(
                ServiceOrderHistory(
                    service_order_id=order.id,
                    changed_by_user_id=current_user.id,
                    field=field,
                    old_value=stringify(old_value),
                    new_value=stringify(value),
                    note=note,
                )
            )

    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{service_order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_order(service_order_id: int, db: Session = Depends(get_db)):
    order = db.get(ServiceOrder, service_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    db.query(ServiceOrderHistory).filter(
        ServiceOrderHistory.service_order_id == service_order_id
    ).delete()
    db.delete(order)
    db.commit()
    return None
