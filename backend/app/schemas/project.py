from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    client_id: int
    name: str = Field(min_length=2, max_length=180)
    description: str | None = None
    project_type: str = "web"
    status: str = "planning"
    priority: str = "medium"
    progress: int = Field(default=0, ge=0, le=100)
    start_date: date | None = None
    due_date: date | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    client_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = None
    project_type: str | None = None
    status: str | None = None
    priority: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    start_date: date | None = None
    due_date: date | None = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
