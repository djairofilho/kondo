from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    description: Mapped[str] = mapped_column(String(180))
    category: Mapped[str] = mapped_column(String(80))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[date | None] = mapped_column(Date)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="pending")

    condominium: Mapped["Condominium"] = relationship(back_populates="expenses")


class Revenue(Base, TimestampMixin):
    __tablename__ = "revenues"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), index=True)
    description: Mapped[str] = mapped_column(String(180))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[date | None] = mapped_column(Date)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="pending")

    condominium: Mapped["Condominium"] = relationship(back_populates="revenues")
    unit: Mapped["Unit | None"] = relationship(back_populates="revenues")


class Delinquency(Base, TimestampMixin):
    __tablename__ = "delinquencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    days_late: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(40), default="open")
    risk: Mapped[str] = mapped_column(String(40), default="medium")

    unit: Mapped["Unit"] = relationship(back_populates="delinquencies")
    agreements: Mapped[list["Agreement"]] = relationship(back_populates="delinquency")


class Agreement(Base, TimestampMixin):
    __tablename__ = "agreements"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    delinquency_id: Mapped[int | None] = mapped_column(ForeignKey("delinquencies.id"), index=True)
    entry_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    installments: Mapped[int] = mapped_column(default=1)
    monthly_installment: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(40), default="active")

    unit: Mapped["Unit"] = relationship(back_populates="agreements")
    delinquency: Mapped["Delinquency | None"] = relationship(back_populates="agreements")
    payments: Mapped[list["Payment"]] = relationship(back_populates="agreement")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), index=True)
    agreement_id: Mapped[int | None] = mapped_column(ForeignKey("agreements.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[date | None] = mapped_column(Date)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payment_method: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="pending")
    payment_metadata: Mapped[dict | None] = mapped_column(JSON)

    unit: Mapped["Unit | None"] = relationship(back_populates="payments")
    agreement: Mapped["Agreement | None"] = relationship(back_populates="payments")

