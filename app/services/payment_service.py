from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Expense, Payment, Revenue
from app.schemas.payments import ExpenseCreate, ExpenseUpdate, PaymentCreate, PaymentUpdate, RevenueCreate, RevenueUpdate


def _get_or_404(db: Session, model, entity_id: int):
    entity = db.get(model, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return entity


def get_revenue(db: Session, revenue_id: int) -> Revenue:
    return _get_or_404(db, Revenue, revenue_id)


def list_revenues(db: Session) -> list[Revenue]:
    return db.query(Revenue).order_by(Revenue.created_at.desc()).all()


def create_revenue(db: Session, payload: RevenueCreate) -> Revenue:
    entity = Revenue(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_revenue(db: Session, revenue_id: int, payload: RevenueUpdate) -> Revenue:
    entity = _get_or_404(db, Revenue, revenue_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def get_expense(db: Session, expense_id: int) -> Expense:
    return _get_or_404(db, Expense, expense_id)


def list_expenses(db: Session) -> list[Expense]:
    return db.query(Expense).order_by(Expense.created_at.desc()).all()


def create_expense(db: Session, payload: ExpenseCreate) -> Expense:
    entity = Expense(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate) -> Expense:
    entity = _get_or_404(db, Expense, expense_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def get_payment(db: Session, payment_id: int) -> Payment:
    return _get_or_404(db, Payment, payment_id)


def list_payments(db: Session) -> list[Payment]:
    return db.query(Payment).order_by(Payment.created_at.desc()).all()


def create_payment(db: Session, payload: PaymentCreate) -> Payment:
    entity = Payment(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_payment(db: Session, payment_id: int, payload: PaymentUpdate) -> Payment:
    entity = _get_or_404(db, Payment, payment_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def mark_payment_paid(db: Session, payment_id: int) -> Payment:
    entity = _get_or_404(db, Payment, payment_id)
    entity.status = "paid"
    entity.paid_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entity)
    return entity


def generate_boleto(db: Session, payment_id: int) -> Payment:
    entity = _get_or_404(db, Payment, payment_id)
    metadata = entity.payment_metadata or {}
    metadata["boleto_url"] = f"https://payments.kondo.local/boletos/{payment_id}"
    metadata["barcode"] = f"23790.00000 00000.000000 {payment_id:010d}"
    entity.payment_method = "boleto"
    entity.payment_metadata = metadata
    db.commit()
    db.refresh(entity)
    return entity
