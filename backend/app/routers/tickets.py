from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tickets import Ticket, TicketAIClassification, TicketAssign, TicketComment, TicketCommentCreate, TicketCreate, TicketStatusUpdate, TicketUpdate
from app.services.ai_service import classify_ticket
from app.services.ticket_service import (
    create_ticket,
    create_ticket_comment,
    assign_ticket,
    get_ticket_or_404,
    list_ticket_comments,
    list_tickets,
    update_ticket,
    update_ticket_ai_analysis,
    update_ticket_status,
)


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[Ticket])
def get_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    return list_tickets(db)


@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket_route(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    return create_ticket(db, payload)


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket_route(ticket_id: int, db: Session = Depends(get_db)) -> Ticket:
    return get_ticket_or_404(db, ticket_id)


@router.patch("/{ticket_id}", response_model=Ticket)
def patch_ticket_route(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)) -> Ticket:
    return update_ticket(db, ticket_id, payload)


@router.patch("/{ticket_id}/status", response_model=Ticket)
def patch_ticket_status_route(ticket_id: int, payload: TicketStatusUpdate, db: Session = Depends(get_db)) -> Ticket:
    return update_ticket_status(db, ticket_id, payload)


@router.patch("/{ticket_id}/assign", response_model=Ticket)
def patch_ticket_assign_route(ticket_id: int, payload: TicketAssign, db: Session = Depends(get_db)) -> Ticket:
    return assign_ticket(db, ticket_id, payload)


@router.get("/{ticket_id}/comments", response_model=list[TicketComment])
def get_ticket_comments_route(ticket_id: int, db: Session = Depends(get_db)) -> list[TicketComment]:
    return list_ticket_comments(db, ticket_id)


@router.post("/{ticket_id}/comments", response_model=TicketComment)
def post_ticket_comment_route(ticket_id: int, payload: TicketCommentCreate, db: Session = Depends(get_db)) -> TicketComment:
    return create_ticket_comment(db, ticket_id, payload)


@router.post("/{ticket_id}/classify-ai", response_model=TicketAIClassification)
def classify_ticket_route(ticket_id: int, db: Session = Depends(get_db)) -> TicketAIClassification:
    ticket = get_ticket_or_404(db, ticket_id)
    classification = classify_ticket(ticket)
    update_ticket_ai_analysis(db, ticket_id, classification)
    return classification

