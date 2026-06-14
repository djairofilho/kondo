from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=utc_now)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_platform_admin: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(40), default="active")

    memberships: Mapped[list["Membership"]] = relationship(back_populates="user")
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="actor")


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


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    condominium_id: Mapped[int] = mapped_column(ForeignKey("condominiums.id"), index=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), index=True)
    role: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), default="active")

    user: Mapped["User"] = relationship(back_populates="memberships")
    condominium: Mapped["Condominium"] = relationship(back_populates="memberships")
    unit: Mapped["Unit | None"] = relationship(back_populates="memberships")


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


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    condominium_id: Mapped[int | None] = mapped_column(ForeignKey("condominiums.id"), index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, index=True)
    event_metadata: Mapped[dict | None] = mapped_column(JSON)

    actor: Mapped["User | None"] = relationship(back_populates="audit_events")

