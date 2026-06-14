from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Agreement, Payment
from app.schemas.agreements import AgreementCreate, AgreementSimulationRequest, AgreementSimulationResponse, AgreementUpdate


def simulate_agreement(payload: AgreementSimulationRequest) -> AgreementSimulationResponse:
    total_due = payload.amount_due + payload.fine_amount
    remaining_amount = max(total_due - payload.entry_amount, Decimal("0"))
    monthly_installment = (remaining_amount / payload.installments).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    is_safe_installment_count = payload.installments <= 4
    has_meaningful_entry = payload.entry_amount >= total_due * Decimal("0.20")
    has_moderate_fine = payload.fine_amount <= payload.amount_due * Decimal("0.10")

    if is_safe_installment_count and has_meaningful_entry and has_moderate_fine:
        cash_impact = "Mantem o caixa positivo no proximo mes."
        recommendation = "Acordo recomendado: boa entrada e prazo controlado."
    elif not has_moderate_fine:
        cash_impact = "Multa elevada aumenta o valor da parcela e pode reduzir adesao."
        recommendation = "Revise a multa ou ofereca entrada menor para preservar negociacao."
    else:
        cash_impact = "Pode pressionar o caixa se outras unidades atrasarem."
        recommendation = "Sugira entrada maior ou reduza o numero de parcelas."

    return AgreementSimulationResponse(
        monthly_installment=monthly_installment,
        total_due=total_due.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        financed_amount=remaining_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
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

