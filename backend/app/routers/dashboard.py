from fastapi import APIRouter, Depends

from app.core.deps import require_roles
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary, dependencies=[Depends(require_roles("manager", "board_member"))])
def dashboard_summary() -> DashboardSummary:
    return get_dashboard_summary()

