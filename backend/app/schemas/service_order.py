from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ServiceOrderStatus = Literal[
    "open",
    "assigned",
    "in_progress",
    "waiting",
    "completed",
    "cancelled",
]
ServiceOrderPriority = Literal["low", "medium", "high", "urgent"]


class ServiceOrderBase(BaseModel):
    client_id: int
    project_id: int | None = None
    assigned_user_id: int | None = None
    title: str = Field(min_length=2, max_length=180)
    description: str | None = None
    priority: ServiceOrderPriority = "medium"
    status: ServiceOrderStatus = "open"
    due_date: date | None = None


class ServiceOrderCreate(ServiceOrderBase):
    pass


class ServiceOrderUpdate(BaseModel):
    client_id: int | None = None
    project_id: int | None = None
    assigned_user_id: int | None = None
    title: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = None
    priority: ServiceOrderPriority | None = None
    status: ServiceOrderStatus | None = None
    due_date: date | None = None
    note: str | None = Field(default=None, max_length=500)


class ServiceOrderRead(ServiceOrderBase):
    id: int
    code: str
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ServiceOrderHistoryRead(BaseModel):
    id: int
    service_order_id: int
    changed_by_user_id: int
    field: str
    old_value: str | None
    new_value: str | None
    note: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
