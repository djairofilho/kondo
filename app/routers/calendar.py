from datetime import date

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import ensure_condominium_access, get_active_membership, require_roles
from app.models import User
from app.schemas.calendar import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from app.services.calendar_service import (
    create_calendar_event,
    delete_calendar_event,
    get_calendar_event_or_404,
    list_calendar_events,
    update_calendar_event,
)


router = APIRouter(prefix="/calendar", tags=["calendar"])


def _current_condominium_id(db: Session, current_user: User) -> int:
    membership = get_active_membership(db, current_user, "manager", "board_member")
    if membership is None:
        membership = get_active_membership(db, current_user)
    return membership.condominium_id if membership else 1


@router.get("/events", response_model=list[CalendarEvent], dependencies=[Depends(require_roles("manager", "board_member"))])
def get_calendar_events(
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
    current_user: User = Depends(require_roles("manager", "board_member")),
    db: Session = Depends(get_db),
) -> list[CalendarEvent]:
    condominium_id = _current_condominium_id(db, current_user)
    ensure_condominium_access(db, current_user, condominium_id, "manager", "board_member")
    return list_calendar_events(db, condominium_id, start, end, category)


@router.post("/events", response_model=CalendarEvent, dependencies=[Depends(require_roles("manager"))])
def post_calendar_event(
    payload: CalendarEventCreate,
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> CalendarEvent:
    ensure_condominium_access(db, current_user, payload.condominium_id, "manager")
    return create_calendar_event(db, payload)


@router.patch("/events/{event_id}", response_model=CalendarEvent, dependencies=[Depends(require_roles("manager"))])
def patch_calendar_event(
    event_id: int,
    payload: CalendarEventUpdate,
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> CalendarEvent:
    event = get_calendar_event_or_404(db, event_id)
    ensure_condominium_access(db, current_user, event.condominium_id, "manager")
    return update_calendar_event(db, event_id, payload)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("manager"))])
def delete_calendar_event_route(
    event_id: int,
    current_user: User = Depends(require_roles("manager")),
    db: Session = Depends(get_db),
) -> Response:
    target = get_calendar_event_or_404(db, event_id)
    ensure_condominium_access(db, current_user, target.condominium_id, "manager")
    delete_calendar_event(db, event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
