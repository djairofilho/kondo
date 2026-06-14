from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Agreement, Payment
from app.schemas.agreements import AgreementCreate, AgreementSimulationRequest, AgreementSimulationResponse, AgreementUpdate


def simulate_agreement(payload: AgreementSimulationRequest) -> AgreementSimulationResponse:
    remaining_amount = max(payload.amount_due - payload.entry_amount, Decimal("0"))
    monthly_installment = (remaining_amount / payload.installments).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    is_safe_installment_count = payload.installments <= 4
    has_meaningful_entry = payload.entry_amount >= payload.amount_due * Decimal("0.20")

    if is_safe_installment_count and has_meaningful_entry:
        cash_impact = "Mantem o caixa positivo no proximo mes."
        recommendation = "Acordo recomendado: boa entrada e prazo controlado."
    else:
        cash_impact = "Pode pressionar o caixa se outras unidades atrasarem."
        recommendation = "Sugira entrada maior ou reduza o numero de parcelas."

    return AgreementSimulationResponse(
        monthly_installment=monthly_installment,
        cash_impact=cash_impact,
        recommendation=recommendation,
    )


def list_agreements(db: Session) -> list[Agreement]:
    return db.query(Agreement).order_by(Agreement.created_at.desc()).all()


def get_agreement_or_404(db: Session, agreement_id: int) -> Agreement:
    agreement = db.get(Agreement, agreement_id)
    if agreement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agreement not found")
    return agreement


def create_agreement(db: Session, payload: AgreementCreate) -> Agreement:
    agreement = Agreement(**payload.model_dump())
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return agreement


def update_agreement(db: Session, agreement_id: int, payload: AgreementUpdate) -> Agreement:
    agreement = get_agreement_or_404(db, agreement_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(agreement, field, value)
    db.commit()
    db.refresh(agreement)
    return agreement


def cancel_agreement(db: Session, agreement_id: int) -> Agreement:
    agreement = get_agreement_or_404(db, agreement_id)
    agreement.status = "cancelled"
    db.commit()
    db.refresh(agreement)
    return agreement


def add_agreement_payment(db: Session, agreement_id: int) -> Payment:
    agreement = get_agreement_or_404(db, agreement_id)
    payment = Payment(
        condominium_id=agreement.unit.condominium_id,
        unit_id=agreement.unit_id,
        agreement_id=agreement.id,
        amount=agreement.monthly_installment,
        payment_method="pix",
        status="pending",
        payment_metadata={"source": "agreement"},
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

