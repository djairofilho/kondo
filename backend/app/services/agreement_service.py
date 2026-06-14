from decimal import Decimal, ROUND_HALF_UP

from app.schemas.agreements import AgreementSimulationRequest, AgreementSimulationResponse


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

