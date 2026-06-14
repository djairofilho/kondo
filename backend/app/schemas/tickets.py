from datetime import datetime

from pydantic import BaseModel, Field


class TicketAIClassification(BaseModel):
    category: str
    priority: str
    risk: str
    suggested_owner: str
    next_action: str


class TicketCreate(BaseModel):
    condominium_id: int = 1
    unit_id: int
    title: str = Field(min_length=3)
    description: str = Field(min_length=5)
    location: str = Field(min_length=2)


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    status: str | None = None
    category: str | None = None
    priority: str | None = None


class TicketStatusUpdate(BaseModel):
    status: str


class TicketAssign(BaseModel):
    assigned_to_user_id: int | None = None


class TicketCommentCreate(BaseModel):
    author_user_id: int | None = None
    body: str = Field(min_length=1)
    visibility: str = "managers"


class TicketComment(BaseModel):
    id: int
    ticket_id: int
    author_user_id: int | None
    body: str
    visibility: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Ticket(TicketCreate):
    id: int
    status: str
    category: str | None = None
    priority: str | None = None
    ai_analysis: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

