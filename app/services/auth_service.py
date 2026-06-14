from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models import Membership, User
from app.schemas.auth import MembershipProfile, PermissionsResponse, TokenResponse, UserCreate, UserProfile


ROLE_PERMISSIONS = {
    "platform_admin": ["platform:admin", "condominiums:manage", "users:manage"],
    "manager": ["condominium:operate", "tickets:manage", "finance:manage", "announcements:publish"],
    "board_member": ["transparency:read", "finance:read", "audit:read"],
    "resident": ["portal:read", "tickets:create", "tickets:read-own", "rules:ask"],
}


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_token(str(user.id), timedelta(minutes=60), "access"),
        refresh_token=create_token(str(user.id), timedelta(days=7), "refresh"),
        user=UserProfile.model_validate(user),
    )


def register_user(db: Session, payload: UserCreate) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(name=payload.name, email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


def authenticate_user(db: Session, email: str, password: str) -> TokenResponse:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return _token_response(user)


def refresh_session(db: Session, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token, expected_type="refresh")
    user = db.get(User, int(payload["sub"]))
    if user is None or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return _token_response(user)


def list_memberships(db: Session, user: User) -> list[MembershipProfile]:
    rows = (
        db.query(Membership)
        .filter(Membership.user_id == user.id, Membership.status == "active")
        .all()
    )
    return [
        MembershipProfile(
            id=row.id,
            condominium_id=row.condominium_id,
            condominium_name=row.condominium.name,
            unit_id=row.unit_id,
            role=row.role,
            status=row.status,
        )
        for row in rows
    ]


def get_permissions(db: Session, user: User) -> PermissionsResponse:
    roles = ["platform_admin"] if user.is_platform_admin else []
    roles.extend(row.role for row in db.query(Membership).filter(Membership.user_id == user.id, Membership.status == "active"))

    permissions = sorted({permission for role in roles for permission in ROLE_PERMISSIONS.get(role, [])})
    return PermissionsResponse(roles=sorted(set(roles)), permissions=permissions)

