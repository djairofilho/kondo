from decimal import Decimal

from pydantic import BaseModel, Field


class AgreementSimulationRequest(BaseModel):
    unit_id: int
    amount_due: Decimal = Field(gt=0)
    entry_amount: Decimal = Field(ge=0)
    installments: int = Field(gt=0, le=24)


class AgreementSimulationResponse(BaseModel):
    monthly_installment: Decimal
    cash_impact: str
    recommendation: str


class AgreementCreate(BaseModel):
    unit_id: int
    delinquency_id: int | None = None
    entry_amount: Decimal = Field(ge=0)
    installments: int = Field(gt=0, le=24)
    monthly_installment: Decimal = Field(gt=0)
    status: str = "active"


class AgreementUpdate(BaseModel):
    entry_amount: Decimal | None = Field(default=None, ge=0)
    installments: int | None = Field(default=None, gt=0, le=24)
    monthly_installment: Decimal | None = Field(default=None, gt=0)
    status: str | None = None


class Agreement(AgreementCreate):
    id: int

    model_config = {"from_attributes": True}

