from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import CalendarEvent, Payment, Unit
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate
from app.services.payment_service import generate_boleto


def _bounds(start: date | None, end: date | None) -> tuple[datetime | None, datetime | None]:
    return (
        datetime.combine(start, time.min) if start else None,
        datetime.combine(end, time.max) if end else None,
    )


def list_calendar_events(
    db: Session,
    condominium_id: int,
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
) -> list[CalendarEvent]:
    start_at, end_at = _bounds(start, end)
    query = db.query(CalendarEvent).filter(CalendarEvent.condominium_id == condominium_id)
    if start_at is not None:
        query = query.filter(CalendarEvent.start_at >= start_at)
    if end_at is not None:
        query = query.filter(CalendarEvent.start_at <= end_at)
    if category:
        query = query.filter(CalendarEvent.category == category)
    return query.order_by(CalendarEvent.start_at.asc()).all()


def list_resident_calendar_events(
    db: Session,
    unit: Unit,
    start: date | None = None,
    end: date | None = None,
) -> list[CalendarEvent]:
    start_at, end_at = _bounds(start, end)
    query = db.query(CalendarEvent).filter(
        CalendarEvent.condominium_id == unit.condominium_id,
        or_(
            CalendarEvent.visibility.in_(["residents", "public"]),
            CalendarEvent.unit_id == unit.id,
        ),
    )
    if start_at is not None:
        query = query.filter(CalendarEvent.start_at >= start_at)
    if end_at is not None:
        query = query.filter(CalendarEvent.start_at <= end_at)
    return query.order_by(CalendarEvent.start_at.asc()).all()


def list_resident_calendar_with_payments(
    db: Session,
    unit: Unit,
    start: date | None = None,
    end: date | None = None,
) -> list[dict]:
    items: list[dict] = [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "category": event.category,
            "start_at": event.start_at.isoformat(),
            "end_at": event.end_at.isoformat() if event.end_at else None,
            "location": event.location,
            "visibility": event.visibility,
            "source_type": event.source_type,
            "source_id": event.source_id,
            "status": event.status,
        }
        for event in list_resident_calendar_events(db, unit, start, end)
    ]

    start_at, end_at = _bounds(start, end)
    payments = db.query(Payment).filter(Payment.unit_id == unit.id, Payment.due_date.isnot(None))
    if start_at is not None:
        payments = payments.filter(Payment.due_date >= start_at.date())
    if end_at is not None:
        payments = payments.filter(Payment.due_date <= end_at.date())

    for payment in payments.order_by(Payment.due_date.asc()).all():
        items.append(
            {
                "id": f"payment-{payment.id}",
                "title": "Vencimento do condominio",
                "description": f"Pagamento #{payment.id}",
                "category": "finance",
                "start_at": datetime.combine(payment.due_date, time.min).isoformat()
                if payment.due_date
                else None,
                "end_at": None,
                "location": None,
                "visibility": "unit",
                "source_type": "payment",
                "source_id": payment.id,
                "status": payment.status,
            }
        )

    return sorted(items, key=lambda item: item["start_at"] or "")


def create_calendar_event(db: Session, payload: CalendarEventCreate) -> CalendarEvent:
    event = CalendarEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_calendar_event_or_404(db: Session, event_id: int) -> CalendarEvent:
    event = db.get(CalendarEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found")
    return event


def update_calendar_event(db: Session, event_id: int, payload: CalendarEventUpdate) -> CalendarEvent:
    event = get_calendar_event_or_404(db, event_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete_calendar_event(db: Session, event_id: int) -> None:
    event = get_calendar_event_or_404(db, event_id)
    db.delete(event)
    db.commit()


def list_resident_payments(db: Session, unit: Unit) -> list[Payment]:
    return db.query(Payment).filter(Payment.unit_id == unit.id).order_by(Payment.due_date.asc()).all()


def generate_resident_boleto(db: Session, unit: Unit, payment_id: int) -> Payment:
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.unit_id != unit.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Payment does not belong to unit")
    return generate_boleto(db, payment_id)
