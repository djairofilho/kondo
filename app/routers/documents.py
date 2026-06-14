from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_active_membership, require_roles
from app.models import User
from app.schemas.documents import Document as DocumentSchema, DocumentAnswerRequest, DocumentAnswerResponse, DocumentCreate, DocumentSummaryResponse, DocumentUpdate
from app.services.ai_service import answer_document_question, summarize_document
from app.services.content_service import create_document, delete_document, get_document, list_documents, update_document
from app.schemas.attachments import Attachment
from app.services.attachment_service import create_attachment, get_attachment_or_404, list_attachments
from app.services.storage_service import storage_service


router = APIRouter(prefix="/documents", tags=["documents"])
RESIDENT_VISIBLE = {"residents", "public"}


def _can_view_document(db: Session, current_user: User, document) -> bool:
    if current_user.is_platform_admin:
        return True
    support_membership = get_active_membership(db, current_user, "manager", "board_member")
    if support_membership is not None:
        return True
    resident_membership = get_active_membership(db, current_user, "resident")
    return (
        resident_membership is not None
        and resident_membership.condominium_id == document.condominium_id
        and document.visibility in RESIDENT_VISIBLE
    )


def _ensure_document_access(db: Session, current_user: User, document_id: int):
    document = get_document(db, document_id)
    if not _can_view_document(db, current_user, document):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Document access denied")
    return document


def _filter_document_attachments(db: Session, current_user: User, document) -> list[Attachment]:
    attachments = list_attachments(db, "document", document.id)
    if current_user.is_platform_admin or get_active_membership(db, current_user, "manager", "board_member") is not None:
        return attachments
    return [attachment for attachment in attachments if attachment.visibility in RESIDENT_VISIBLE]


@router.get("", response_model=list[DocumentSchema])
def get_documents(
    current_user: User = Depends(require_roles("manager", "board_member", "resident")),
    db: Session = Depends(get_db),
) -> list[DocumentSchema]:
    return [document for document in list_documents(db) if _can_view_document(db, current_user, document)]


@router.post("", response_model=DocumentSchema, dependencies=[Depends(require_roles("manager"))])
def post_document(payload: DocumentCreate, db: Session = Depends(get_db)) -> DocumentSchema:
    return create_document(db, payload)


@router.post("/upload", response_model=Attachment, dependencies=[Depends(require_roles("manager"))])
async def upload_document(
    file: UploadFile = File(...),
    condominium_id: int = Form(1),
    document_id: int = Form(...),
    uploaded_by_user_id: int | None = Form(None),
    visibility: str = Form("managers"),
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> Attachment:
    return await create_attachment(db, file, condominium_id, "document", document_id, current_user.id, visibility)


@router.get("/{document_id}", response_model=DocumentSchema)
def get_document_route(
    document_id: int,
    current_user: User = Depends(require_roles("manager", "board_member", "resident")),
    db: Session = Depends(get_db),
) -> DocumentSchema:
    return _ensure_document_access(db, current_user, document_id)


@router.get("/{document_id}/attachments", response_model=list[Attachment])
def get_document_attachments(
    document_id: int,
    current_user: User = Depends(require_roles("manager", "board_member", "resident")),
    db: Session = Depends(get_db),
) -> list[Attachment]:
    document = _ensure_document_access(db, current_user, document_id)
    return _filter_document_attachments(db, current_user, document)


@router.get("/{document_id}/attachments/{attachment_id}/download")
def download_document_attachment(
    document_id: int,
    attachment_id: int,
    current_user: User = Depends(require_roles("manager", "board_member", "resident")),
    db: Session = Depends(get_db),
) -> FileResponse:
    document = _ensure_document_access(db, current_user, document_id)
    attachment = get_attachment_or_404(db, attachment_id)
    allowed_attachments = _filter_document_attachments(db, current_user, document)
    if attachment.entity_type != "document" or attachment.entity_id != document.id or attachment.id not in {item.id for item in allowed_attachments}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    path = storage_service.get_file_path(attachment.storage_key)
    return FileResponse(path, media_type=attachment.content_type, filename=attachment.original_file_name)


@router.patch("/{document_id}", response_model=DocumentSchema, dependencies=[Depends(require_roles("manager"))])
def patch_document(document_id: int, payload: DocumentUpdate, db: Session = Depends(get_db)) -> DocumentSchema:
    return update_document(db, document_id, payload)


@router.delete("/{document_id}", dependencies=[Depends(require_roles("manager"))])
def remove_document(document_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    delete_document(db, document_id)
    return {"status": "deleted"}


@router.post("/{document_id}/summarize", response_model=DocumentSummaryResponse)
def summarize_document_route(
    document_id: int,
    current_user: User = Depends(require_roles("manager", "board_member", "resident")),
    db: Session = Depends(get_db),
) -> DocumentSummaryResponse:
    _ensure_document_access(db, current_user, document_id)
    return summarize_document(document_id)


@router.post("/{document_id}/ask", response_model=DocumentAnswerResponse)
def answer_document_question_route(
    document_id: int,
    payload: DocumentAnswerRequest,
    current_user: User = Depends(require_roles("manager", "board_member", "resident")),
    db: Session = Depends(get_db),
) -> DocumentAnswerResponse:
    _ensure_document_access(db, current_user, document_id)
    return answer_document_question(document_id, payload)

