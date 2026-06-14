from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Resident, Unit
from app.schemas.condominiums import ResidentOnboarding, ResidentOnboardingUpdate


def _resident_for_unit(db: Session, unit: Unit) -> Resident | None:
    return (
        db.query(Resident)
        .filter(Resident.unit_id == unit.id, Resident.status == "active")
        .order_by(Resident.created_at.asc())
        .first()
    )


def get_resident_onboarding(db: Session, unit: Unit) -> ResidentOnboarding:
    resident = _resident_for_unit(db, unit)
    return ResidentOnboarding(
        unit_id=unit.id,
        unit_number=unit.number,
        unit_block=unit.block,
        resident_name=resident.name if resident else None,
        email=resident.email if resident else None,
        phone=resident.phone if resident else None,
        emergency_contact=resident.emergency_contact if resident else None,
        household_info=resident.household_info if resident else None,
        vehicles=resident.vehicles if resident else None,
        pets=resident.pets if resident else None,
        notification_preference=resident.notification_preference if resident else None,
        completed=resident.onboarding_completed if resident else False,
    )


def update_resident_onboarding(
    db: Session,
    unit: Unit,
    payload: ResidentOnboardingUpdate,
) -> ResidentOnboarding:
    resident = _resident_for_unit(db, unit)
    if resident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    updates = payload.model_dump(exclude_unset=True)
    name = updates.pop("resident_name", None)
    completed = updates.pop("completed", None)
    if name is not None:
        resident.name = name
    if completed is not None:
        resident.onboarding_completed = completed
    for field, value in updates.items():
        setattr(resident, field, value)
    resident.onboarding_metadata = {"source": "resident-portal"}
    db.commit()
    db.refresh(resident)
    return get_resident_onboarding(db, unit)
