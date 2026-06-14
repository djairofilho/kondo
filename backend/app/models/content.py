from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    document_type: Mapped[str] = mapped_column(String(80))
    content: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(40), default="managers")

    condominium: Mapped["Condominium"] = relationship(back_populates="documents")


class Announcement(Base, TimestampMixin):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    audience: Mapped[str] = mapped_column(String(80), default="residents")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    condominium: Mapped["Condominium"] = relationship(back_populates="announcements")

