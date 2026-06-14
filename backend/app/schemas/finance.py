from decimal import Decimal

from pydantic import BaseModel


class FinanceSummary(BaseModel):
    expected_revenue: Decimal
    received_revenue: Decimal
    expenses: Decimal
    cash_gap: Decimal
    insights: list[str]


class DelinquencyItem(BaseModel):
    unit_id: int
    amount_due: Decimal
    days_late: int
    risk: str

