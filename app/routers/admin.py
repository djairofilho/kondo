from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models import AuditEvent, Condominium, User
from app.schemas.audit import AuditEvent as AuditEventSchema
from app.schemas.auth import UserProfile
from app.schemas.condominiums import Condominium as CondominiumSchema, CondominiumCreate
from app.services.condominium_service import create_condominium


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", dependencies=[Depends(require_roles("platform_admin"))])
def admin_overview(db: Session = Depends(get_db)) -> dict:
    return {
        "condominiums": db.query(Condominium).count(),
        "users": db.query(User).count(),
        "audit_events": db.query(AuditEvent).count(),
    }


@router.get("/condominiums", response_model=list[CondominiumSchema], dependencies=[Depends(require_roles("platform_admin"))])
def admin_condominiums(db: Session = Depends(get_db)) -> list[Condominium]:
    return db.query(Condominium).order_by(Condominium.created_at.desc()).all()


@router.post("/condominiums", response_model=CondominiumSchema, dependencies=[Depends(require_roles("platform_admin"))])
def admin_create_condominium(payload: CondominiumCreate, db: Session = Depends(get_db)) -> Condominium:
    return create_condominium(db, payload)


@router.get("/users", response_model=list[UserProfile], dependencies=[Depends(require_roles("platform_admin"))])
def admin_users(db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/audit-events", response_model=list[AuditEventSchema], dependencies=[Depends(require_roles("platform_admin"))])
def admin_audit_events(db: Session = Depends(get_db)) -> list[AuditEvent]:
    return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()

