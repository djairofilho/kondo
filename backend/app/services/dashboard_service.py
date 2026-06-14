from decimal import Decimal

from app.schemas.dashboard import DashboardSummary


def get_dashboard_summary() -> DashboardSummary:
    return DashboardSummary(
        cash_balance=Decimal("18400.00"),
        projected_cash=Decimal("14200.00"),
        delinquency_rate=0.1195,
        open_tickets=12,
        critical_tickets=2,
        ai_priorities=[
            "Risco de deficit no proximo mes se 3 acordos nao forem fechados.",
            "Chamado de vazamento na garagem B2 deve ser priorizado.",
            "Contrato de manutencao do elevador vence em 7 dias.",
        ],
    )

