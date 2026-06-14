from sqlalchemy.orm import Session

from app.models import AuditEvent
from app.schemas.audit import AuditEventCreate


def list_audit_events(db: Session) -> list[AuditEvent]:
    return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()


def create_audit_event(db: Session, payload: AuditEventCreate) -> AuditEvent:
    entity = AuditEvent(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

