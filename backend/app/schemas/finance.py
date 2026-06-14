from decimal import Decimal

from pydantic import BaseModel


class FinanceSummary(BaseModel):
    expected_revenue: Decimal
    received_revenue: Decimal
    expenses: Decimal
    cash_gap: Decimal
    insights: list[str]


class DelinquencyItem(BaseModel):
    id: int | None = None
    unit_id: int
    amount_due: Decimal
    days_late: int
    risk: str
    status: str | None = None

    model_config = {"from_attributes": True}

