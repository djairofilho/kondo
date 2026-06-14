from fastapi import APIRouter, HTTPException, status

from app.schemas.tickets import Ticket, TicketAIClassification, TicketCreate
from app.services.ai_service import classify_ticket
from app.services.ticket_service import create_ticket, get_ticket, list_tickets, update_ticket_ai_analysis


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[Ticket])
def get_tickets() -> list[Ticket]:
    return list_tickets()


@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket_route(payload: TicketCreate) -> Ticket:
    return create_ticket(payload)


@router.post("/{ticket_id}/classify-ai", response_model=TicketAIClassification)
def classify_ticket_route(ticket_id: int) -> TicketAIClassification:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    classification = classify_ticket(ticket)
    update_ticket_ai_analysis(ticket_id, classification)
    return classification

