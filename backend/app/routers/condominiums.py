from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.condominiums import (
    Condominium,
    CondominiumCreate,
    CondominiumOverview,
    CondominiumUpdate,
    Membership,
    MembershipCreate,
    MembershipUpdate,
    Resident,
    ResidentCreate,
    ResidentUpdate,
    Unit,
    UnitCreate,
    UnitUpdate,
)
from app.services.condominium_service import (
    create_condominium,
    create_membership,
    create_resident,
    create_unit,
    delete_membership,
    get_condominium,
    get_condominium_overview,
    get_unit,
    get_unit_history,
    list_condominiums,
    list_memberships,
    list_residents,
    list_units,
    update_condominium,
    update_membership,
    update_resident,
    update_unit,
)


router = APIRouter(tags=["condominiums"])


@router.get("/condominiums", response_model=list[Condominium])
def get_condominiums(db: Session = Depends(get_db)) -> list[Condominium]:
    return list_condominiums(db)


@router.post("/condominiums", response_model=Condominium)
def post_condominium(payload: CondominiumCreate, db: Session = Depends(get_db)) -> Condominium:
    return create_condominium(db, payload)


@router.get("/condominiums/{condominium_id}", response_model=Condominium)
def get_condominium_route(condominium_id: int, db: Session = Depends(get_db)) -> Condominium:
    return get_condominium(db, condominium_id)


@router.patch("/condominiums/{condominium_id}", response_model=Condominium)
def patch_condominium(condominium_id: int, payload: CondominiumUpdate, db: Session = Depends(get_db)) -> Condominium:
    return update_condominium(db, condominium_id, payload)


@router.get("/condominiums/{condominium_id}/overview", response_model=CondominiumOverview)
def get_condominium_overview_route(condominium_id: int, db: Session = Depends(get_db)) -> CondominiumOverview:
    return get_condominium_overview(db, condominium_id)


@router.get("/condominiums/{condominium_id}/units", response_model=list[Unit])
def get_units(condominium_id: int, db: Session = Depends(get_db)) -> list[Unit]:
    return list_units(db, condominium_id)


@router.post("/condominiums/{condominium_id}/units", response_model=Unit)
def post_unit(condominium_id: int, payload: UnitCreate, db: Session = Depends(get_db)) -> Unit:
    payload.condominium_id = condominium_id
    return create_unit(db, payload)


@router.get("/units/{unit_id}", response_model=Unit)
def get_unit_route(unit_id: int, db: Session = Depends(get_db)) -> Unit:
    return get_unit(db, unit_id)


@router.patch("/units/{unit_id}", response_model=Unit)
def patch_unit(unit_id: int, payload: UnitUpdate, db: Session = Depends(get_db)) -> Unit:
    return update_unit(db, unit_id, payload)


@router.get("/units/{unit_id}/history")
def get_unit_history_route(unit_id: int, db: Session = Depends(get_db)) -> dict:
    return get_unit_history(db, unit_id)


@router.get("/condominiums/{condominium_id}/memberships", response_model=list[Membership])
def get_memberships(condominium_id: int, db: Session = Depends(get_db)) -> list[Membership]:
    return list_memberships(db, condominium_id)


@router.post("/condominiums/{condominium_id}/memberships", response_model=Membership)
def post_membership(condominium_id: int, payload: MembershipCreate, db: Session = Depends(get_db)) -> Membership:
    payload.condominium_id = condominium_id
    return create_membership(db, payload)


@router.patch("/memberships/{membership_id}", response_model=Membership)
def patch_membership(membership_id: int, payload: MembershipUpdate, db: Session = Depends(get_db)) -> Membership:
    return update_membership(db, membership_id, payload)


@router.delete("/memberships/{membership_id}")
def remove_membership(membership_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    delete_membership(db, membership_id)
    return {"status": "deleted"}


@router.get("/units/{unit_id}/residents", response_model=list[Resident])
def get_residents(unit_id: int, db: Session = Depends(get_db)) -> list[Resident]:
    return list_residents(db, unit_id)


@router.post("/units/{unit_id}/residents", response_model=Resident)
def post_resident(unit_id: int, payload: ResidentCreate, db: Session = Depends(get_db)) -> Resident:
    payload.unit_id = unit_id
    return create_resident(db, payload)


@router.patch("/residents/{resident_id}", response_model=Resident)
def patch_resident(resident_id: int, payload: ResidentUpdate, db: Session = Depends(get_db)) -> Resident:
    return update_resident(db, resident_id, payload)

