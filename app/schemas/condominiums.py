from datetime import datetime

from pydantic import BaseModel, Field


class CondominiumCreate(BaseModel):
    name: str = Field(min_length=2)
    address: str = Field(min_length=3)
    city: str | None = None
    state: str | None = None
    status: str = "active"


class CondominiumUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    status: str | None = None


class Condominium(CondominiumCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CondominiumOverview(BaseModel):
    condominium: Condominium
    units: int
    active_memberships: int
    open_tickets: int


class UnitCreate(BaseModel):
    condominium_id: int
    number: str
    block: str | None = None
    status: str = "active"


class UnitUpdate(BaseModel):
    number: str | None = None
    block: str | None = None
    status: str | None = None


class Unit(UnitCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ResidentCreate(BaseModel):
    unit_id: int
    user_id: int | None = None
    name: str
    email: str | None = None
    resident_type: str = "tenant"
    status: str = "active"


class ResidentUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    household_info: str | None = None
    vehicles: str | None = None
    pets: str | None = None
    notification_preference: str | None = None
    onboarding_completed: bool | None = None
    onboarding_metadata: dict | None = None
    resident_type: str | None = None
    status: str | None = None


class Resident(ResidentCreate):
    id: int
    phone: str | None = None
    emergency_contact: str | None = None
    household_info: str | None = None
    vehicles: str | None = None
    pets: str | None = None
    notification_preference: str | None = None
    onboarding_completed: bool = False
    onboarding_metadata: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResidentOnboarding(BaseModel):
    unit_id: int
    unit_number: str
    unit_block: str | None = None
    resident_name: str | None = None
    email: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    household_info: str | None = None
    vehicles: str | None = None
    pets: str | None = None
    notification_preference: str | None = None
    completed: bool = False


class ResidentOnboardingUpdate(BaseModel):
    resident_name: str | None = None
    email: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    household_info: str | None = None
    vehicles: str | None = None
    pets: str | None = None
    notification_preference: str | None = None
    completed: bool = True


class MembershipCreate(BaseModel):
    user_id: int
    condominium_id: int
    unit_id: int | None = None
    role: str
    status: str = "active"


class MembershipUpdate(BaseModel):
    unit_id: int | None = None
    role: str | None = None
    status: str | None = None


class Membership(MembershipCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

