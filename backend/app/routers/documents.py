from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.documents import Document, DocumentAnswerRequest, DocumentAnswerResponse, DocumentCreate, DocumentSummaryResponse, DocumentUpdate
from app.services.ai_service import answer_document_question, summarize_document
from app.services.content_service import create_document, delete_document, get_document, list_documents, update_document
from app.schemas.attachments import Attachment
from app.services.attachment_service import create_attachment


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[Document])
def get_documents(db: Session = Depends(get_db)) -> list[Document]:
    return list_documents(db)


@router.post("", response_model=Document)
def post_document(payload: DocumentCreate, db: Session = Depends(get_db)) -> Document:
    return create_document(db, payload)


@router.post("/upload", response_model=Attachment)
async def upload_document(
    file: UploadFile = File(...),
    condominium_id: int = Form(1),
    document_id: int = Form(...),
    uploaded_by_user_id: int | None = Form(None),
    visibility: str = Form("managers"),
    db: Session = Depends(get_db),
) -> Attachment:
    return await create_attachment(db, file, condominium_id, "document", document_id, uploaded_by_user_id, visibility)


@router.get("/{document_id}", response_model=Document)
def get_document_route(document_id: int, db: Session = Depends(get_db)) -> Document:
    return get_document(db, document_id)


@router.patch("/{document_id}", response_model=Document)
def patch_document(document_id: int, payload: DocumentUpdate, db: Session = Depends(get_db)) -> Document:
    return update_document(db, document_id, payload)


@router.delete("/{document_id}")
def remove_document(document_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    delete_document(db, document_id)
    return {"status": "deleted"}


@router.post("/{document_id}/summarize", response_model=DocumentSummaryResponse)
def summarize_document_route(document_id: int) -> DocumentSummaryResponse:
    return summarize_document(document_id)


@router.post("/{document_id}/ask", response_model=DocumentAnswerResponse)
def answer_document_question_route(
    document_id: int,
    payload: DocumentAnswerRequest,
) -> DocumentAnswerResponse:
    return answer_document_question(document_id, payload)

