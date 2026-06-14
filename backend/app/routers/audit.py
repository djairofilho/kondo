from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.audit import AuditEvent, AuditEventCreate
from app.services.audit_service import create_audit_event, list_audit_events


router = APIRouter(tags=["audit"])


@router.get("/audit/events", response_model=list[AuditEvent])
def get_audit_events(db: Session = Depends(get_db)) -> list[AuditEvent]:
    return list_audit_events(db)


@router.post("/audit/events", response_model=AuditEvent)
def post_audit_event(payload: AuditEventCreate, db: Session = Depends(get_db)) -> AuditEvent:
    return create_audit_event(db, payload)

