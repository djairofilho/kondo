import asyncio
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_active_membership
from app.models import (
    Announcement,
    AuditEvent,
    ChatSession,
    Delinquency,
    Document,
    Expense,
    Membership,
    Revenue,
    Ticket,
    Unit,
    User,
)
from app.schemas.ai_chat import AIChatAction, AIChatRequest, AIChatResponse, AIChatToolCall


# ---------------------------------------------------------------------------
# result_type — saída estruturada obrigatória do Agent
# ---------------------------------------------------------------------------

class KondoAIResult(BaseModel):
    answer: str
    action_taken: Literal[
        "none",
        "expense_added",
        "announcement_created",
        "ticket_opened",
        "ticket_status_updated",
    ] = "none"
    entity_id: int | None = None


# ---------------------------------------------------------------------------
# System prompts — um por perfil, sem vazar ferramentas nem dados restritos
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_SINDICO = """
Voce e o Kondo IA, copiloto operacional do sindico.
Responda sempre em portugues do Brasil, com objetividade e foco em decisao.

Seu perfil e SINDICO. Voce tem acesso completo ao sistema.

Ferramentas disponiveis:
- listar_categorias_despesa: lista categorias validas de despesa
- listar_status_chamado: lista status validos de chamado
- adicionar_despesa: registra despesa no financeiro
- criar_comunicado: cria ou publica comunicado para moradores
- abrir_chamado: abre novo chamado operacional
- atualizar_status_chamado: avanca status de chamado no Kanban

Diretrizes:
- Use ferramentas quando o usuario pedir uma acao clara ("adiciona", "registra", "cria", "abre", "publica", "muda status").
- Para despesas acima de R$5.000 ou publicacoes imediatas, confirme os dados antes de executar.
- Nunca finja ter executado uma acao. Informe sempre o resultado real da ferramenta.
- No campo action_taken do resultado, informe a acao executada (ou "none" se nenhuma tool foi chamada).
- No campo entity_id, informe o id da entidade criada/atualizada (ou null).
""".strip()

_SYSTEM_PROMPT_CONSELHO = """
Voce e o Kondo IA, assistente do membro do conselho.
Responda sempre em portugues do Brasil, com objetividade e foco em governanca.

Seu perfil e CONSELHO. Voce pode consultar financeiro, criar comunicados e abrir chamados.
Voce NAO pode adicionar despesas nem alterar status de chamados.

Ferramentas disponiveis:
- listar_categorias_despesa: lista categorias validas (somente consulta)
- listar_status_chamado: lista status validos (somente consulta)
- criar_comunicado: cria ou publica comunicado para moradores
- abrir_chamado: abre novo chamado operacional

Diretrizes:
- Foque em transparencia, resumos financeiros e governanca.
- Para comunicados, confirme audiencia e tom antes de publicar.
- No campo action_taken, informe a acao executada (ou "none").
- No campo entity_id, informe o id da entidade criada (ou null).
""".strip()

_SYSTEM_PROMPT_MORADOR = """
Voce e o Kondo IA, assistente do morador.
Responda sempre em portugues do Brasil, de forma simples e direta.

Seu perfil e MORADOR. Voce so pode abrir chamados da sua propria unidade.
Voce NAO tem acesso a dados financeiros do condominio, nao pode criar comunicados e nao pode alterar status de chamados.

Ferramentas disponiveis:
- abrir_chamado: abre um chamado para a sua unidade (somente sua unidade)

Diretrizes:
- Ajude o morador a descrever o problema com clareza para abrir o chamado corretamente.
- Se perguntarem sobre financas do condominio, informe que esses dados sao restritos a gestao.
- Nunca revele dados financeiros, inadimplencia ou informacoes de outras unidades.
- No campo action_taken, use "ticket_opened" se abriu chamado, caso contrario "none".
- No campo entity_id, informe o id do chamado criado (ou null).
""".strip()

_SYSTEM_PROMPTS: dict[str, str] = {
    "sindico": _SYSTEM_PROMPT_SINDICO,
    "conselho": _SYSTEM_PROMPT_CONSELHO,
    "morador": _SYSTEM_PROMPT_MORADOR,
}

ROLE_TO_PROFILE: dict[str, str] = {
    "manager": "sindico",
    "board_member": "conselho",
    "resident": "morador",
}

VALID_TICKET_STATUSES = {
    "received", "in_review", "vendor_contacted",
    "waiting_approval", "in_progress", "resolved",
}

VALID_EXPENSE_CATEGORIES = {
    "manutencao", "limpeza", "seguranca", "agua", "energia",
    "gas", "seguro", "administrativo", "obras", "outros",
}


# ---------------------------------------------------------------------------
# Deps — injetado em todas as tools via RunContext
# ---------------------------------------------------------------------------

@dataclass
class KondoDeps:
    db: Session
    condominium_id: int
    unit_id: int | None   # unidade do membro logado (None = sem unidade vinculada)
    user_id: int          # id do usuário autenticado — para AuditEvent e created_by
    profile: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _money(value: Decimal | int | float | None) -> str:
    amount = Decimal(value or 0)
    return f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _audit(
    db: Session,
    deps: KondoDeps,
    action: str,
    entity_type: str,
    entity_id: int,
    meta: dict | None = None,
) -> None:
    db.add(AuditEvent(
        condominium_id=deps.condominium_id,
        actor_user_id=deps.user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        event_metadata=meta or {},
    ))
    db.commit()


def _profile_for_user(db: Session, current_user: User, requested_profile: str | None) -> str:
    memberships = (
        db.query(Membership)
        .filter(Membership.user_id == current_user.id, Membership.status == "active")
        .order_by(Membership.created_at.asc())
        .all()
    )
    allowed_profiles = {ROLE_TO_PROFILE.get(m.role) for m in memberships}
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
        t for t in tickets
        if t.status not in {"resolved", "closed"}
        and t.priority in {"high", "critical", "alta", "critica"}
    ]

    documents_count = 0
    announcements_count = 0
    if condominium_id is not None:
        documents_count = (
            db.query(Document).filter(Document.condominium_id == condominium_id).count()
        )
        announcements_count = (
            db.query(Announcement)
            .filter(
                Announcement.condominium_id == condominium_id,
                Announcement.status == "published",
            )
            .count()
        )

    context: dict = {
        "profile": profile,
        "tickets_total": len(tickets),
        "critical_tickets": [t.title for t in critical_tickets[:4]],
        "documents_count": documents_count,
        "announcements_count": announcements_count,
    }

    # Dados financeiros: somente sindico e conselho
    if profile in {"sindico", "conselho"}:
        received = db.query(func.sum(Revenue.amount)).filter(Revenue.status == "paid")
        expected = db.query(func.sum(Revenue.amount))
        expenses_q = db.query(func.sum(Expense.amount))
        delinquencies = db.query(func.sum(Delinquency.amount_due))
        if condominium_id is not None:
            received = received.filter(Revenue.condominium_id == condominium_id)
            expected = expected.filter(Revenue.condominium_id == condominium_id)
            expenses_q = expenses_q.filter(Expense.condominium_id == condominium_id)
            delinquencies = delinquencies.join(Delinquency.unit).filter_by(
                condominium_id=condominium_id
            )

        received_total = received.scalar() or Decimal("0.00")
        expenses_total = expenses_q.scalar() or Decimal("0.00")
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

    if any(t in text for t in ["chamado", "manutenc", "problema", "prioridade"]):
        actions.append(AIChatAction(label="Abrir chamados", to="/chamados"))
    if profile in {"sindico", "conselho"} and any(
        t in text for t in ["financ", "despesa", "caixa", "inadimpl", "acordo"]
    ):
        actions.append(AIChatAction(label="Abrir financeiro", to="/financeiro"))
    if profile in {"sindico", "conselho"} and any(
        t in text for t in ["conselho", "transpar", "resumo"]
    ):
        actions.append(AIChatAction(label="Abrir conselho", to="/conselho"))
    if any(t in text for t in ["document", "comunic"]):
        actions.append(AIChatAction(label="Abrir documentos", to="/documentos"))
    if profile == "morador":
        actions.append(AIChatAction(label="Abrir portal", to="/morador"))
    elif not actions:
        actions.append(AIChatAction(label="Central do sindico", to="/sindico"))
    actions.append(AIChatAction(label="Dashboard", to="/"))

    unique: list[AIChatAction] = []
    seen: set[str] = set()
    for action in actions:
        key = f"{action.label}:{action.to}"
        if key not in seen:
            unique.append(action)
            seen.add(key)
    return unique[:4]


# ---------------------------------------------------------------------------
# ChatSession — persistência de histórico nativo do pydantic-ai
# ---------------------------------------------------------------------------

def _load_session(
    db: Session,
    session_id: int | None,
    user_id: int,
    condominium_id: int,
    profile: str,
) -> ChatSession:
    """Carrega sessão existente (validando ownership) ou cria uma nova."""
    if session_id is not None:
        session = db.get(ChatSession, session_id)
        if (
            session is not None
            and session.user_id == user_id
            and session.condominium_id == condominium_id
            and session.status == "active"
        ):
            return session
        # Sessão inválida ou de outro usuário → cria nova silenciosamente

    session = ChatSession(
        user_id=user_id,
        condominium_id=condominium_id,
        profile=profile,
        messages_json=None,
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _save_session(db: Session, session: ChatSession, messages_json: str, last_preview: str) -> None:
    session.messages_json = messages_json
    session.last_message_preview = last_preview[:300]
    db.commit()


# ---------------------------------------------------------------------------
# Agent builder — tools condicionais por perfil + result_type estruturado
# ---------------------------------------------------------------------------

def _build_agent_with_tools(deps: KondoDeps):
    """
    Constrói o Agent com:
    - result_type=KondoAIResult (saída estruturada obrigatória)
    - tools filtradas pelo perfil (morador só vê abrir_chamado)
    - message_history nativo via session.messages_json
    - AuditEvent em cada tool de escrita
    """
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models.anthropic import AnthropicModel
    from pydantic_ai.providers.anthropic import AnthropicProvider

    settings = get_settings()
    model = AnthropicModel(
        settings.ai_model,
        provider=AnthropicProvider(api_key=settings.anthropic_api_key),
    )
    system_prompt = _SYSTEM_PROMPTS.get(deps.profile, _SYSTEM_PROMPT_MORADOR)

    agent: Agent[KondoDeps, KondoAIResult] = Agent(
        model,
        deps_type=KondoDeps,
        output_type=KondoAIResult,
        system_prompt=system_prompt,
    )

    # ------------------------------------------------------------------ #
    # READ tools — plain, todos os perfis
    # ------------------------------------------------------------------ #

    @agent.tool_plain
    def listar_categorias_despesa() -> str:
        """Retorna as categorias válidas para registro de despesa."""
        return "Categorias disponíveis: " + ", ".join(sorted(VALID_EXPENSE_CATEGORIES))

    @agent.tool_plain
    def listar_status_chamado() -> str:
        """Retorna os status válidos para atualização de chamado no Kanban."""
        return "Status válidos: " + ", ".join(sorted(VALID_TICKET_STATUSES))

    # ------------------------------------------------------------------ #
    # abrir_chamado — todos os perfis, ownership enforced para morador
    # ------------------------------------------------------------------ #

    @agent.tool
    def abrir_chamado(
        ctx: RunContext[KondoDeps],
        titulo: str,
        descricao: str,
        localizacao: str,
        unit_id: int,
    ) -> str:
        """
        Abre um novo chamado operacional e cria o WorkItem no Kanban automaticamente.

        Args:
            titulo: Título curto do problema (ex: "Vazamento no corredor bloco B").
            descricao: Descrição detalhada do que está acontecendo.
            localizacao: Local exato (ex: "Corredor 3º andar bloco B").
            unit_id: ID da unidade que reporta o chamado.
        """
        # Morador só pode abrir chamado na própria unidade
        if ctx.deps.profile == "morador":
            if ctx.deps.unit_id is None:
                return "Sua conta não possui unidade vinculada. Contate o síndico."
            if unit_id != ctx.deps.unit_id:
                return (
                    f"Acesso negado: como morador, você só pode abrir chamados "
                    f"para sua unidade (id={ctx.deps.unit_id})."
                )

        db = ctx.deps.db
        unit = db.get(Unit, unit_id)
        if unit is None:
            return f"Unidade id={unit_id} não encontrada."
        if unit.condominium_id != ctx.deps.condominium_id:
            return "Acesso negado: unidade pertence a outro condomínio."

        if len(titulo.strip()) < 3:
            return "O título do chamado deve ter pelo menos 3 caracteres."
        if len(descricao.strip()) < 5:
            return "A descrição deve ter pelo menos 5 caracteres."

        ticket = Ticket(
            condominium_id=ctx.deps.condominium_id,
            unit_id=unit_id,
            created_by_user_id=ctx.deps.user_id,
            title=titulo.strip(),
            description=descricao.strip(),
            location=localizacao.strip(),
            status="received",
        )
        db.add(ticket)
        db.flush()

        from app.models import WorkItem as WorkItemModel
        db.add(WorkItemModel(
            condominium_id=ctx.deps.condominium_id,
            ticket_id=ticket.id,
            type="ticket",
            title=titulo.strip(),
            description=descricao.strip(),
            status="received",
            priority="medium",
            source_type="ticket",
            source_id=ticket.id,
        ))
        db.commit()
        db.refresh(ticket)

        _audit(db, ctx.deps, "ai.ticket.created", "ticket", ticket.id, {
            "titulo": titulo, "via": "ai_chat",
        })

        return (
            f"Chamado aberto (id={ticket.id}): '{titulo}', "
            f"local '{localizacao}', status 'received'. WorkItem criado no Kanban."
        )

    # ------------------------------------------------------------------ #
    # Tools exclusivas de sindico e conselho
    # ------------------------------------------------------------------ #

    if deps.profile in {"sindico", "conselho"}:

        @agent.tool
        def criar_comunicado(
            ctx: RunContext[KondoDeps],
            titulo: str,
            corpo: str,
            audiencia: str,
            publicar: bool,
        ) -> str:
            """
            Cria um comunicado para moradores ou gestão.

            Args:
                titulo: Título do comunicado (mínimo 5 caracteres).
                corpo: Texto completo do comunicado.
                audiencia: "residents" para moradores, "managers" para gestão interna.
                publicar: True para publicar imediatamente, False para salvar como rascunho.
            """
            from datetime import datetime, timezone

            if len(titulo.strip()) < 5:
                return "O título deve ter pelo menos 5 caracteres."
            if len(corpo.strip()) < 10:
                return "O corpo deve ter pelo menos 10 caracteres."

            audiencia_norm = audiencia.lower().strip()
            if audiencia_norm not in {"residents", "managers"}:
                audiencia_norm = "residents"

            db = ctx.deps.db
            status_val = "published" if publicar else "draft"
            published_at = datetime.now(timezone.utc) if publicar else None

            announcement = Announcement(
                condominium_id=ctx.deps.condominium_id,
                title=titulo.strip(),
                body=corpo.strip(),
                audience=audiencia_norm,
                status=status_val,
                published_at=published_at,
            )
            db.add(announcement)
            db.commit()
            db.refresh(announcement)

            _audit(db, ctx.deps, "ai.announcement.created", "announcement", announcement.id, {
                "titulo": titulo, "status": status_val, "via": "ai_chat",
            })

            estado = "publicado" if publicar else "salvo como rascunho"
            return (
                f"Comunicado {estado} (id={announcement.id}): "
                f"'{titulo}', audiência '{audiencia_norm}'."
            )

    # ------------------------------------------------------------------ #
    # Tools exclusivas de sindico
    # ------------------------------------------------------------------ #

    if deps.profile == "sindico":

        @agent.tool
        def adicionar_despesa(
            ctx: RunContext[KondoDeps],
            descricao: str,
            categoria: str,
            valor: float,
            vencimento: str,
        ) -> str:
            """
            Registra uma nova despesa no financeiro do condomínio.

            Args:
                descricao: Descrição clara (ex: "Manutenção portão bloco A").
                categoria: Categoria. Use listar_categorias_despesa() para opções válidas.
                valor: Valor em reais, número positivo (ex: 1500.00).
                vencimento: Data de vencimento no formato YYYY-MM-DD (ex: "2026-07-10").
            """
            categoria_norm = categoria.lower().strip()
            if categoria_norm not in VALID_EXPENSE_CATEGORIES:
                return (
                    f"Categoria '{categoria}' inválida. "
                    f"Opções: {', '.join(sorted(VALID_EXPENSE_CATEGORIES))}."
                )

            try:
                due = date.fromisoformat(vencimento)
            except ValueError:
                return f"Data '{vencimento}' inválida. Use o formato YYYY-MM-DD."

            if valor <= 0:
                return "O valor deve ser maior que zero."

            db = ctx.deps.db
            expense = Expense(
                condominium_id=ctx.deps.condominium_id,
                description=descricao.strip(),
                category=categoria_norm,
                amount=Decimal(str(valor)).quantize(Decimal("0.01")),
                due_date=due,
                status="pending",
            )
            db.add(expense)
            db.commit()
            db.refresh(expense)

            _audit(db, ctx.deps, "ai.expense.created", "expense", expense.id, {
                "descricao": descricao, "valor": str(expense.amount), "via": "ai_chat",
            })

            return (
                f"Despesa registrada (id={expense.id}): '{descricao}', "
                f"categoria '{categoria_norm}', {_money(expense.amount)}, "
                f"vencimento {due.strftime('%d/%m/%Y')}."
            )

        @agent.tool
        def atualizar_status_chamado(
            ctx: RunContext[KondoDeps],
            ticket_id: int,
            novo_status: str,
        ) -> str:
            """
            Atualiza o status de um chamado e sincroniza o WorkItem no Kanban.

            Args:
                ticket_id: ID do chamado a atualizar.
                novo_status: Novo status. Use listar_status_chamado() para opções válidas.
            """
            status_norm = novo_status.lower().strip()
            if status_norm not in VALID_TICKET_STATUSES:
                return (
                    f"Status '{novo_status}' inválido. "
                    f"Opções: {', '.join(sorted(VALID_TICKET_STATUSES))}."
                )

            db = ctx.deps.db
            ticket = db.get(Ticket, ticket_id)
            if ticket is None:
                return f"Chamado id={ticket_id} não encontrado."
            if ticket.condominium_id != ctx.deps.condominium_id:
                return "Acesso negado: chamado pertence a outro condomínio."

            status_anterior = ticket.status
            ticket.status = status_norm
            for item in ticket.work_items:
                item.status = status_norm
            db.commit()

            _audit(db, ctx.deps, "ai.ticket.status_updated", "ticket", ticket_id, {
                "de": status_anterior, "para": status_norm, "via": "ai_chat",
            })

            return (
                f"Status do chamado id={ticket_id} atualizado: "
                f"'{status_anterior}' → '{status_norm}'. Kanban sincronizado."
            )

    return agent


# ---------------------------------------------------------------------------
# Prompt builder — contexto sanitizado por perfil
# ---------------------------------------------------------------------------

def _build_prompt(payload: AIChatRequest, context: dict) -> str:
    profile = context["profile"]
    # Morador nunca recebe dados financeiros no prompt, mesmo que o dict os contenha
    safe_context = {
        k: v for k, v in context.items()
        if not (k == "finance" and profile == "morador")
    }
    return (
        f"Perfil ativo: {profile}\n"
        f"Rota atual: {payload.route or 'nao informada'}\n"
        f"Contexto operacional: {safe_context}\n"
        f"Mensagem do usuario: {payload.message}\n"
        "Responda em ate 2 paragrafos objetivos. "
        "Preencha action_taken e entity_id corretamente no resultado estruturado."
    )


# ---------------------------------------------------------------------------
# Anthropic runner — message_history nativo + sessão persistida
# ---------------------------------------------------------------------------

async def _run_anthropic_agent(
    payload: AIChatRequest,
    context: dict,
    deps: KondoDeps,
    session: ChatSession,
) -> tuple[KondoAIResult, list[AIChatToolCall], str]:
    """
    Executa o agent com histórico nativo do pydantic-ai.
    Retorna (result, tool_calls, messages_json_atualizado).
    """
    from pydantic_ai.messages import ModelMessagesTypeAdapter

    settings = get_settings()
    agent = _build_agent_with_tools(deps)
    prompt = _build_prompt(payload, context)

    # Carrega histórico serializado da sessão
    message_history = None
    if session.messages_json:
        try:
            message_history = ModelMessagesTypeAdapter.validate_json(session.messages_json)
        except Exception:
            message_history = None  # corrompido → começa do zero

    run_kwargs: dict = {"deps": deps}
    if message_history:
        run_kwargs["message_history"] = message_history

    result = await asyncio.wait_for(
        agent.run(prompt, **run_kwargs),
        timeout=settings.ai_timeout_seconds,
    )

    # Serializa histórico completo atualizado
    updated_messages_json = result.all_messages_json().decode()

    # Extrai tool calls do histórico de mensagens para o response
    tool_calls: list[AIChatToolCall] = []
    for msg in result.all_messages():
        if not hasattr(msg, "parts"):
            continue
        for part in msg.parts:
            part_type = type(part).__name__
            if part_type == "ToolCallPart":
                tool_calls.append(AIChatToolCall(
                    tool=getattr(part, "tool_name", "desconhecida"),
                    summary=str(getattr(part, "args", ""))[:120],
                ))
            elif part_type == "ToolReturnPart" and tool_calls:
                # Substitui summary pelo retorno real da tool
                tool_calls[-1] = AIChatToolCall(
                    tool=tool_calls[-1].tool,
                    summary=str(getattr(part, "content", ""))[:200],
                )

    return result.output, tool_calls, updated_messages_json


# ---------------------------------------------------------------------------
# Mock fallback — por perfil, com detecção de intenção de escrita
# ---------------------------------------------------------------------------

def _mock_answer(payload: AIChatRequest, context: dict) -> str:
    profile = context["profile"]
    text = payload.message.lower()
    critical = context["critical_tickets"]
    finance = context.get("finance", {})

    if profile == "morador":
        if any(t in text for t in ["financ", "despesa", "caixa", "inadimpl", "acordo", "boleto"]):
            return (
                "Dados financeiros do condomínio são restritos à gestão. "
                "Posso te ajudar com seus chamados, comunicados e regras."
            )
        if any(t in text for t in ["abre", "cria", "registra"]) and "chamado" in text:
            return (
                "[Simulado — configure ANTHROPIC_API_KEY para eu abrir o chamado diretamente] "
                "Descreva o problema e a localização."
            )
        return (
            f"Você tem {context['tickets_total']} chamado(s) registrado(s). "
            "Descreva o problema e eu ajudo a abrir um chamado claro."
        )

    if profile == "conselho":
        if any(t in text for t in ["adiciona", "registra"]) and any(
            t in text for t in ["despesa", "gasto"]
        ):
            return "Registro de despesas é exclusivo do síndico."
        if any(t in text for t in ["muda", "atualiza"]) and "status" in text:
            return "Alteração de status de chamado é exclusiva do síndico."
        if any(t in text for t in ["cria", "publica"]) and any(
            t in text for t in ["comunic", "aviso"]
        ):
            return (
                "[Simulado — configure ANTHROPIC_API_KEY para eu criar o comunicado] "
                "Informe título, corpo, audiência e se publica agora."
            )
        if finance:
            return (
                f"Resumo: receita {finance.get('received_revenue')}, "
                f"despesas {finance.get('expenses')}, caixa {finance.get('cash_gap')}, "
                f"inadimplência {finance.get('delinquency_total')}."
            )

    # sindico
    if any(t in text for t in ["adiciona", "registra", "lança"]) and any(
        t in text for t in ["despesa", "gasto"]
    ):
        return (
            "[Simulado — configure ANTHROPIC_API_KEY para registrar a despesa] "
            "Informe: descrição, categoria, valor e data de vencimento."
        )
    if any(t in text for t in ["cria", "publica"]) and any(
        t in text for t in ["comunic", "aviso"]
    ):
        return (
            "[Simulado — configure ANTHROPIC_API_KEY para criar o comunicado] "
            "Informe: título, corpo, audiência e se publica agora."
        )
    if any(t in text for t in ["muda", "atualiza", "fecha", "resolve"]) and any(
        t in text for t in ["chamado", "status"]
    ):
        return (
            "[Simulado — configure ANTHROPIC_API_KEY para atualizar o status] "
            "Informe o ID do chamado e o novo status."
        )
    if finance and any(t in text for t in ["financ", "despesa", "caixa", "inadimpl"]):
        return (
            f"Receita {finance.get('received_revenue')}, despesas {finance.get('expenses')}, "
            f"caixa {finance.get('cash_gap')}, inadimplência {finance.get('delinquency_total')}. "
            "Priorize acordos e revise as maiores despesas."
        )
    if critical:
        return f"Chamados críticos: {', '.join(critical)}. Resolva o maior impacto primeiro."

    return (
        f"{len(critical)} chamado(s) crítico(s), caixa {finance.get('cash_gap', 'indisponível')}. "
        "Me diga se quer foco em financeiro, chamados, comunicados ou resumo para o conselho."
    )


# ---------------------------------------------------------------------------
# Entry point público
# ---------------------------------------------------------------------------

async def chat_with_kondo_ai(db: Session, current_user: User, payload: AIChatRequest) -> AIChatResponse:
    settings = get_settings()
    profile = _profile_for_user(db, current_user, payload.profile)
    context = _context_for_user(db, current_user, profile)
    actions = _actions_for(payload.message, profile)

    membership = get_active_membership(db, current_user)
    if membership is None and not current_user.is_platform_admin:
        return AIChatResponse(
            answer="Sua conta não possui vínculo ativo com um condomínio. Contate o administrador.",
            actions=[],
            tool_calls=[],
            confidence="low",
            source="mock",
            provider="mock",
            model="mock",
        )

    condominium_id = membership.condominium_id if membership else 1
    unit_id = membership.unit_id if membership else None

    can_use_anthropic = (
        settings.ai_provider == "anthropic"
        and bool(settings.anthropic_api_key)
        and bool(settings.ai_model)
    )

    if can_use_anthropic:
        try:
            session = _load_session(
                db,
                session_id=payload.session_id,
                user_id=current_user.id,
                condominium_id=condominium_id,
                profile=profile,
            )
            deps = KondoDeps(
                db=db,
                condominium_id=condominium_id,
                unit_id=unit_id,
                user_id=current_user.id,
                profile=profile,
            )
            ai_result, tool_calls, updated_json = await _run_anthropic_agent(
                payload, context, deps, session
            )
            _save_session(db, session, updated_json, ai_result.answer)

            return AIChatResponse(
                answer=ai_result.answer,
                actions=actions,
                tool_calls=tool_calls,
                confidence="high" if tool_calls else "medium",
                source="ai",
                provider="anthropic",
                model=settings.ai_model,
                session_id=session.id,
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "AI agent failed, falling back to mock. %s: %s",
                type(exc).__name__,
                exc,
            )
            if not settings.ai_enable_mock_fallback:
                raise

    return AIChatResponse(
        answer=_mock_answer(payload, context),
        actions=actions,
        tool_calls=[],
        confidence="medium" if context["tickets_total"] or context.get("finance") else "low",
        source="mock",
        provider=settings.ai_provider if can_use_anthropic else "mock",
        model=settings.ai_model if can_use_anthropic else "mock",
        session_id=None,
    )
