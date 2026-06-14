from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Delinquency, Expense, Revenue
from fastapi import HTTPException, status

from app.schemas.finance import DelinquencyItem, DelinquencyUpdate, FinanceSummary


def _sum_or_zero(value: Decimal | None) -> Decimal:
    return value or Decimal("0.00")


def get_finance_summary(db: Session | None = None) -> FinanceSummary:
    if db is not None:
        expected_revenue = _sum_or_zero(db.query(func.sum(Revenue.amount)).scalar())
        received_revenue = _sum_or_zero(db.query(func.sum(Revenue.amount)).filter(Revenue.status == "paid").scalar())
        expenses = _sum_or_zero(db.query(func.sum(Expense.amount)).scalar())
        cash_gap = received_revenue - expenses
        return FinanceSummary(
            expected_revenue=expected_revenue,
            received_revenue=received_revenue,
            expenses=expenses,
            cash_gap=cash_gap,
            insights=[
                "Resumo calculado a partir das receitas e despesas persistidas.",
                "Use o cash gap para priorizar acordos e cobrancas.",
            ],
        )

    return FinanceSummary(
        expected_revenue=Decimal("20640.00"),
        received_revenue=Decimal("17640.00"),
        expenses=Decimal("19800.00"),
        cash_gap=Decimal("-2160.00"),
        insights=[
            "A inadimplencia atual pode pressionar o caixa ainda este mes.",
            "A conta de agua subiu 18% em relacao a media dos ultimos 3 meses.",
        ],
    )


def get_delinquencies(db: Session | None = None) -> list[DelinquencyItem]:
    if db is not None:
        rows = db.query(Delinquency).order_by(Delinquency.days_late.desc()).all()
        return [
            DelinquencyItem(
                id=row.id,
                unit_id=row.unit_id,
                amount_due=row.amount_due,
                days_late=row.days_late,
                risk=row.risk,
                status=row.status,
            )
            for row in rows
        ]

    return [
        DelinquencyItem(unit_id=304, amount_due=Decimal("1548.00"), days_late=63, risk="medio"),
        DelinquencyItem(unit_id=1202, amount_due=Decimal("1032.00"), days_late=41, risk="baixo"),
        DelinquencyItem(unit_id=708, amount_due=Decimal("2580.00"), days_late=95, risk="alto"),
    ]


def get_delinquency_or_404(db: Session, delinquency_id: int) -> Delinquency:
    delinquency = db.get(Delinquency, delinquency_id)
    if delinquency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delinquency not found")
    return delinquency


def update_delinquency(db: Session, delinquency_id: int, payload: DelinquencyUpdate) -> Delinquency:
    delinquency = get_delinquency_or_404(db, delinquency_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(delinquency, field, value)
    db.commit()
    db.refresh(delinquency)
    return delinquency


def get_cashflow(db: Session) -> dict:
    summary = get_finance_summary(db)
    return {
        "expected_revenue": summary.expected_revenue,
        "received_revenue": summary.received_revenue,
        "expenses": summary.expenses,
        "projected_cash": summary.cash_gap,
    }


def get_monthly_report(db: Session) -> dict:
    summary = get_finance_summary(db)
    return {
        "summary": summary.model_dump(),
        "narrative": "Relatorio mensal gerado a partir das receitas, despesas e inadimplencias persistidas.",
    }

