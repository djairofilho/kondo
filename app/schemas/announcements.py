from pydantic import BaseModel, Field
from datetime import datetime


class AnnouncementCreate(BaseModel):
    condominium_id: int = 1
    title: str = Field(min_length=2)
    body: str = Field(min_length=3)
    audience: str = "residents"
    status: str = "draft"


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    audience: str | None = None
    status: str | None = None


class Announcement(AnnouncementCreate):
    id: int
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnnouncementGenerationRequest(BaseModel):
    draft: str = Field(min_length=3)
    tone: str = "formal"


class AnnouncementGenerationResponse(BaseModel):
    title: str
    body: str
    tone: str

