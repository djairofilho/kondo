from decimal import Decimal
from datetime import date

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


class DelinquencyUpdate(BaseModel):
    amount_due: Decimal | None = None
    days_late: int | None = None
    status: str | None = None
    risk: str | None = None


class ExpenseRadarCategory(BaseModel):
    category: str
    amount: Decimal
    share: float
    status: str
    insight: str


class ExpenseRadarItem(BaseModel):
    id: int
    description: str
    category: str
    amount: Decimal
    status: str
    due_date: date | None = None
    risk: str
    suggested_action: str


class ExpenseRadarAlert(BaseModel):
    title: str
    severity: str
    detail: str
    action: str


class ExpenseRadarResponse(BaseModel):
    total_expenses: Decimal
    category_count: int
    confidence: str
    categories: list[ExpenseRadarCategory]
    top_expenses: list[ExpenseRadarItem]
    alerts: list[ExpenseRadarAlert]
    explanation: str


class ExpenseInsightsResponse(BaseModel):
    insights: list[str]
    recommendations: list[str]
    council_summary: str
    resident_message: str
    vendor_message: str


class MonthlyReportResponse(BaseModel):
    summary: FinanceSummary
    narrative: str
    risks: list[str]
    relevant_expenses: list[ExpenseRadarItem]
    next_steps: list[str]
    council_summary: str

