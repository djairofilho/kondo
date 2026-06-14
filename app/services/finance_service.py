from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Delinquency, Expense, Revenue
from fastapi import HTTPException, status

from app.schemas.finance import (
    DelinquencyItem,
    DelinquencyUpdate,
    ExpenseInsightsResponse,
    ExpenseRadarAlert,
    ExpenseRadarCategory,
    ExpenseRadarItem,
    ExpenseRadarResponse,
    FinanceSummary,
    MonthlyReportResponse,
)


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


def _expense_risk(expense: Expense, total_expenses: Decimal) -> str:
    if total_expenses <= 0:
        return "baixo"
    share = expense.amount / total_expenses
    if share >= Decimal("0.35") or expense.status in {"overdue", "late"}:
        return "alto"
    if share >= Decimal("0.18") or expense.status == "pending":
        return "medio"
    return "baixo"


def _expense_action(expense: Expense, total_expenses: Decimal) -> str:
    risk = _expense_risk(expense, total_expenses)
    if risk == "alto":
        return "Pedir segunda cotacao, revisar contrato ou levar ao conselho antes de pagar."
    if risk == "medio":
        return "Conferir nota, vencimento e historico antes da aprovacao."
    return "Acompanhar no fluxo normal de pagamentos."


def _top_expense_items(expenses: list[Expense], total_expenses: Decimal, limit: int = 5) -> list[ExpenseRadarItem]:
    return [
        ExpenseRadarItem(
            id=expense.id,
            description=expense.description,
            category=expense.category,
            amount=expense.amount,
            status=expense.status,
            due_date=expense.due_date,
            risk=_expense_risk(expense, total_expenses),
            suggested_action=_expense_action(expense, total_expenses),
        )
        for expense in sorted(expenses, key=lambda item: item.amount, reverse=True)[:limit]
    ]


def get_expense_radar(db: Session) -> ExpenseRadarResponse:
    expenses = db.query(Expense).order_by(Expense.amount.desc()).all()
    total_expenses = sum((expense.amount for expense in expenses), Decimal("0.00"))
    summary = get_finance_summary(db)
    delinquencies = get_delinquencies(db)
    delinquency_total = sum((item.amount_due for item in delinquencies), Decimal("0.00"))

    if not expenses:
        return ExpenseRadarResponse(
            total_expenses=Decimal("0.00"),
            category_count=0,
            confidence="baixa",
            categories=[],
            top_expenses=[],
            alerts=[
                ExpenseRadarAlert(
                    title="Sem despesas cadastradas",
                    severity="info",
                    detail="Cadastre despesas ou importe pagamentos para liberar comparacoes uteis.",
                    action="Adicionar despesas no financeiro.",
                )
            ],
            explanation="Ainda nao ha historico suficiente. O radar vai ganhar confianca conforme despesas forem registradas.",
        )

    category_totals: dict[str, Decimal] = {}
    for expense in expenses:
        category_totals[expense.category] = category_totals.get(expense.category, Decimal("0.00")) + expense.amount

    categories: list[ExpenseRadarCategory] = []
    for category, amount in sorted(category_totals.items(), key=lambda item: item[1], reverse=True):
        share = float((amount / total_expenses) * 100) if total_expenses else 0.0
        status_label = "critico" if share >= 40 else "atencao" if share >= 25 else "em_linha"
        insight = (
            f"{category} concentra {share:.1f}% das despesas. "
            + ("Vale revisar contrato ou cotacao." if share >= 25 else "Esta dentro de uma faixa esperada para o MVP.")
        )
        categories.append(ExpenseRadarCategory(category=category, amount=amount, share=round(share, 2), status=status_label, insight=insight))

    alerts: list[ExpenseRadarAlert] = []
    if summary.cash_gap < 0:
        alerts.append(
            ExpenseRadarAlert(
                title="Caixa projetado negativo",
                severity="critical",
                detail=f"O caixa esta em {summary.cash_gap}. Priorize cobrancas e despesas essenciais.",
                action="Simular acordos e revisar pagamentos pendentes.",
            )
        )
    if categories and categories[0].share >= 35:
        alerts.append(
            ExpenseRadarAlert(
                title="Categoria concentrada",
                severity="warning",
                detail=f"{categories[0].category} representa {categories[0].share:.1f}% das despesas cadastradas.",
                action="Comparar fornecedor atual com pelo menos duas alternativas.",
            )
        )
    if delinquency_total > 0:
        alerts.append(
            ExpenseRadarAlert(
                title="Inadimplencia pressiona caixa",
                severity="warning",
                detail=f"Ha {delinquency_total} em aberto impactando a previsibilidade do mes.",
                action="Priorizar unidades com maior atraso e oferecer acordo.",
            )
        )
    pending_total = sum((expense.amount for expense in expenses if expense.status != "paid"), Decimal("0.00"))
    if pending_total > 0:
        alerts.append(
            ExpenseRadarAlert(
                title="Pagamentos a aprovar",
                severity="info",
                detail=f"Existem {pending_total} em despesas ainda nao quitadas.",
                action="Conferir vencimentos e aprovar somente despesas sem pendencia.",
            )
        )

    confidence = "media" if len(expenses) < 6 else "alta"
    if len(expenses) < 3:
        confidence = "baixa"

    return ExpenseRadarResponse(
        total_expenses=total_expenses,
        category_count=len(categories),
        confidence=confidence,
        categories=categories,
        top_expenses=_top_expense_items(expenses, total_expenses),
        alerts=alerts,
        explanation=(
            "Radar calculado com base nas despesas cadastradas, receita recebida e inadimplencia atual. "
            "Como ainda nao ha serie historica completa, variacoes usam concentracao por categoria e impacto no caixa."
        ),
    )


def get_expense_insights(db: Session) -> ExpenseInsightsResponse:
    summary = get_finance_summary(db)
    radar = get_expense_radar(db)
    top_category = radar.categories[0] if radar.categories else None
    top_expense = radar.top_expenses[0] if radar.top_expenses else None

    insights = [
        f"Receita recebida: {summary.received_revenue}; despesas: {summary.expenses}; caixa projetado: {summary.cash_gap}.",
        radar.explanation,
    ]
    if top_category:
        insights.append(f"Maior concentracao: {top_category.category}, com {top_category.share:.1f}% das despesas.")
    if top_expense:
        insights.append(f"Despesa mais relevante: {top_expense.description} ({top_expense.amount}), risco {top_expense.risk}.")

    recommendations = []
    if summary.cash_gap < 0:
        recommendations.append("Antecipar cobrancas e negociar despesas nao essenciais ate recompor o caixa.")
    if top_category and top_category.share >= 25:
        recommendations.append(f"Renegociar ou cotar alternativas para {top_category.category}.")
    recommendations.append("Enviar resumo ao conselho com riscos, decisoes pendentes e proximos passos.")

    council_summary = (
        f"Resumo financeiro: receita recebida {summary.received_revenue}, despesas {summary.expenses}, "
        f"caixa projetado {summary.cash_gap}. "
        f"Principal ponto de atencao: {radar.alerts[0].title if radar.alerts else 'sem alerta critico no momento'}."
    )
    resident_message = (
        "Estamos acompanhando as despesas do condominio e priorizando pagamentos essenciais. "
        "Novas medidas serao comunicadas com antecedencia."
    )
    vendor_message = (
        "Ola, estamos revisando contratos e despesas do condominio. "
        "Pode enviar uma proposta atualizada com opcoes de reducao de custo ou melhoria de prazo?"
    )

    return ExpenseInsightsResponse(
        insights=insights,
        recommendations=recommendations,
        council_summary=council_summary,
        resident_message=resident_message,
        vendor_message=vendor_message,
    )


def get_monthly_report(db: Session) -> MonthlyReportResponse:
    summary = get_finance_summary(db)
    radar = get_expense_radar(db)
    insights = get_expense_insights(db)
    risks = [alert.detail for alert in radar.alerts] or ["Nenhum risco financeiro relevante detectado nos dados atuais."]
    next_steps = insights.recommendations
    return MonthlyReportResponse(
        summary=summary,
        narrative=(
            "Relatorio mensal gerado a partir das receitas, despesas e inadimplencias persistidas. "
            f"O caixa projetado e {summary.cash_gap}, com confianca {radar.confidence} no radar de despesas."
        ),
        risks=risks,
        relevant_expenses=radar.top_expenses,
        next_steps=next_steps,
        council_summary=insights.council_summary,
    )

