from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), default="received", index=True)
    category: Mapped[str | None] = mapped_column(String(80))
    priority: Mapped[str | None] = mapped_column(String(40))
    ai_analysis: Mapped[dict | None] = mapped_column(JSON)

    condominium: Mapped["Condominium"] = relationship(back_populates="tickets")
    unit: Mapped["Unit | None"] = relationship(back_populates="tickets")
    work_items: Mapped[list["WorkItem"]] = relationship(back_populates="ticket")


class WorkItem(Base, TimestampMixin):
    __tablename__ = "work_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    ticket_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id"), index=True)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(40), default="ticket", index=True)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="received", index=True)
    priority: Mapped[str] = mapped_column(String(40), default="medium")
    due_date: Mapped[date | None] = mapped_column(Date)
    source_type: Mapped[str | None] = mapped_column(String(80))
    source_id: Mapped[int | None] = mapped_column(Integer)

    condominium: Mapped["Condominium"] = relationship(back_populates="work_items")
    ticket: Mapped["Ticket | None"] = relationship(back_populates="work_items")

