from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.schemas.finance import DelinquencyItem, DelinquencyUpdate, ExpenseInsightsResponse, ExpenseRadarResponse, FinanceSummary, MonthlyReportResponse
from app.schemas.payments import Expense, ExpenseCreate, ExpenseUpdate, Payment, PaymentCreate, PaymentUpdate, Revenue, RevenueCreate, RevenueUpdate
from app.services.finance_service import (
    get_cashflow,
    get_delinquencies,
    get_delinquency_or_404,
    get_expense_insights,
    get_expense_radar,
    get_finance_summary,
    get_monthly_report,
    update_delinquency,
)
from app.services.payment_service import (
    create_expense,
    create_payment,
    create_revenue,
    generate_boleto,
    generate_component_boleto,
    get_expense,
    get_payment,
    get_revenue,
    list_expenses,
    list_payments,
    list_revenues,
    mark_payment_paid,
    update_expense,
    update_payment,
    update_revenue,
)


router = APIRouter(tags=["finance"], dependencies=[Depends(require_roles("manager", "board_member"))])


@router.get("/finance/summary", response_model=FinanceSummary)
def finance_summary(db: Session = Depends(get_db)) -> FinanceSummary:
    return get_finance_summary(db)


@router.get("/finance/cashflow")
def finance_cashflow(db: Session = Depends(get_db)) -> dict:
    return get_cashflow(db)


@router.get("/finance/expense-radar", response_model=ExpenseRadarResponse)
def finance_expense_radar(db: Session = Depends(get_db)) -> ExpenseRadarResponse:
    return get_expense_radar(db)


@router.get("/finance/monthly-report", response_model=MonthlyReportResponse)
def finance_monthly_report(db: Session = Depends(get_db)) -> MonthlyReportResponse:
    return get_monthly_report(db)


@router.post("/finance/insights-ai")
def finance_insights_ai(db: Session = Depends(get_db)) -> dict:
    return {"insights": get_finance_summary(db).insights}


@router.post("/finance/expense-insights-ai", response_model=ExpenseInsightsResponse)
def finance_expense_insights_ai(db: Session = Depends(get_db)) -> ExpenseInsightsResponse:
    return get_expense_insights(db)


@router.get("/delinquencies", response_model=list[DelinquencyItem])
def delinquency_list(db: Session = Depends(get_db)) -> list[DelinquencyItem]:
    return get_delinquencies(db)


@router.get("/delinquencies/{delinquency_id}", response_model=DelinquencyItem)
def get_delinquency(delinquency_id: int, db: Session = Depends(get_db)) -> DelinquencyItem:
    return get_delinquency_or_404(db, delinquency_id)


@router.patch("/delinquencies/{delinquency_id}", response_model=DelinquencyItem, dependencies=[Depends(require_roles("manager"))])
def patch_delinquency(delinquency_id: int, payload: DelinquencyUpdate, db: Session = Depends(get_db)) -> DelinquencyItem:
    return update_delinquency(db, delinquency_id, payload)


@router.get("/revenues", response_model=list[Revenue])
def get_revenues(db: Session = Depends(get_db)) -> list[Revenue]:
    return list_revenues(db)


@router.post("/revenues", response_model=Revenue, dependencies=[Depends(require_roles("manager"))])
def post_revenue(payload: RevenueCreate, db: Session = Depends(get_db)) -> Revenue:
    return create_revenue(db, payload)


@router.get("/revenues/{revenue_id}", response_model=Revenue)
def get_revenue_route(revenue_id: int, db: Session = Depends(get_db)) -> Revenue:
    return get_revenue(db, revenue_id)


@router.patch("/revenues/{revenue_id}", response_model=Revenue, dependencies=[Depends(require_roles("manager"))])
def patch_revenue(revenue_id: int, payload: RevenueUpdate, db: Session = Depends(get_db)) -> Revenue:
    return update_revenue(db, revenue_id, payload)


@router.get("/expenses", response_model=list[Expense])
def get_expenses(db: Session = Depends(get_db)) -> list[Expense]:
    return list_expenses(db)


@router.post("/expenses", response_model=Expense, dependencies=[Depends(require_roles("manager"))])
def post_expense(payload: ExpenseCreate, db: Session = Depends(get_db)) -> Expense:
    return create_expense(db, payload)


@router.get("/expenses/{expense_id}", response_model=Expense)
def get_expense_route(expense_id: int, db: Session = Depends(get_db)) -> Expense:
    return get_expense(db, expense_id)


@router.patch("/expenses/{expense_id}", response_model=Expense, dependencies=[Depends(require_roles("manager"))])
def patch_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)) -> Expense:
    return update_expense(db, expense_id, payload)


@router.get("/payments", response_model=list[Payment])
def get_payments(db: Session = Depends(get_db)) -> list[Payment]:
    return list_payments(db)


@router.post("/payments", response_model=Payment, dependencies=[Depends(require_roles("manager"))])
def post_payment(payload: PaymentCreate, db: Session = Depends(get_db)) -> Payment:
    return create_payment(db, payload)


@router.get("/payments/{payment_id}", response_model=Payment)
def get_payment_route(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    return get_payment(db, payment_id)


@router.patch("/payments/{payment_id}", response_model=Payment, dependencies=[Depends(require_roles("manager"))])
def patch_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db)) -> Payment:
    return update_payment(db, payment_id, payload)


@router.post("/payments/{payment_id}/mark-paid", response_model=Payment, dependencies=[Depends(require_roles("manager"))])
def post_mark_payment_paid(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    return mark_payment_paid(db, payment_id)


@router.post("/payments/{payment_id}/generate-boleto", response_model=Payment, dependencies=[Depends(require_roles("manager"))])
def post_generate_boleto(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    return generate_boleto(db, payment_id)


@router.post("/payments/{payment_id}/components/{component}/generate-boleto", response_model=Payment, dependencies=[Depends(require_roles("manager"))])
def post_generate_component_boleto(payment_id: int, component: str, db: Session = Depends(get_db)) -> Payment:
    return generate_component_boleto(db, payment_id, component)

