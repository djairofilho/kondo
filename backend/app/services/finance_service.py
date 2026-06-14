from decimal import Decimal

from app.schemas.finance import DelinquencyItem, FinanceSummary


def get_finance_summary() -> FinanceSummary:
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


def get_delinquencies() -> list[DelinquencyItem]:
    return [
        DelinquencyItem(unit_id=304, amount_due=Decimal("1548.00"), days_late=63, risk="medio"),
        DelinquencyItem(unit_id=1202, amount_due=Decimal("1032.00"), days_late=41, risk="baixo"),
        DelinquencyItem(unit_id=708, amount_due=Decimal("2580.00"), days_late=95, risk="alto"),
    ]

