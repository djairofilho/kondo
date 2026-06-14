from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agreements import Agreement, AgreementCreate, AgreementSimulationRequest, AgreementSimulationResponse, AgreementUpdate
from app.schemas.payments import Payment
from app.services.agreement_service import (
    add_agreement_payment,
    cancel_agreement,
    create_agreement,
    get_agreement_or_404,
    list_agreements,
    simulate_agreement,
    update_agreement,
)


router = APIRouter(prefix="/agreements", tags=["agreements"])


@router.get("", response_model=list[Agreement])
def get_agreements(db: Session = Depends(get_db)) -> list[Agreement]:
    return list_agreements(db)


@router.post("", response_model=Agreement)
def post_agreement(payload: AgreementCreate, db: Session = Depends(get_db)) -> Agreement:
    return create_agreement(db, payload)


@router.get("/{agreement_id}", response_model=Agreement)
def get_agreement(agreement_id: int, db: Session = Depends(get_db)) -> Agreement:
    return get_agreement_or_404(db, agreement_id)


@router.patch("/{agreement_id}", response_model=Agreement)
def patch_agreement(agreement_id: int, payload: AgreementUpdate, db: Session = Depends(get_db)) -> Agreement:
    return update_agreement(db, agreement_id, payload)


@router.post("/simulate", response_model=AgreementSimulationResponse)
def simulate_agreement_route(payload: AgreementSimulationRequest) -> AgreementSimulationResponse:
    return simulate_agreement(payload)


@router.post("/{agreement_id}/payments", response_model=Payment)
def post_agreement_payment(agreement_id: int, db: Session = Depends(get_db)) -> Payment:
    return add_agreement_payment(db, agreement_id)


@router.post("/{agreement_id}/cancel", response_model=Agreement)
def post_cancel_agreement(agreement_id: int, db: Session = Depends(get_db)) -> Agreement:
    return cancel_agreement(db, agreement_id)

