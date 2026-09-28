from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

class ClientBase(BaseModel):
    company_name: str
    responsible_name: str
    email: EmailStr | None = None
    phone: str | None = None
    document: str | None = None
    notes: str | None = None
    status: str = "active"

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    company_name: str | None = None
    responsible_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    document: str | None = None
    notes: str | None = None
    status: str | None = None

class ClientRead(ClientBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
