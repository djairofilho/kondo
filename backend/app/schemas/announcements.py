from pydantic import BaseModel, Field


class AnnouncementGenerationRequest(BaseModel):
    draft: str = Field(min_length=3)
    tone: str = "formal"


class AnnouncementGenerationResponse(BaseModel):
    title: str
    body: str
    tone: str

