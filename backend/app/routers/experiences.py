from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tickets import Ticket, TicketCreate
from app.services.experience_service import (
    board_dashboard,
    board_financial_transparency,
    board_maintenance_status,
    manager_dashboard,
    resident_home,
    resident_rules,
)
from app.services.ticket_service import create_ticket, list_tickets


router = APIRouter(tags=["experiences"])


@router.get("/manager/dashboard")
def get_manager_dashboard(db: Session = Depends(get_db)) -> dict:
    return manager_dashboard(db)


@router.get("/board/dashboard")
def get_board_dashboard(db: Session = Depends(get_db)) -> dict:
    return board_dashboard(db)


@router.get("/board/overview")
def get_board_overview(db: Session = Depends(get_db)) -> dict:
    return board_dashboard(db)


@router.get("/board/financial-transparency")
def get_board_financial_transparency(db: Session = Depends(get_db)) -> dict:
    return board_financial_transparency(db)


@router.get("/board/maintenance-status")
def get_board_maintenance_status(db: Session = Depends(get_db)) -> dict:
    return board_maintenance_status(db)


@router.get("/board/decisions")
def get_board_decisions() -> dict:
    return {"decisions": []}


@router.get("/board/audit-events")
def get_board_audit_events() -> dict:
    return {"events": []}


@router.get("/resident-portal/home")
def get_resident_portal_home(unit_id: int | None = None, db: Session = Depends(get_db)) -> dict:
    return resident_home(db, unit_id)


@router.get("/resident-portal/my-unit")
def get_resident_my_unit(unit_id: int | None = None, db: Session = Depends(get_db)) -> dict:
    return {"unit": resident_home(db, unit_id)["unit"]}


@router.get("/resident-portal/my-tickets", response_model=list[Ticket])
def get_resident_my_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    return list_tickets(db)


@router.post("/resident-portal/tickets", response_model=Ticket)
def post_resident_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    return create_ticket(db, payload)


@router.get("/resident-portal/announcements")
def get_resident_announcements(db: Session = Depends(get_db)) -> dict:
    return resident_home(db)["announcements"]


@router.get("/resident-portal/rules")
def get_resident_rules(db: Session = Depends(get_db)) -> dict:
    return resident_rules(db)


@router.post("/resident-portal/rules/ask")
def post_resident_rules_ask() -> dict:
    return {"answer": "Segundo o regimento cadastrado, consulte os horarios permitidos antes de iniciar obras."}

