from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    cash_balance: Decimal
    projected_cash: Decimal
    delinquency_rate: float
    open_tickets: int
    critical_tickets: int
    ai_priorities: list[str]

