from datetime import date, datetime

from pydantic import BaseModel, Field


class KanbanColumn(BaseModel):
    id: str
    title: str
    order: int


class WorkItemCreate(BaseModel):
    condominium_id: int = 1
    ticket_id: int | None = None
    type: str = "ticket"
    title: str = Field(min_length=3)
    description: str | None = None
    status: str = "received"
    priority: str = "medium"
    due_date: date | None = None
    source_type: str | None = None
    source_id: int | None = None


class WorkItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: date | None = None


class WorkItemMove(BaseModel):
    status: str


class WorkItem(BaseModel):
    id: int
    condominium_id: int
    ticket_id: int | None
    type: str
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date | None
    source_type: str | None
    source_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}

