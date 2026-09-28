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

class ClientRead(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
