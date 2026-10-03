from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Department = Literal["fiscal", "payroll", "accounting", "corporate", "other"]
ObligationStatus = Literal["pending", "in_progress", "waiting", "completed"]


class AccountingObligationCreate(BaseModel):
    client_id: int
    title: str = Field(min_length=1, max_length=180)
    department: Department
    competence: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    due_date: date
    status: ObligationStatus = "pending"
    notes: str | None = None


class AccountingObligationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    department: Department | None = None
    competence: str | None = Field(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    due_date: date | None = None
    status: ObligationStatus | None = None
    notes: str | None = None


class AccountingObligationRead(AccountingObligationCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)