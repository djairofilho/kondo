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

