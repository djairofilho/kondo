from datetime import datetime, timezone

from app.schemas.tickets import Ticket, TicketAIClassification, TicketCreate


_tickets: list[Ticket] = [
    Ticket(
        id=1,
        unit_id=304,
        title="Vazamento na garagem",
        description="Vazamento forte na garagem B2 perto do quadro eletrico.",
        location="Garagem B2",
        status="recebido",
        category="hidraulica",
        priority="alta",
        ai_analysis=TicketAIClassification(
            category="hidraulica",
            priority="alta",
            risk="risco eletrico",
            suggested_owner="zelador e fornecedor hidraulico",
            next_action="Isolar a area e acionar fornecedor imediatamente.",
        ),
        created_at=datetime.now(timezone.utc),
    ),
    Ticket(
        id=2,
        unit_id=1202,
        title="Lampada queimada",
        description="Lampada queimada no corredor do 12 andar.",
        location="12 andar",
        status="em analise",
        created_at=datetime.now(timezone.utc),
    ),
]


def list_tickets() -> list[Ticket]:
    return _tickets


def get_ticket(ticket_id: int) -> Ticket | None:
    return next((ticket for ticket in _tickets if ticket.id == ticket_id), None)


def create_ticket(payload: TicketCreate) -> Ticket:
    ticket = Ticket(
        id=max((ticket.id for ticket in _tickets), default=0) + 1,
        unit_id=payload.unit_id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        status="recebido",
        created_at=datetime.now(timezone.utc),
    )
    _tickets.append(ticket)
    return ticket


def update_ticket_ai_analysis(ticket_id: int, classification: TicketAIClassification) -> None:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        return

    ticket.ai_analysis = classification
    ticket.category = classification.category
    ticket.priority = classification.priority

