from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(
    prefix="/api/v1/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_user)],
)

REQUIRED_FIELDS = ("company_name", "responsible_name", "status")


def reject_null_required_fields(changes: dict) -> None:
    for field in REQUIRED_FIELDS:
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O campo '{field}' não pode ficar vazio",
            )

@router.get("", response_model=list[ClientRead])
def list_clients(
    q: str | None = Query(default=None, max_length=120),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(Client)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Client.company_name.ilike(term),
                Client.responsible_name.ilike(term),
            )
        )
    if status_filter:
        query = query.filter(Client.status == status_filter)
    return query.order_by(Client.id.desc()).all()

@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    client = Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client

@router.patch("/{client_id}", response_model=ClientRead)
def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db)):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    changes = payload.model_dump(exclude_unset=True)
    reject_null_required_fields(changes)

    for field, value in changes.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(client)
    db.commit()
    return None
