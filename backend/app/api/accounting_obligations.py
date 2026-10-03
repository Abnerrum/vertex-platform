from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.accounting_obligation import AccountingObligation
from app.models.client import Client
from app.schemas.accounting_obligation import (
    AccountingObligationCreate,
    AccountingObligationRead,
    AccountingObligationUpdate,
)

router = APIRouter(
    prefix="/api/v1/accounting-obligations",
    tags=["accounting-obligations"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[AccountingObligationRead])
def list_obligations(
    client_id: int | None = None,
    competence: str | None = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    department: str | None = Query(
        default=None,
        pattern=r"^(fiscal|payroll|accounting|corporate|other)$",
    ),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        pattern=r"^(pending|in_progress|waiting|completed)$",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingObligation)
    if client_id is not None:
        query = query.filter(AccountingObligation.client_id == client_id)
    if competence:
        query = query.filter(AccountingObligation.competence == competence)
    if department:
        query = query.filter(AccountingObligation.department == department)
    if status_filter:
        query = query.filter(AccountingObligation.status == status_filter)
    return query.order_by(AccountingObligation.due_date, AccountingObligation.id).all()


@router.post("", response_model=AccountingObligationRead, status_code=201)
def create_obligation(
    payload: AccountingObligationCreate,
    db: Session = Depends(get_db),
):
    if not db.get(Client, payload.client_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    obligation = AccountingObligation(**payload.model_dump())
    db.add(obligation)
    db.commit()
    db.refresh(obligation)
    return obligation


@router.patch("/{obligation_id}", response_model=AccountingObligationRead)
def update_obligation(
    obligation_id: int,
    payload: AccountingObligationUpdate,
    db: Session = Depends(get_db),
):
    obligation = db.get(AccountingObligation, obligation_id)
    if not obligation:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if value is None and field != "notes":
            raise HTTPException(status_code=422, detail=f"O campo '{field}' não pode ficar vazio")
        setattr(obligation, field, value)
    obligation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(obligation)
    return obligation