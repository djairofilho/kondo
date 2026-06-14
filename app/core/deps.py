from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models import AuditEvent, Membership, Unit, User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    payload = decode_token(credentials.credentials)
    user_id = int(payload["sub"])
    user = db.get(User, user_id)
    if user is None or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_roles(*roles: str):
    def dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.is_platform_admin:
            return current_user

        has_role = (
            db.query(Membership)
            .filter(
                Membership.user_id == current_user.id,
                Membership.role.in_(roles),
                Membership.status == "active",
            )
            .first()
            is not None
        )
        if not has_role:
            record_authorization_denied(db, current_user, request.url.path, roles)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        return current_user

    return dependency


def record_authorization_denied(db: Session, current_user: User, path: str, roles: tuple[str, ...] = ()) -> None:
    membership = get_active_membership(db, current_user)
    db.add(
        AuditEvent(
            condominium_id=membership.condominium_id if membership else None,
            actor_user_id=current_user.id,
            action="authorization.denied",
            entity_type="route",
            event_metadata={"path": path, "required_roles": list(roles)},
        )
    )
    db.commit()


def get_active_membership(db: Session, current_user: User, *roles: str) -> Membership | None:
    query = db.query(Membership).filter(Membership.user_id == current_user.id, Membership.status == "active")
    if roles:
        query = query.filter(Membership.role.in_(roles))
    return query.order_by(Membership.created_at.asc()).first()


def get_unit_or_404(db: Session, unit_id: int) -> Unit:
    unit = db.get(Unit, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return unit


def ensure_condominium_access(db: Session, current_user: User, condominium_id: int, *roles: str) -> None:
    if current_user.is_platform_admin:
        return

    query = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.condominium_id == condominium_id,
        Membership.status == "active",
    )
    if roles:
        query = query.filter(Membership.role.in_(roles))
    if query.first() is None:
        record_authorization_denied(db, current_user, f"condominiums/{condominium_id}", roles)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient condominium access")


def ensure_unit_access(db: Session, current_user: User, unit_id: int, *roles: str) -> Unit:
    unit = get_unit_or_404(db, unit_id)
    ensure_condominium_access(db, current_user, unit.condominium_id, *roles)
    return unit


def resolve_resident_portal_unit(
    unit_id: int | None = None,
    current_user: User = Depends(require_roles("resident", "manager", "board_member")),
    db: Session = Depends(get_db),
) -> Unit | None:
    if current_user.is_platform_admin:
        return get_unit_or_404(db, unit_id) if unit_id is not None else None

    support_membership = get_active_membership(db, current_user, "manager", "board_member")
    if support_membership is not None and unit_id is not None:
        return ensure_unit_access(db, current_user, unit_id, "manager", "board_member")

    resident_membership = get_active_membership(db, current_user, "resident")
    if resident_membership is None or resident_membership.unit_id is None:
        if support_membership is not None:
            return None
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resident unit not found")

    return get_unit_or_404(db, resident_membership.unit_id)


def resolve_resident_ticket_unit(
    current_user: User = Depends(require_roles("resident")),
    db: Session = Depends(get_db),
) -> Unit:
    resident_membership = get_active_membership(db, current_user, "resident")
    if resident_membership is None or resident_membership.unit_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resident unit not found")
    return get_unit_or_404(db, resident_membership.unit_id)
