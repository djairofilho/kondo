from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models import User
from app.schemas.attachments import Attachment
from app.services.attachment_service import create_attachment, delete_attachment, get_attachment_or_404, list_attachments
from app.services.storage_service import storage_service


router = APIRouter(tags=["attachments"], dependencies=[Depends(require_roles("manager", "board_member"))])


@router.post("/attachments", response_model=Attachment, dependencies=[Depends(require_roles("manager"))])
async def post_attachment(
    file: UploadFile = File(...),
    condominium_id: int = Form(1),
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    uploaded_by_user_id: int | None = Form(None),
    visibility: str = Form("private"),
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> Attachment:
    return await create_attachment(db, file, condominium_id, entity_type, entity_id, current_user.id, visibility)


@router.get("/attachments/{attachment_id}", response_model=Attachment)
def get_attachment(attachment_id: int, db: Session = Depends(get_db)) -> Attachment:
    return get_attachment_or_404(db, attachment_id)


@router.get("/attachments/{attachment_id}/download")
def download_attachment(attachment_id: int, db: Session = Depends(get_db)) -> FileResponse:
    attachment = get_attachment_or_404(db, attachment_id)
    path = storage_service.get_file_path(attachment.storage_key)
    return FileResponse(path, media_type=attachment.content_type, filename=attachment.original_file_name)


@router.delete("/attachments/{attachment_id}", dependencies=[Depends(require_roles("manager"))])
def remove_attachment(attachment_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    delete_attachment(db, attachment_id)
    return {"status": "deleted"}


@router.post("/tickets/{ticket_id}/attachments", response_model=Attachment, dependencies=[Depends(require_roles("manager"))])
async def post_ticket_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    condominium_id: int = Form(1),
    uploaded_by_user_id: int | None = Form(None),
    visibility: str = Form("residents"),
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> Attachment:
    return await create_attachment(db, file, condominium_id, "ticket", ticket_id, current_user.id, visibility)


@router.get("/tickets/{ticket_id}/attachments", response_model=list[Attachment])
def get_ticket_attachments(ticket_id: int, db: Session = Depends(get_db)) -> list[Attachment]:
    return list_attachments(db, "ticket", ticket_id)


@router.post("/payments/{payment_id}/attachments", response_model=Attachment, dependencies=[Depends(require_roles("manager"))])
async def post_payment_attachment(
    payment_id: int,
    file: UploadFile = File(...),
    condominium_id: int = Form(1),
    uploaded_by_user_id: int | None = Form(None),
    visibility: str = Form("private"),
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> Attachment:
    return await create_attachment(db, file, condominium_id, "payment", payment_id, current_user.id, visibility)


@router.get("/payments/{payment_id}/attachments", response_model=list[Attachment])
def get_payment_attachments(payment_id: int, db: Session = Depends(get_db)) -> list[Attachment]:
    return list_attachments(db, "payment", payment_id)


@router.post("/kanban/items/{item_id}/attachments", response_model=Attachment, dependencies=[Depends(require_roles("manager"))])
async def post_kanban_attachment(
    item_id: int,
    file: UploadFile = File(...),
    condominium_id: int = Form(1),
    uploaded_by_user_id: int | None = Form(None),
    visibility: str = Form("managers"),
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> Attachment:
    return await create_attachment(db, file, condominium_id, "work_item", item_id, current_user.id, visibility)


@router.get("/kanban/items/{item_id}/attachments", response_model=list[Attachment])
def get_kanban_attachments(item_id: int, db: Session = Depends(get_db)) -> list[Attachment]:
    return list_attachments(db, "work_item", item_id)

