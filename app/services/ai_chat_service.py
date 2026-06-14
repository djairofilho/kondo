import asyncio
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import UploadFile
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
    Resident,
    Revenue,
    Ticket,
    Unit,
    User,
)
from app.schemas.ai_chat import AIChatAction, AIChatAttachmentRef, AIChatRequest, AIChatResponse, AIChatToolCall


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
- Para despesas acima de R$5.000, publicacoes imediatas e chamados marcados como resolvidos, confirme os dados antes de executar.
- Confirmar significa que o usuario respondeu explicitamente algo como "Confirmo, pode executar"; listar dados para revisao nao e confirmacao.
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
- Para comunicados, confirme audiencia e tom antes de publicar. Confirmar exige resposta explicita do usuario.
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

IMPORTANTE sobre abrir_chamado:
- A unidade do morador ja esta identificada no sistema — NUNCA peca o numero do apartamento, bloco ou ID de unidade.
- Para abrir o chamado voce precisa apenas de: titulo (curto), descricao do problema e localizacao exata dentro do condominio (ex: "banheiro da suite", "corredor do 3o andar").
- Se o morador ja descreveu o problema com clareza suficiente, abra o chamado diretamente sem fazer mais perguntas.
- So peca mais detalhes se a descricao for realmente insuficiente para entender o problema.

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
    user_message: str


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
    entity_id: int | None,
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


def _audit_guardrail(
    db: Session,
    condominium_id: int | None,
    user_id: int | None,
    reason: str,
    profile: str,
    meta: dict | None = None,
) -> None:
    db.add(AuditEvent(
        condominium_id=condominium_id,
        actor_user_id=user_id,
        action="ai.guardrail.blocked",
        entity_type="ai_chat",
        entity_id=None,
        event_metadata={"reason": reason, "profile": profile, **(meta or {})},
    ))
    db.commit()


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def _has_explicit_confirmation(message: str) -> bool:
    text = _normalize_text(message)
    cancellation_phrases = (
        "nao confirmo",
        "sem confirmar",
        "nao execute",
        "nao publique",
        "nao registre",
        "nao altere",
    )
    confirmation_phrases = (
        "confirmo",
        "pode executar",
        "pode registrar",
        "pode publicar",
        "pode alterar",
        "pode fechar",
        "pode resolver",
        "autorizo",
        "esta confirmado",
        "sim, execute",
        "sim execute",
        "sim, pode",
        "sim pode",
    )
    return any(phrase in text for phrase in confirmation_phrases) and not any(
        phrase in text for phrase in cancellation_phrases
    )


def _confirmation_required(deps: KondoDeps, operation: str, details: dict) -> str:
    _audit(
        deps.db,
        deps,
        "ai.guardrail.confirmation_required",
        "ai_chat",
        None,
        {"operation": operation, "details": details},
    )
    detail_text = "; ".join(f"{key}: {value}" for key, value in details.items())
    return (
        f"Confirmacao necessaria antes de executar '{operation}'. "
        f"Revise os dados ({detail_text}) e responda com uma confirmacao explicita, "
        "por exemplo: 'Confirmo, pode executar'. Nenhuma alteracao foi gravada."
    )


def _blocked_response(
    db: Session,
    condominium_id: int | None,
    user_id: int | None,
    profile: str,
    reason: str,
    answer: str,
) -> AIChatResponse:
    _audit_guardrail(db, condominium_id, user_id, reason, profile)
    return AIChatResponse(
        answer=answer,
        actions=_actions_for("", profile),
        tool_calls=[AIChatToolCall(tool="guardrail", summary=reason)],
        attachments=[],
        confidence="high",
        source="mock",
        provider="guardrail",
        model="policy",
    )


def _preflight_guardrail(
    db: Session,
    current_user: User,
    condominium_id: int | None,
    profile: str,
    message: str,
) -> AIChatResponse | None:
    text = _normalize_text(message)
    finance_terms = ("finance", "despesa", "caixa", "inadimpl", "acordo", "boleto", "receita")
    write_terms = (
        "adiciona",
        "adicione",
        "registra",
        "registre",
        "lanca",
        "cria despesa",
        "crie despesa",
        "crie uma despesa",
    )
    status_terms = (
        "muda status",
        "alterar status",
        "atualiza status",
        "fecha chamado",
        "fechar chamado",
        "resolve chamado",
        "resolver chamado",
    )

    if profile == "morador" and any(term in text for term in finance_terms):
        return _blocked_response(
            db,
            condominium_id,
            current_user.id,
            profile,
            "resident_finance_access_denied",
            "Dados financeiros do condominio sao restritos a gestao. Posso te ajudar com chamados, comunicados e regras da sua unidade.",
        )

    if profile == "morador" and any(term in text for term in ("comunicado", "aviso")) and any(
        term in text for term in ("cria", "publique", "publica", "envia")
    ):
        return _blocked_response(
            db,
            condominium_id,
            current_user.id,
            profile,
            "resident_announcement_write_denied",
            "Moradores nao podem criar ou publicar comunicados pela IA. Posso ajudar a escrever uma sugestao para enviar a gestao.",
        )

    if profile == "conselho" and any(term in text for term in write_terms) and any(
        term in text for term in ("despesa", "gasto")
    ):
        return _blocked_response(
            db,
            condominium_id,
            current_user.id,
            profile,
            "board_expense_write_denied",
            "Registro de despesas e exclusivo do sindico. Posso revisar os dados e preparar uma recomendacao para aprovacao.",
        )

    if profile == "conselho" and any(term in text for term in status_terms):
        return _blocked_response(
            db,
            condominium_id,
            current_user.id,
            profile,
            "board_ticket_status_write_denied",
            "Alteracao de status de chamados e exclusiva do sindico. Posso ajudar a montar uma recomendacao para a gestao.",
        )

    return None


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

    if profile == "morador" and unit_id is not None:
        unit = db.get(Unit, unit_id)
        if unit is not None:
            context["unit_number"] = unit.number
            context["unit_block"] = unit.block or ""
            resident = (
                db.query(Resident)
                .filter(Resident.unit_id == unit_id, Resident.status == "active")
                .order_by(Resident.created_at.asc())
                .first()
            )
            if resident:
                context["resident_name"] = resident.name

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
    elif profile == "conselho" and not actions:
        actions.append(AIChatAction(label="Abrir conselho", to="/conselho"))
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
    # abrir_chamado para MORADOR — unit_id resolvido automaticamente
    # ------------------------------------------------------------------ #

    if deps.profile == "morador":

        @agent.tool
        def abrir_chamado(
            ctx: RunContext[KondoDeps],
            titulo: str,
            descricao: str,
            localizacao: str,
        ) -> str:
            """
            Abre um chamado para a unidade do morador logado. A unidade é resolvida automaticamente.

            Args:
                titulo: Resumo curto do problema (ex: "Vazamento no banheiro").
                descricao: Descrição do que está acontecendo.
                localizacao: Local exato dentro do apartamento ou condomínio (ex: "banheiro da suíte", "corredor do 3º andar").
            """
            if ctx.deps.unit_id is None:
                return "Sua conta não possui unidade vinculada. Contate o síndico."

            db = ctx.deps.db
            unit = db.get(Unit, ctx.deps.unit_id)
            if unit is None or unit.condominium_id != ctx.deps.condominium_id:
                return "Unidade não encontrada ou pertence a outro condomínio."

            if len(titulo.strip()) < 3:
                return "O título deve ter pelo menos 3 caracteres."
            if len(descricao.strip()) < 5:
                return "A descrição deve ter pelo menos 5 caracteres."
            if len(localizacao.strip()) < 3:
                return "A localização deve ter pelo menos 3 caracteres."

            ticket = Ticket(
                condominium_id=ctx.deps.condominium_id,
                unit_id=ctx.deps.unit_id,
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
    # abrir_chamado para SINDICO/CONSELHO — recebe unit_id explícito
    # ------------------------------------------------------------------ #

    if deps.profile in {"sindico", "conselho"}:

        @agent.tool
        def abrir_chamado(  # noqa: F811
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
            if len(localizacao.strip()) < 3:
                return "A localização deve ter pelo menos 3 caracteres."

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
    # READ tools — plain, sindico e conselho apenas
    # ------------------------------------------------------------------ #

    if deps.profile in {"sindico", "conselho"}:

        @agent.tool_plain
        def listar_categorias_despesa() -> str:
            """Retorna as categorias válidas para registro de despesa."""
            return "Categorias disponíveis: " + ", ".join(sorted(VALID_EXPENSE_CATEGORIES))

        @agent.tool_plain
        def listar_status_chamado() -> str:
            """Retorna os status válidos para atualização de chamado no Kanban."""
            return "Status válidos: " + ", ".join(sorted(VALID_TICKET_STATUSES))

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

            if publicar and not _has_explicit_confirmation(ctx.deps.user_message):
                return _confirmation_required(ctx.deps, "publicar_comunicado", {
                    "titulo": titulo.strip(),
                    "audiencia": audiencia_norm,
                    "publicar": publicar,
                })

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

            if valor > 5000 and not _has_explicit_confirmation(ctx.deps.user_message):
                return _confirmation_required(ctx.deps, "registrar_despesa_alta", {
                    "descricao": descricao.strip(),
                    "categoria": categoria_norm,
                    "valor": _money(valor),
                    "vencimento": due.isoformat(),
                })

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

            if status_norm == "resolved" and not _has_explicit_confirmation(ctx.deps.user_message):
                return _confirmation_required(ctx.deps, "resolver_chamado", {
                    "ticket_id": ticket_id,
                    "status_atual": ticket.status,
                    "novo_status": status_norm,
                })

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

def _build_prompt(payload: AIChatRequest, context: dict, file_descriptions: list[str] | None = None) -> str:
    profile = context["profile"]
    safe_context = {
        k: v for k, v in context.items()
        if k not in ("finance",) or profile != "morador"
    }

    unit_line = ""
    if profile == "morador" and context.get("unit_number"):
        block = context.get("unit_block", "")
        unit_ref = f"Bloco {block} - Apto {context['unit_number']}" if block else f"Apto {context['unit_number']}"
        resident_name = context.get("resident_name", "")
        unit_line = f"Unidade do morador: {unit_ref}" + (f" (titular: {resident_name})" if resident_name else "") + "\n"

    base = (
        f"Perfil ativo: {profile}\n"
        f"Rota atual: {payload.route or 'nao informada'}\n"
        + unit_line +
        f"Contexto operacional: {safe_context}\n"
        f"Mensagem do usuario: {payload.message}\n"
    )
    if file_descriptions:
        files_note = "Arquivos enviados junto com esta mensagem:\n" + "\n".join(
            f"- {desc}" for desc in file_descriptions
        ) + "\n"
        base = base + files_note
    return base + (
        "Responda em ate 2 paragrafos objetivos. "
        "Se uma ferramenta retornar confirmacao necessaria, diga que nada foi gravado e peca confirmacao explicita. "
        "Se uma ferramenta negar permissao, explique o limite do perfil sem contornar a regra. "
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
    file_parts: list[tuple[bytes, str]] | None = None,
) -> tuple[KondoAIResult, list[AIChatToolCall], str]:
    from pydantic_ai.messages import ModelMessagesTypeAdapter

    settings = get_settings()
    agent = _build_agent_with_tools(deps)

    file_descriptions = [name for _, name in file_parts] if file_parts else None
    prompt = _build_prompt(payload, context, file_descriptions)

    message_history = None
    if session.messages_json:
        try:
            message_history = ModelMessagesTypeAdapter.validate_json(session.messages_json)
        except Exception:
            message_history = None

    if file_parts:
        from pydantic_ai.messages import BinaryContent
        user_content: list = [prompt]
        for raw_bytes, name in file_parts:
            suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            if suffix in {"jpg", "jpeg"}:
                media_type = "image/jpeg"
            elif suffix == "png":
                media_type = "image/png"
            elif suffix == "webp":
                media_type = "image/webp"
            else:
                media_type = "application/pdf"
            user_content.append(BinaryContent(data=raw_bytes, media_type=media_type))
        run_input = user_content
    else:
        run_input = prompt

    run_kwargs: dict = {"deps": deps}
    if message_history:
        run_kwargs["message_history"] = message_history

    result = await asyncio.wait_for(
        agent.run(run_input, **run_kwargs),
        timeout=settings.ai_timeout_seconds,
    )

    updated_messages_json = result.all_messages_json().decode()

    tool_calls: list[AIChatToolCall] = []
    for msg in result.all_messages():
        if not hasattr(msg, "parts"):
            continue
        for part in msg.parts:
            part_type = type(part).__name__
            if part_type == "ToolCallPart":
                tool_name = getattr(part, "tool_name", "desconhecida")
                if tool_name == "final_result":
                    continue
                tool_calls.append(AIChatToolCall(
                    tool=tool_name,
                    summary=str(getattr(part, "args", ""))[:120],
                ))
            elif part_type == "ToolReturnPart" and tool_calls:
                tool_calls[-1] = AIChatToolCall(
                    tool=tool_calls[-1].tool,
                    summary=str(getattr(part, "content", ""))[:200],
                )

    output = result.output
    # O pydantic-ai usa uma tool interna chamada "final_result" para saída estruturada.
    # O Haiku às vezes vaza o nome dessa tool ou o texto "Final result processed." no
    # campo answer. Sanitizamos aqui antes de retornar ao frontend.
    _ARTIFACTS = (
        "final_result",
        "Final result processed.",
        "final_result\nFinal result processed.",
    )
    clean_answer = output.answer
    for artifact in _ARTIFACTS:
        clean_answer = clean_answer.replace(artifact, "")
    clean_answer = clean_answer.strip()
    if not clean_answer:
        clean_answer = "Processado com sucesso."
    if clean_answer != output.answer:
        output = KondoAIResult(
            answer=clean_answer,
            action_taken=output.action_taken,
            entity_id=output.entity_id,
        )

    return output, tool_calls, updated_messages_json


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

async def chat_with_kondo_ai(
    db: Session,
    current_user: User,
    payload: AIChatRequest,
    files: list[UploadFile] | None = None,
) -> AIChatResponse:
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

    blocked = _preflight_guardrail(db, current_user, condominium_id, profile, payload.message)
    if blocked is not None:
        return blocked

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
                user_message=payload.message,
            )

            attachment_refs: list[AIChatAttachmentRef] = []
            file_parts: list[tuple[bytes, str]] = []

            if files:
                from app.services.attachment_service import create_attachment

                for upload in files:
                    if not upload.filename and not upload.content_type:
                        continue

                    raw = await upload.read()
                    if not raw:
                        continue

                    await upload.seek(0)

                    attachment = await create_attachment(
                        db,
                        upload,
                        condominium_id,
                        "chat_message",
                        session.id,
                        current_user.id,
                        "private",
                    )
                    attachment_refs.append(AIChatAttachmentRef(
                        id=attachment.id,
                        original_file_name=attachment.original_file_name,
                        content_type=attachment.content_type,
                        file_size=attachment.file_size,
                        download_url=f"/attachments/{attachment.id}/download",
                    ))
                    file_parts.append((raw, attachment.original_file_name))

            ai_result, tool_calls, updated_json = await _run_anthropic_agent(
                payload, context, deps, session,
                file_parts=file_parts or None,
            )
            _save_session(db, session, updated_json, ai_result.answer)

            return AIChatResponse(
                answer=ai_result.answer,
                actions=actions,
                tool_calls=tool_calls,
                attachments=attachment_refs,
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
        attachments=[],
        confidence="medium" if context["tickets_total"] or context.get("finance") else "low",
        source="mock",
        provider=settings.ai_provider if can_use_anthropic else "mock",
        model=settings.ai_model if can_use_anthropic else "mock",
        session_id=None,
    )
