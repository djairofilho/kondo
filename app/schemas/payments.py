from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RevenueCreate(BaseModel):
    condominium_id: int = 1
    unit_id: int | None = None
    description: str = Field(min_length=3)
    amount: Decimal = Field(gt=0)
    due_date: date | None = None
    status: str = "pending"


class RevenueUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    due_date: date | None = None
    status: str | None = None


class Revenue(RevenueCreate):
    id: int
    paid_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    condominium_id: int = 1
    description: str = Field(min_length=3)
    category: str
    amount: Decimal = Field(gt=0)
    due_date: date | None = None
    status: str = "pending"


class ExpenseUpdate(BaseModel):
    description: str | None = None
    category: str | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    due_date: date | None = None
    status: str | None = None


class Expense(ExpenseCreate):
    id: int
    paid_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    condominium_id: int = 1
    unit_id: int | None = None
    agreement_id: int | None = None
    amount: Decimal = Field(gt=0)
    due_date: date | None = None
    payment_method: str | None = None
    status: str = "pending"
    payment_metadata: dict | None = None


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    due_date: date | None = None
    payment_method: str | None = None
    status: str | None = None
    payment_metadata: dict | None = None


class Payment(PaymentCreate):
    id: int
    paid_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

