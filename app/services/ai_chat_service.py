import asyncio
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_active_membership
from app.models import Announcement, Delinquency, Document, Expense, Membership, Revenue, Ticket, User
from app.schemas.ai_chat import AIChatAction, AIChatRequest, AIChatResponse


SYSTEM_PROMPT = """
Voce e o Kondo IA, copiloto operacional de gestao condominial.
Responda sempre em portugues do Brasil, com objetividade e foco em decisao.
Organize prioridades, explique riscos e sugira proximas acoes usando rotas existentes.
Nunca diga que executou uma acao destrutiva. Para acoes sensiveis futuras, peca confirmacao.
Nao exponha dados financeiros restritos para moradores.
""".strip()


ROLE_TO_PROFILE = {
    "manager": "sindico",
    "board_member": "conselho",
    "resident": "morador",
}


def _money(value: Decimal | int | float | None) -> str:
    amount = Decimal(value or 0)
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _profile_for_user(db: Session, current_user: User, requested_profile: str | None) -> str:
    memberships = (
        db.query(Membership)
        .filter(Membership.user_id == current_user.id, Membership.status == "active")
        .order_by(Membership.created_at.asc())
        .all()
    )
    allowed_profiles = {ROLE_TO_PROFILE.get(membership.role) for membership in memberships}
    allowed_profiles.discard(None)

    if requested_profile in allowed_profiles:
        return requested_profile
    if allowed_profiles:
        return sorted(allowed_profiles)[0]
    if current_user.is_platform_admin:
        return requested_profile or "sindico"
    return "morador"


def _context_for_user(db: Session, current_user: User, profile: str) -> dict:
    membership = get_active_membership(db, current_user)
    condominium_id = membership.condominium_id if membership else None
    unit_id = membership.unit_id if membership else None

    ticket_query = db.query(Ticket)
    if condominium_id is not None:
        ticket_query = ticket_query.filter(Ticket.condominium_id == condominium_id)
    if profile == "morador":
        ticket_query = ticket_query.filter(Ticket.unit_id == unit_id)

    tickets = ticket_query.order_by(Ticket.created_at.desc()).limit(8).all()
    critical_tickets = [
        ticket
        for ticket in tickets
        if ticket.status not in {"resolved", "closed"} and ticket.priority in {"high", "critical", "alta", "critica"}
    ]

    documents_count = 0
    announcements_count = 0
    if condominium_id is not None:
        documents_count = db.query(Document).filter(Document.condominium_id == condominium_id).count()
        announcements_count = (
            db.query(Announcement)
            .filter(Announcement.condominium_id == condominium_id, Announcement.status == "published")
            .count()
        )

    context = {
        "profile": profile,
        "route_hint": None,
        "tickets_total": len(tickets),
        "critical_tickets": [ticket.title for ticket in critical_tickets[:4]],
        "documents_count": documents_count,
        "announcements_count": announcements_count,
    }

    if profile != "morador":
        finance_query = db.query(Revenue, Expense)
        if condominium_id is not None:
            finance_query = finance_query.filter(Revenue.condominium_id == condominium_id)
        received = db.query(func.sum(Revenue.amount)).filter(Revenue.status == "paid")
        expected = db.query(func.sum(Revenue.amount))
        expenses = db.query(func.sum(Expense.amount))
        delinquencies = db.query(func.sum(Delinquency.amount_due))
        if condominium_id is not None:
            received = received.filter(Revenue.condominium_id == condominium_id)
            expected = expected.filter(Revenue.condominium_id == condominium_id)
            expenses = expenses.filter(Expense.condominium_id == condominium_id)
            delinquencies = delinquencies.join(Delinquency.unit).filter_by(condominium_id=condominium_id)

        received_total = received.scalar() or Decimal("0.00")
        expenses_total = expenses.scalar() or Decimal("0.00")
        context["finance"] = {
            "expected_revenue": _money(expected.scalar()),
            "received_revenue": _money(received_total),
            "expenses": _money(expenses_total),
            "cash_gap": _money(received_total - expenses_total),
            "delinquency_total": _money(delinquencies.scalar()),
        }

    return context


def _actions_for(message: str, profile: str) -> list[AIChatAction]:
    text = message.lower()
    actions: list[AIChatAction] = []
    if any(term in text for term in ["chamado", "manutenc", "problema", "prioridade"]):
        actions.append(AIChatAction(label="Abrir chamados", to="/chamados"))
    if profile != "morador" and any(term in text for term in ["finance", "despesa", "caixa", "inadimpl", "acordo"]):
        actions.append(AIChatAction(label="Abrir financeiro", to="/financeiro"))
    if profile != "morador" and any(term in text for term in ["conselho", "transpar", "resumo"]):
        actions.append(AIChatAction(label="Abrir conselho", to="/conselho"))
    if any(term in text for term in ["document", "comunic", "morador"]):
        actions.append(AIChatAction(label="Abrir documentos", to="/documentos"))
    if profile == "morador":
        actions.append(AIChatAction(label="Abrir portal", to="/morador"))
    elif not actions:
        actions.append(AIChatAction(label="Central do sindico", to="/sindico"))
    actions.append(AIChatAction(label="Dashboard padrao", to="/"))

    unique: list[AIChatAction] = []
    seen: set[str] = set()
    for action in actions:
        key = f"{action.label}:{action.to}"
        if key not in seen:
            unique.append(action)
            seen.add(key)
    return unique[:4]


def _mock_answer(payload: AIChatRequest, context: dict) -> str:
    profile = context["profile"]
    text = payload.message.lower()
    critical = context["critical_tickets"]

    if profile == "morador":
        if any(term in text for term in ["finance", "despesa", "caixa", "inadimpl"]):
            return (
                "Como morador, eu nao mostro dados financeiros restritos do condominio aqui. "
                "Posso te ajudar com chamados da sua unidade, comunicados, regras e proximas acoes no portal."
            )
        return (
            f"Para voce, eu olharia primeiro seus {context['tickets_total']} chamado(s) e os comunicados publicados. "
            "Se quiser resolver algo rapido, descreva o problema e eu te ajudo a transformar em um chamado claro."
        )

    finance = context.get("finance", {})
    if any(term in text for term in ["finance", "despesa", "caixa", "inadimpl", "acordo"]):
        return (
            "Resumo operacional: "
            f"receita recebida {finance.get('received_revenue')}, despesas {finance.get('expenses')} "
            f"e caixa projetado {finance.get('cash_gap')}. "
            "Eu priorizaria cobrancas/acordos, revisao das maiores despesas e um resumo curto para o conselho."
        )
    if any(term in text for term in ["chamado", "manutenc", "problema"]):
        if critical:
            return f"Eu comecaria por estes chamados criticos: {', '.join(critical)}. Abra o Kanban e resolva o maior impacto primeiro."
        return "Nao encontrei chamados criticos no contexto atual. Vale revisar novos chamados e manter o Kanban limpo."
    if any(term in text for term in ["conselho", "resumo"]):
        return (
            f"Resumo para conselho: caixa projetado {finance.get('cash_gap')}, "
            f"{len(critical)} chamado(s) critico(s), {context['documents_count']} documento(s) no acervo "
            "e proximas decisoes focadas em caixa e manutencao."
        )
    return (
        f"Eu organizaria o dia assim: {len(critical)} chamado(s) critico(s), "
        f"caixa projetado {finance.get('cash_gap', 'indisponivel')} e comunicacao pendente para moradores/conselho. "
        "Me diga se voce quer foco em financeiro, chamados, documentos ou moradores."
    )


def _prompt(payload: AIChatRequest, context: dict) -> str:
    history = "\n".join(f"{item.role}: {item.content}" for item in payload.history[-6:])
    return (
        f"Perfil: {context['profile']}\n"
        f"Rota atual: {payload.route or 'nao informada'}\n"
        f"Contexto seguro: {context}\n"
        f"Historico recente:\n{history or 'sem historico'}\n"
        f"Pergunta: {payload.message}\n"
        "Responda em ate 2 paragrafos curtos, com recomendacao operacional."
    )


async def _run_anthropic_agent(payload: AIChatRequest, context: dict) -> str:
    settings = get_settings()
    from pydantic_ai import Agent
    from pydantic_ai.models.anthropic import AnthropicModel
    from pydantic_ai.providers.anthropic import AnthropicProvider

    model = AnthropicModel(
        settings.ai_model,
        provider=AnthropicProvider(api_key=settings.anthropic_api_key),
    )
    agent = Agent(model, system_prompt=SYSTEM_PROMPT)
    result = await asyncio.wait_for(
        agent.run(_prompt(payload, context)),
        timeout=settings.ai_timeout_seconds,
    )
    return str(result.output).strip()


async def chat_with_kondo_ai(db: Session, current_user: User, payload: AIChatRequest) -> AIChatResponse:
    settings = get_settings()
    profile = _profile_for_user(db, current_user, payload.profile)
    context = _context_for_user(db, current_user, profile)
    actions = _actions_for(payload.message, profile)

    can_use_anthropic = (
        settings.ai_provider == "anthropic"
        and bool(settings.anthropic_api_key)
        and settings.ai_model
    )

    if can_use_anthropic:
        try:
            answer = await _run_anthropic_agent(payload, context)
            if answer:
                return AIChatResponse(
                    answer=answer,
                    actions=actions,
                    confidence="medium",
                    source="ai",
                    provider="anthropic",
                    model=settings.ai_model,
                )
        except Exception:
            if not settings.ai_enable_mock_fallback:
                raise

    return AIChatResponse(
        answer=_mock_answer(payload, context),
        actions=actions,
        confidence="medium" if context["tickets_total"] or context.get("finance") else "low",
        source="mock",
        provider=settings.ai_provider if can_use_anthropic else "mock",
        model=settings.ai_model if can_use_anthropic else "mock",
    )
