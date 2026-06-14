from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    category: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="active")

    condominium: Mapped["Condominium"] = relationship(back_populates="vendors")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="vendor")


class Quote(Base, TimestampMixin):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"), index=True)
    work_item_id: Mapped[int | None] = mapped_column(ForeignKey("work_items.id"), index=True)
    title: Mapped[str] = mapped_column(String(180))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    scope: Mapped[str | None] = mapped_column(Text)
    warranty_days: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), default="received")

    vendor: Mapped["Vendor | None"] = relationship(back_populates="quotes")

