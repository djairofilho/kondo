from pydantic import BaseModel, Field


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

