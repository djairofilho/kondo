from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Attachment(Base, TimestampMixin):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[int] = mapped_column(index=True)
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    original_file_name: Mapped[str] = mapped_column(String(255))
    stored_file_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    file_size: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(String(500))
    storage_provider: Mapped[str] = mapped_column(String(40), default="local")
    visibility: Mapped[str] = mapped_column(String(40), default="private")

