from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

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
    metadata = dict(entity.payment_metadata or {})
    metadata["boleto_url"] = f"https://payments.kondo.local/boletos/{payment_id}"
    metadata["barcode"] = f"23790.00000 00000.000000 {payment_id:010d}"
    entity.payment_method = "boleto"
    entity.payment_metadata = metadata
    db.commit()
    db.refresh(entity)
    return entity


VALID_PAYMENT_COMPONENTS = {"condominio", "agua", "luz", "gas"}


def generate_component_boleto(db: Session, payment_id: int, component: str) -> Payment:
    entity = _get_or_404(db, Payment, payment_id)
    component_key = component.lower().strip()
    if component_key not in VALID_PAYMENT_COMPONENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment component",
        )

    metadata = dict(entity.payment_metadata or {})
    breakdown = metadata.get("breakdown") if isinstance(metadata.get("breakdown"), dict) else {}
    amount = Decimal(str(breakdown.get(component_key, "0")))
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment component has no amount",
        )

    component_boletos = metadata.get("component_boletos")
    if not isinstance(component_boletos, dict):
        component_boletos = {}

    component_boletos[component_key] = {
        "boleto_url": f"https://payments.kondo.local/boletos/{payment_id}/{component_key}",
        "barcode": f"23790.00000 {payment_id:010d} {component_key[:3].upper()}",
        "amount": str(amount.quantize(Decimal("0.01"))),
        "component": component_key,
    }
    metadata["component_boletos"] = component_boletos
    entity.payment_method = "boleto"
    entity.payment_metadata = metadata
    flag_modified(entity, "payment_metadata")
    flag_modified(entity, "payment_metadata")
    db.commit()
    db.refresh(entity)
    return entity
