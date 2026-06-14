from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(min_length=5)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    is_platform_admin: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserProfile


class MembershipProfile(BaseModel):
    id: int
    condominium_id: int
    condominium_name: str
    unit_id: int | None
    role: str
    status: str


class PermissionsResponse(BaseModel):
    roles: list[str]
    permissions: list[str]

