from datetime import datetime

from pydantic import BaseModel, Field


class TicketAIClassification(BaseModel):
    category: str
    priority: str
    risk: str
    suggested_owner: str
    next_action: str


class TicketCreate(BaseModel):
    unit_id: int
    title: str = Field(min_length=3)
    description: str = Field(min_length=5)
    location: str = Field(min_length=2)


class Ticket(TicketCreate):
    id: int
    status: str
    category: str | None = None
    priority: str | None = None
    ai_analysis: TicketAIClassification | None = None
    created_at: datetime

