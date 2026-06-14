from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from fastapi import HTTPException, status

from app.core.deps import require_roles, resolve_resident_portal_unit, resolve_resident_ticket_unit
from app.models import Unit
from app.schemas.condominiums import ResidentOnboarding, ResidentOnboardingUpdate
from app.schemas.payments import Payment
from app.schemas.tickets import Ticket, TicketCreate
from app.services.calendar_service import (
    generate_resident_boleto,
    generate_resident_component_boleto,
    list_resident_calendar_with_payments,
    list_resident_payments,
)
from app.services.experience_service import (
    board_dashboard,
    board_audit_events,
    board_decisions,
    board_financial_transparency,
    board_maintenance_status,
    manager_dashboard,
    resident_home,
    resident_rules,
)
from app.services.resident_portal_service import get_resident_onboarding, update_resident_onboarding
from app.services.ticket_service import create_ticket, list_tickets


router = APIRouter(tags=["experiences"])


def require_unit(unit: Unit | None) -> Unit:
    if unit is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unit_id is required for this view")
    return unit


@router.get("/manager/dashboard", dependencies=[Depends(require_roles("manager"))])
def get_manager_dashboard(db: Session = Depends(get_db)) -> dict:
    return manager_dashboard(db)


@router.get("/board/dashboard", dependencies=[Depends(require_roles("manager", "board_member"))])
def get_board_dashboard(db: Session = Depends(get_db)) -> dict:
    return board_dashboard(db)


@router.get("/board/overview", dependencies=[Depends(require_roles("manager", "board_member"))])
def get_board_overview(db: Session = Depends(get_db)) -> dict:
    return board_dashboard(db)


@router.get("/board/financial-transparency", dependencies=[Depends(require_roles("manager", "board_member"))])
def get_board_financial_transparency(db: Session = Depends(get_db)) -> dict:
    return board_financial_transparency(db)


@router.get("/board/maintenance-status", dependencies=[Depends(require_roles("manager", "board_member"))])
def get_board_maintenance_status(db: Session = Depends(get_db)) -> dict:
    return board_maintenance_status(db)


@router.get("/board/decisions", dependencies=[Depends(require_roles("manager", "board_member"))])
def get_board_decisions(db: Session = Depends(get_db)) -> dict:
    return board_decisions(db)


@router.get("/board/audit-events", dependencies=[Depends(require_roles("manager", "board_member"))])
def get_board_audit_events(db: Session = Depends(get_db)) -> dict:
    return board_audit_events(db)


@router.get("/resident-portal/home")
def get_resident_portal_home(unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> dict:
    return resident_home(db, unit)


@router.get("/resident-portal/my-unit")
def get_resident_my_unit(unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> dict:
    return {"unit": resident_home(db, unit)["unit"]}


@router.get("/resident-portal/my-tickets", response_model=list[Ticket])
def get_resident_my_tickets(unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> list[Ticket]:
    return list_tickets(db, unit_id=unit.id if unit else None)


@router.post("/resident-portal/tickets", response_model=Ticket)
def post_resident_ticket(payload: TicketCreate, unit: Unit = Depends(resolve_resident_ticket_unit), db: Session = Depends(get_db)) -> Ticket:
    return create_ticket(db, payload, unit=unit)


@router.get("/resident-portal/announcements", dependencies=[Depends(require_roles("resident", "manager", "board_member"))])
def get_resident_announcements(db: Session = Depends(get_db)) -> list[str]:
    return resident_home(db)["announcements"]


@router.get("/resident-portal/rules", dependencies=[Depends(require_roles("resident", "manager", "board_member"))])
def get_resident_rules(db: Session = Depends(get_db)) -> dict:
    return resident_rules(db)


@router.post("/resident-portal/rules/ask", dependencies=[Depends(require_roles("resident", "manager", "board_member"))])
def post_resident_rules_ask() -> dict:
    return {"answer": "Segundo o regimento cadastrado, consulte os horarios permitidos antes de iniciar obras."}


@router.get("/resident-portal/payments", response_model=list[Payment])
def get_resident_payments(unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> list[Payment]:
    return list_resident_payments(db, require_unit(unit))


@router.post("/resident-portal/payments/{payment_id}/generate-boleto", response_model=Payment)
def post_resident_boleto(payment_id: int, unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> Payment:
    return generate_resident_boleto(db, require_unit(unit), payment_id)


@router.post("/resident-portal/payments/{payment_id}/components/{component}/generate-boleto", response_model=Payment)
def post_resident_component_boleto(payment_id: int, component: str, unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> Payment:
    return generate_resident_component_boleto(db, require_unit(unit), payment_id, component)


@router.get("/resident-portal/calendar")
def get_resident_calendar(unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> list[dict]:
    return list_resident_calendar_with_payments(db, require_unit(unit))


@router.get("/resident-portal/onboarding", response_model=ResidentOnboarding)
def get_onboarding(unit: Unit | None = Depends(resolve_resident_portal_unit), db: Session = Depends(get_db)) -> ResidentOnboarding:
    return get_resident_onboarding(db, require_unit(unit))


@router.post("/resident-portal/onboarding", response_model=ResidentOnboarding)
def post_onboarding(
    payload: ResidentOnboardingUpdate,
    unit: Unit | None = Depends(resolve_resident_portal_unit),
    db: Session = Depends(get_db),
) -> ResidentOnboarding:
    return update_resident_onboarding(db, require_unit(unit), payload)
