from datetime import datetime

from pydantic import BaseModel


class AuditEventCreate(BaseModel):
    condominium_id: int | None = None
    actor_user_id: int | None = None
    action: str
    entity_type: str | None = None
    entity_id: int | None = None
    event_metadata: dict | None = None


class AuditEvent(AuditEventCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

