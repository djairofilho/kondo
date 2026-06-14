from datetime import datetime

from pydantic import BaseModel, Field


class CalendarEventCreate(BaseModel):
    condominium_id: int = 1
    unit_id: int | None = None
    title: str = Field(min_length=3)
    description: str | None = None
    category: str = "event"
    start_at: datetime
    end_at: datetime | None = None
    location: str | None = None
    visibility: str = "residents"
    source_type: str | None = None
    source_id: int | None = None
    status: str = "scheduled"


class CalendarEventUpdate(BaseModel):
    unit_id: int | None = None
    title: str | None = Field(default=None, min_length=3)
    description: str | None = None
    category: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None
    visibility: str | None = None
    source_type: str | None = None
    source_id: int | None = None
    status: str | None = None


class CalendarEvent(CalendarEventCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
