from fastapi import APIRouter

from app.schemas.agreements import AgreementSimulationRequest, AgreementSimulationResponse
from app.services.agreement_service import simulate_agreement


router = APIRouter(prefix="/agreements", tags=["agreements"])


@router.post("/simulate", response_model=AgreementSimulationResponse)
def simulate_agreement_route(payload: AgreementSimulationRequest) -> AgreementSimulationResponse:
    return simulate_agreement(payload)

