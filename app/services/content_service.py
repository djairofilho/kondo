from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Announcement, Document
from app.schemas.announcements import AnnouncementCreate, AnnouncementUpdate
from app.schemas.documents import DocumentCreate, DocumentUpdate


def _get_or_404(db: Session, model, entity_id: int):
    entity = db.get(model, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return entity


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def create_document(db: Session, payload: DocumentCreate) -> Document:
    entity = Document(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_document(db: Session, document_id: int) -> Document:
    return _get_or_404(db, Document, document_id)


def update_document(db: Session, document_id: int, payload: DocumentUpdate) -> Document:
    entity = get_document(db, document_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def delete_document(db: Session, document_id: int) -> None:
    entity = get_document(db, document_id)
    db.delete(entity)
    db.commit()


def list_announcements(db: Session) -> list[Announcement]:
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()


def create_announcement(db: Session, payload: AnnouncementCreate) -> Announcement:
    entity = Announcement(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_announcement(db: Session, announcement_id: int) -> Announcement:
    return _get_or_404(db, Announcement, announcement_id)


def update_announcement(db: Session, announcement_id: int, payload: AnnouncementUpdate) -> Announcement:
    entity = get_announcement(db, announcement_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def publish_announcement(db: Session, announcement_id: int) -> Announcement:
    entity = get_announcement(db, announcement_id)
    entity.status = "published"
    entity.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entity)
    return entity
