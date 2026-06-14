from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Condominium, Membership, Resident, Ticket, Unit
from app.schemas.condominiums import (
    CondominiumCreate,
    CondominiumOverview,
    CondominiumUpdate,
    MembershipCreate,
    MembershipUpdate,
    ResidentCreate,
    ResidentUpdate,
    UnitCreate,
    UnitUpdate,
)


def _get_or_404(db: Session, model, entity_id: int):
    entity = db.get(model, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return entity


def list_condominiums(db: Session) -> list[Condominium]:
    return db.query(Condominium).order_by(Condominium.name).all()


def create_condominium(db: Session, payload: CondominiumCreate) -> Condominium:
    entity = Condominium(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_condominium(db: Session, condominium_id: int) -> Condominium:
    return _get_or_404(db, Condominium, condominium_id)


def update_condominium(db: Session, condominium_id: int, payload: CondominiumUpdate) -> Condominium:
    entity = get_condominium(db, condominium_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def get_condominium_overview(db: Session, condominium_id: int) -> CondominiumOverview:
    condominium = get_condominium(db, condominium_id)
    return CondominiumOverview(
        condominium=condominium,
        units=db.query(Unit).filter(Unit.condominium_id == condominium_id).count(),
        active_memberships=db.query(Membership).filter(Membership.condominium_id == condominium_id, Membership.status == "active").count(),
        open_tickets=db.query(Ticket).filter(Ticket.condominium_id == condominium_id, Ticket.status != "resolved").count(),
    )


def list_units(db: Session, condominium_id: int) -> list[Unit]:
    return db.query(Unit).filter(Unit.condominium_id == condominium_id).order_by(Unit.block, Unit.number).all()


def create_unit(db: Session, payload: UnitCreate) -> Unit:
    entity = Unit(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_unit(db: Session, unit_id: int) -> Unit:
    return _get_or_404(db, Unit, unit_id)


def update_unit(db: Session, unit_id: int, payload: UnitUpdate) -> Unit:
    entity = get_unit(db, unit_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def get_unit_history(db: Session, unit_id: int) -> dict:
    unit = get_unit(db, unit_id)
    return {
        "unit_id": unit.id,
        "tickets": len(unit.tickets),
        "revenues": len(unit.revenues),
        "delinquencies": len(unit.delinquencies),
        "agreements": len(unit.agreements),
    }


def list_memberships(db: Session, condominium_id: int) -> list[Membership]:
    return db.query(Membership).filter(Membership.condominium_id == condominium_id).all()


def create_membership(db: Session, payload: MembershipCreate) -> Membership:
    entity = Membership(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_membership(db: Session, membership_id: int, payload: MembershipUpdate) -> Membership:
    entity = _get_or_404(db, Membership, membership_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def delete_membership(db: Session, membership_id: int) -> None:
    entity = _get_or_404(db, Membership, membership_id)
    db.delete(entity)
    db.commit()


def list_residents(db: Session, unit_id: int) -> list[Resident]:
    return db.query(Resident).filter(Resident.unit_id == unit_id).all()


def create_resident(db: Session, payload: ResidentCreate) -> Resident:
    entity = Resident(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_resident(db: Session, resident_id: int, payload: ResidentUpdate) -> Resident:
    entity = _get_or_404(db, Resident, resident_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity

