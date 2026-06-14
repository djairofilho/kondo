from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.finance import DelinquencyItem, FinanceSummary
from app.schemas.payments import Expense, ExpenseCreate, ExpenseUpdate, Payment, PaymentCreate, PaymentUpdate, Revenue, RevenueCreate, RevenueUpdate
from app.services.finance_service import get_delinquencies, get_finance_summary
from app.services.payment_service import (
    create_expense,
    create_payment,
    create_revenue,
    generate_boleto,
    list_expenses,
    list_payments,
    list_revenues,
    mark_payment_paid,
    update_expense,
    update_payment,
    update_revenue,
)


router = APIRouter(tags=["finance"])


@router.get("/finance/summary", response_model=FinanceSummary)
def finance_summary(db: Session = Depends(get_db)) -> FinanceSummary:
    return get_finance_summary(db)


@router.get("/delinquencies", response_model=list[DelinquencyItem])
def delinquency_list(db: Session = Depends(get_db)) -> list[DelinquencyItem]:
    return get_delinquencies(db)


@router.get("/revenues", response_model=list[Revenue])
def get_revenues(db: Session = Depends(get_db)) -> list[Revenue]:
    return list_revenues(db)


@router.post("/revenues", response_model=Revenue)
def post_revenue(payload: RevenueCreate, db: Session = Depends(get_db)) -> Revenue:
    return create_revenue(db, payload)


@router.patch("/revenues/{revenue_id}", response_model=Revenue)
def patch_revenue(revenue_id: int, payload: RevenueUpdate, db: Session = Depends(get_db)) -> Revenue:
    return update_revenue(db, revenue_id, payload)


@router.get("/expenses", response_model=list[Expense])
def get_expenses(db: Session = Depends(get_db)) -> list[Expense]:
    return list_expenses(db)


@router.post("/expenses", response_model=Expense)
def post_expense(payload: ExpenseCreate, db: Session = Depends(get_db)) -> Expense:
    return create_expense(db, payload)


@router.patch("/expenses/{expense_id}", response_model=Expense)
def patch_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)) -> Expense:
    return update_expense(db, expense_id, payload)


@router.get("/payments", response_model=list[Payment])
def get_payments(db: Session = Depends(get_db)) -> list[Payment]:
    return list_payments(db)


@router.post("/payments", response_model=Payment)
def post_payment(payload: PaymentCreate, db: Session = Depends(get_db)) -> Payment:
    return create_payment(db, payload)


@router.patch("/payments/{payment_id}", response_model=Payment)
def patch_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db)) -> Payment:
    return update_payment(db, payment_id, payload)


@router.post("/payments/{payment_id}/mark-paid", response_model=Payment)
def post_mark_payment_paid(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    return mark_payment_paid(db, payment_id)


@router.post("/payments/{payment_id}/generate-boleto", response_model=Payment)
def post_generate_boleto(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    return generate_boleto(db, payment_id)

