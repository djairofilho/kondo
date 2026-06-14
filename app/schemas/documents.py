from pydantic import BaseModel, Field
from datetime import datetime


class DocumentCreate(BaseModel):
    condominium_id: int = 1
    title: str = Field(min_length=2)
    document_type: str
    content: str | None = None
    summary: str | None = None
    visibility: str = "managers"


class DocumentUpdate(BaseModel):
    title: str | None = None
    document_type: str | None = None
    content: str | None = None
    summary: str | None = None
    visibility: str | None = None


class Document(DocumentCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentSummaryResponse(BaseModel):
    document_id: int
    title: str
    summary: str


class DocumentAnswerRequest(BaseModel):
    question: str = Field(min_length=3)


class DocumentAnswerResponse(BaseModel):
    document_id: int
    question: str
    answer: str

