from fastapi import APIRouter

from app.schemas.finance import DelinquencyItem, FinanceSummary
from app.services.finance_service import get_delinquencies, get_finance_summary


router = APIRouter(tags=["finance"])


@router.get("/finance/summary", response_model=FinanceSummary)
def finance_summary() -> FinanceSummary:
    return get_finance_summary()


@router.get("/delinquencies", response_model=list[DelinquencyItem])
def delinquency_list() -> list[DelinquencyItem]:
    return get_delinquencies()

