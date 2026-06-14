from fastapi import APIRouter

from app.schemas.documents import DocumentAnswerRequest, DocumentAnswerResponse, DocumentSummaryResponse
from app.services.ai_service import answer_document_question, summarize_document


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/{document_id}/summarize", response_model=DocumentSummaryResponse)
def summarize_document_route(document_id: int) -> DocumentSummaryResponse:
    return summarize_document(document_id)


@router.post("/{document_id}/ask", response_model=DocumentAnswerResponse)
def answer_document_question_route(
    document_id: int,
    payload: DocumentAnswerRequest,
) -> DocumentAnswerResponse:
    return answer_document_question(document_id, payload)

