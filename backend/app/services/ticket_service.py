from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Ticket as TicketModel
from app.models import WorkItem
from app.schemas.tickets import TicketAIClassification, TicketCreate, TicketStatusUpdate, TicketUpdate


def list_tickets(db: Session) -> list[TicketModel]:
    return db.query(TicketModel).order_by(TicketModel.created_at.desc()).all()


def get_ticket(db: Session, ticket_id: int) -> TicketModel | None:
    return db.get(TicketModel, ticket_id)


def get_ticket_or_404(db: Session, ticket_id: int) -> TicketModel:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def create_ticket(db: Session, payload: TicketCreate) -> TicketModel:
    ticket = TicketModel(
        condominium_id=payload.condominium_id,
        unit_id=payload.unit_id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        status="received",
    )
    db.add(ticket)
    db.flush()

    db.add(
        WorkItem(
            condominium_id=payload.condominium_id,
            ticket_id=ticket.id,
            type="ticket",
            title=payload.title,
            description=payload.description,
            status="received",
            priority="medium",
            source_type="ticket",
            source_id=ticket.id,
        )
    )
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(db: Session, ticket_id: int, payload: TicketUpdate) -> TicketModel:
    ticket = get_ticket_or_404(db, ticket_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket_id: int, payload: TicketStatusUpdate) -> TicketModel:
    ticket = get_ticket_or_404(db, ticket_id)
    ticket.status = payload.status
    for item in ticket.work_items:
        item.status = payload.status
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_ai_analysis(db: Session, ticket_id: int, classification: TicketAIClassification) -> None:
    ticket = get_ticket_or_404(db, ticket_id)

    ticket.ai_analysis = classification.model_dump()
    ticket.category = classification.category
    ticket.priority = classification.priority
    for item in ticket.work_items:
        item.priority = "high" if classification.priority == "alta" else "medium"
    db.commit()

