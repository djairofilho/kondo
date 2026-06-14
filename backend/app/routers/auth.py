from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    MembershipProfile,
    PermissionsResponse,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserProfile,
)
from app.services.auth_service import authenticate_user, get_permissions, list_memberships, refresh_session, register_user


router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    return register_user(db, payload)


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return authenticate_user(db, payload.email, payload.password)


@router.post("/auth/logout")
def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return refresh_session(db, payload.refresh_token)


@router.get("/me", response_model=UserProfile)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/memberships", response_model=list[MembershipProfile])
def me_memberships(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MembershipProfile]:
    return list_memberships(db, current_user)


@router.get("/me/permissions", response_model=PermissionsResponse)
def me_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PermissionsResponse:
    return get_permissions(db, current_user)

