from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.announcements import Announcement, AnnouncementCreate, AnnouncementGenerationRequest, AnnouncementGenerationResponse, AnnouncementUpdate
from app.services.ai_service import generate_announcement
from app.services.content_service import create_announcement, get_announcement, list_announcements, publish_announcement, update_announcement


router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get("", response_model=list[Announcement])
def get_announcements(db: Session = Depends(get_db)) -> list[Announcement]:
    return list_announcements(db)


@router.post("", response_model=Announcement)
def post_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db)) -> Announcement:
    return create_announcement(db, payload)


@router.get("/{announcement_id}", response_model=Announcement)
def get_announcement_route(announcement_id: int, db: Session = Depends(get_db)) -> Announcement:
    return get_announcement(db, announcement_id)


@router.patch("/{announcement_id}", response_model=Announcement)
def patch_announcement(announcement_id: int, payload: AnnouncementUpdate, db: Session = Depends(get_db)) -> Announcement:
    return update_announcement(db, announcement_id, payload)


@router.post("/{announcement_id}/publish", response_model=Announcement)
def post_publish_announcement(announcement_id: int, db: Session = Depends(get_db)) -> Announcement:
    return publish_announcement(db, announcement_id)


@router.post("/generate-ai", response_model=AnnouncementGenerationResponse)
def generate_announcement_route(payload: AnnouncementGenerationRequest) -> AnnouncementGenerationResponse:
    return generate_announcement(payload)

