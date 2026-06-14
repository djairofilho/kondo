from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models import Attachment
from app.services.storage_service import storage_service


async def create_attachment(
    db: Session,
    file: UploadFile,
    condominium_id: int,
    entity_type: str,
    entity_id: int,
    uploaded_by_user_id: int | None = None,
    visibility: str = "private",
) -> Attachment:
    stored_file_name, storage_key, file_size = await storage_service.save_file(file, entity_type)
    attachment = Attachment(
        condominium_id=condominium_id,
        entity_type=entity_type,
        entity_id=entity_id,
        uploaded_by_user_id=uploaded_by_user_id,
        original_file_name=file.filename or stored_file_name,
        stored_file_name=stored_file_name,
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        storage_key=storage_key,
        storage_provider="local",
        visibility=visibility,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def get_attachment_or_404(db: Session, attachment_id: int) -> Attachment:
    attachment = db.get(Attachment, attachment_id)
    if attachment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return attachment


def list_attachments(db: Session, entity_type: str, entity_id: int) -> list[Attachment]:
    return (
        db.query(Attachment)
        .filter(Attachment.entity_type == entity_type, Attachment.entity_id == entity_id)
        .order_by(Attachment.created_at.desc())
        .all()
    )


def delete_attachment(db: Session, attachment_id: int) -> None:
    attachment = get_attachment_or_404(db, attachment_id)
    storage_service.delete_file(attachment.storage_key)
    db.delete(attachment)
    db.commit()

