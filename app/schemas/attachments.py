from datetime import datetime

from pydantic import BaseModel


class Attachment(BaseModel):
    id: int
    condominium_id: int
    entity_type: str
    entity_id: int
    uploaded_by_user_id: int | None
    original_file_name: str
    stored_file_name: str
    content_type: str
    file_size: int
    storage_key: str
    storage_provider: str
    visibility: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AttachmentCreateMetadata(BaseModel):
    condominium_id: int = 1
    entity_type: str
    entity_id: int
    uploaded_by_user_id: int | None = None
    visibility: str = "private"

