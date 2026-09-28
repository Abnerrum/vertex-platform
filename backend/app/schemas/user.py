from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["admin", "commercial", "technical", "finance"]

class BootstrapAdmin(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserCreate(BootstrapAdmin):
    role: UserRole = "commercial"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
