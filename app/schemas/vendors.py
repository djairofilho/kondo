from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class VendorCreate(BaseModel):
    condominium_id: int = 1
    name: str = Field(min_length=2)
    category: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str = "active"


class VendorUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None


class Vendor(VendorCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QuoteCreate(BaseModel):
    condominium_id: int = 1
    vendor_id: int | None = None
    work_item_id: int | None = None
    title: str = Field(min_length=2)
    amount: Decimal | None = None
    scope: str | None = None
    warranty_days: int | None = None
    status: str = "received"


class QuoteUpdate(BaseModel):
    vendor_id: int | None = None
    work_item_id: int | None = None
    title: str | None = None
    amount: Decimal | None = None
    scope: str | None = None
    warranty_days: int | None = None
    status: str | None = None


class Quote(QuoteCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QuoteComparison(BaseModel):
    recommendation: str
    rationale: str

