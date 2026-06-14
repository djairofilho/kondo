from fastapi import APIRouter

from app.schemas.announcements import AnnouncementGenerationRequest, AnnouncementGenerationResponse
from app.services.ai_service import generate_announcement


router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.post("/generate-ai", response_model=AnnouncementGenerationResponse)
def generate_announcement_route(payload: AnnouncementGenerationRequest) -> AnnouncementGenerationResponse:
    return generate_announcement(payload)

