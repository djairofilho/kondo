from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Condominium(Base, TimestampMixin):
    __tablename__ = "condominiums"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(2))
    status: Mapped[str] = mapped_column(String(40), default="active")

    memberships: Mapped[list["Membership"]] = relationship(back_populates="condominium")
    units: Mapped[list["Unit"]] = relationship(back_populates="condominium")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="condominium")
    work_items: Mapped[list["WorkItem"]] = relationship(back_populates="condominium")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="condominium")
    revenues: Mapped[list["Revenue"]] = relationship(back_populates="condominium")
    documents: Mapped[list["Document"]] = relationship(back_populates="condominium")
    announcements: Mapped[list["Announcement"]] = relationship(back_populates="condominium")
    vendors: Mapped[list["Vendor"]] = relationship(back_populates="condominium")


class Unit(Base, TimestampMixin):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    block: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="active")

    condominium: Mapped["Condominium"] = relationship(back_populates="units")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="unit")
    residents: Mapped[list["Resident"]] = relationship(back_populates="unit")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="unit")
    revenues: Mapped[list["Revenue"]] = relationship(back_populates="unit")
    delinquencies: Mapped[list["Delinquency"]] = relationship(back_populates="unit")
    agreements: Mapped[list["Agreement"]] = relationship(back_populates="unit")
    payments: Mapped[list["Payment"]] = relationship(back_populates="unit")


class Resident(Base, TimestampMixin):
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(255))
    resident_type: Mapped[str] = mapped_column(String(40), default="tenant")
    status: Mapped[str] = mapped_column(String(40), default="active")

    unit: Mapped["Unit"] = relationship(back_populates="residents")

