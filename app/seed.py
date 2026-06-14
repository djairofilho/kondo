from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models import (
    Agreement,
    Announcement,
    Condominium,
    Delinquency,
    Document,
    Expense,
    Membership,
    Payment,
    Resident,
    Revenue,
    Ticket,
    Unit,
    User,
    Vendor,
    WorkItem,
)


def update_demo_login_emails(db: Session) -> None:
    email_updates = {
        "maria@kondo.local": "sindico@kondo.com",
        "carlos@kondo.local": "conselho@kondo.com",
        "joao@kondo.local": "morador@kondo.com",
    }
    for old_email, new_email in email_updates.items():
        user = db.query(User).filter(User.email == old_email).first()
        if user is not None:
            user.email = new_email

    resident = db.query(Resident).filter(Resident.email == "joao@kondo.local").first()
    if resident is not None:
        resident.email = "morador@kondo.com"

    db.commit()


def seed_demo_data(db: Session) -> None:
    existing = db.query(Condominium).filter(Condominium.name == "Condominio Jardim Aurora").first()
    if existing is not None:
        update_demo_login_emails(db)
        return

    condominium = Condominium(
        name="Condominio Jardim Aurora",
        address="Rua das Palmeiras, 1200",
        city="Sao Paulo",
        state="SP",
    )
    manager = User(name="Maria Sindica", email="sindico@kondo.com", password_hash=hash_password("kondo123"))
    board = User(name="Carlos Conselho", email="conselho@kondo.com", password_hash=hash_password("kondo123"))
    resident_user = User(name="Joao Morador", email="morador@kondo.com", password_hash=hash_password("kondo123"))
    admin_user = User(name="Admin Kondo", email="admin@kondo.local", password_hash=hash_password("kondo123"), is_platform_admin=True)

    db.add_all([condominium, manager, board, resident_user, admin_user])
    db.flush()

    unit_304 = Unit(condominium_id=condominium.id, number="304", block="A")
    unit_1202 = Unit(condominium_id=condominium.id, number="1202", block="B")
    db.add_all([unit_304, unit_1202])
    db.flush()

    db.add_all(
        [
            Membership(user_id=manager.id, condominium_id=condominium.id, role="manager"),
            Membership(user_id=board.id, condominium_id=condominium.id, role="board_member"),
            Membership(user_id=resident_user.id, condominium_id=condominium.id, unit_id=unit_304.id, role="resident"),
            Resident(unit_id=unit_304.id, user_id=resident_user.id, name="Joao Morador", email="morador@kondo.com", resident_type="tenant"),
        ]
    )

    ticket = Ticket(
        condominium_id=condominium.id,
        unit_id=unit_304.id,
        created_by_user_id=resident_user.id,
        title="Vazamento na garagem",
        description="Vazamento forte na garagem B2 perto do quadro eletrico.",
        location="Garagem B2",
        status="received",
        category="hidraulica",
        priority="alta",
        ai_analysis={
            "risk": "risco eletrico",
            "next_action": "Isolar a area e acionar fornecedor imediatamente.",
        },
    )
    db.add(ticket)
    db.flush()

    db.add(
        WorkItem(
            condominium_id=condominium.id,
            ticket_id=ticket.id,
            type="ticket",
            title=ticket.title,
            description=ticket.description,
            status="vendor_contacted",
            priority="high",
            source_type="ticket",
            source_id=ticket.id,
        )
    )

    db.add_all(
        [
            Revenue(condominium_id=condominium.id, unit_id=unit_304.id, description="Taxa condominial junho", amount=Decimal("516.00"), due_date=date(2026, 6, 10), status="pending"),
            Expense(condominium_id=condominium.id, description="Manutencao elevador", category="manutencao", amount=Decimal("2300.00"), due_date=date(2026, 6, 20), status="pending"),
            Delinquency(unit_id=unit_304.id, amount_due=Decimal("1548.00"), days_late=63, risk="medium"),
            Agreement(unit_id=unit_304.id, entry_amount=Decimal("400.00"), installments=4, monthly_installment=Decimal("287.00")),
            Payment(condominium_id=condominium.id, unit_id=unit_304.id, amount=Decimal("516.00"), due_date=date(2026, 6, 10), payment_method="pix", status="pending", payment_metadata={"pix_code": "demo-pix-code"}),
            Document(condominium_id=condominium.id, title="Regimento interno", document_type="rules", content="Obras com ruido devem ocorrer em dias uteis, em horario comercial.", visibility="residents"),
            Announcement(condominium_id=condominium.id, title="Manutencao emergencial", body="A garagem B2 ficara parcialmente isolada para reparo.", audience="residents", status="published"),
            Vendor(condominium_id=condominium.id, name="HidroService", category="hidraulica", phone="11999990000"),
        ]
    )

    db.commit()


def main() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)


if __name__ == "__main__":
    main()

