from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models import (
    Agreement,
    Announcement,
    Attachment,
    AuditEvent,
    CalendarEvent,
    Condominium,
    Delinquency,
    Document,
    Expense,
    Membership,
    Payment,
    Quote,
    Resident,
    Revenue,
    Ticket,
    TicketComment,
    Unit,
    User,
    Vendor,
    WorkItem,
)


DEMO_CONDOMINIUM_NAME = "Condominio Jardim Aurora"
DEMO_PASSWORD = "kondo123"
DEMO_EMAILS = {
    "manager": "sindico@kondo.com",
    "board": "conselho@kondo.com",
    "resident": "morador@kondo.com",
    "admin": "admin@kondo.local",
}


RESIDENT_NAMES = [
    "Ana Ribeiro",
    "Bruno Carvalho",
    "Camila Torres",
    "Daniel Martins",
    "Elisa Nogueira",
    "Felipe Rocha",
    "Gabriela Lima",
    "Henrique Alves",
    "Isabela Costa",
    "Joao Morador",
    "Karina Mendes",
    "Leonardo Dias",
    "Marina Souza",
    "Nicolas Prado",
    "Olivia Barros",
    "Paulo Ferraz",
    "Renata Araujo",
    "Samuel Vieira",
    "Tatiana Lopes",
    "Victor Gomes",
    "Yasmin Duarte",
    "Andre Moreira",
    "Bianca Freitas",
    "Caio Barbosa",
    "Debora Reis",
    "Eduardo Pinto",
    "Fernanda Melo",
    "Gustavo Nunes",
    "Helena Martins",
    "Igor Campos",
    "Julia Andrade",
    "Lucas Teixeira",
]


def money(value: str | Decimal | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def reset_demo_data(db: Session) -> None:
    condominium = db.query(Condominium).filter(Condominium.name == DEMO_CONDOMINIUM_NAME).first()
    if condominium is None:
        return

    unit_ids = [unit.id for unit in db.query(Unit).filter(Unit.condominium_id == condominium.id).all()]
    ticket_ids = [ticket.id for ticket in db.query(Ticket).filter(Ticket.condominium_id == condominium.id).all()]
    work_item_ids = [
        item.id for item in db.query(WorkItem).filter(WorkItem.condominium_id == condominium.id).all()
    ]
    vendor_ids = [vendor.id for vendor in db.query(Vendor).filter(Vendor.condominium_id == condominium.id).all()]
    demo_user_ids = [
        user.id
        for user in db.query(User)
        .filter(
            (User.email.in_(list(DEMO_EMAILS.values())))
            | (User.email.like("%@morador.kondo.local"))
        )
        .all()
    ]

    if ticket_ids:
        db.query(TicketComment).filter(TicketComment.ticket_id.in_(ticket_ids)).delete(synchronize_session=False)
    if work_item_ids:
        db.query(Quote).filter(Quote.work_item_id.in_(work_item_ids)).delete(synchronize_session=False)
    if vendor_ids:
        db.query(Quote).filter(Quote.vendor_id.in_(vendor_ids)).delete(synchronize_session=False)

    db.query(Attachment).filter(Attachment.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(AuditEvent).filter(AuditEvent.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(WorkItem).filter(WorkItem.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Ticket).filter(Ticket.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Payment).filter(Payment.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Revenue).filter(Revenue.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Expense).filter(Expense.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(CalendarEvent).filter(CalendarEvent.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Document).filter(Document.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Announcement).filter(Announcement.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Vendor).filter(Vendor.condominium_id == condominium.id).delete(synchronize_session=False)

    if unit_ids:
        db.query(Agreement).filter(Agreement.unit_id.in_(unit_ids)).delete(synchronize_session=False)
        db.query(Delinquency).filter(Delinquency.unit_id.in_(unit_ids)).delete(synchronize_session=False)
        db.query(Resident).filter(Resident.unit_id.in_(unit_ids)).delete(synchronize_session=False)
    db.query(Membership).filter(Membership.condominium_id == condominium.id).delete(synchronize_session=False)
    db.query(Unit).filter(Unit.condominium_id == condominium.id).delete(synchronize_session=False)
    db.delete(condominium)

    if demo_user_ids:
        db.query(AuditEvent).filter(AuditEvent.actor_user_id.in_(demo_user_ids)).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_(demo_user_ids)).delete(synchronize_session=False)

    db.commit()


def charge_breakdown(amount: Decimal, floor: int, unit_index: int, mode: str) -> dict[str, str]:
    if mode == "water_gas_included":
        values = {
            "condominio": amount - money("92"),
            "agua": money("0"),
            "luz": money("92"),
            "gas": money("0"),
        }
    else:
        water = money(72 + ((floor + unit_index) % 5) * 8)
        power = money(86 + (floor % 4) * 11)
        gas = money(38 + (unit_index % 4) * 9)
        values = {
            "condominio": amount - water - power - gas,
            "agua": water,
            "luz": power,
            "gas": gas,
        }
    return {key: str(value.quantize(Decimal("0.01"))) for key, value in values.items()}


def seed_demo_data(db: Session) -> None:
    reset_demo_data(db)

    condominium = Condominium(
        name=DEMO_CONDOMINIUM_NAME,
        address="Rua das Palmeiras, 1200",
        city="Sao Paulo",
        state="SP",
    )
    manager = User(
        name="Maria Sindica",
        email=DEMO_EMAILS["manager"],
        password_hash=hash_password(DEMO_PASSWORD),
    )
    board = User(
        name="Carlos Conselho",
        email=DEMO_EMAILS["board"],
        password_hash=hash_password(DEMO_PASSWORD),
    )
    resident_user = User(
        name="Joao Morador",
        email=DEMO_EMAILS["resident"],
        password_hash=hash_password(DEMO_PASSWORD),
    )
    admin_user = User(
        name="Admin Kondo",
        email=DEMO_EMAILS["admin"],
        password_hash=hash_password(DEMO_PASSWORD),
        is_platform_admin=True,
    )
    db.add_all([condominium, manager, board, resident_user, admin_user])
    db.flush()

    units: dict[str, Unit] = {}
    for floor in range(1, 17):
        for apartment in range(1, 5):
            number = f"{floor}{apartment:02d}"
            unit = Unit(condominium_id=condominium.id, number=number, block="A")
            db.add(unit)
            units[number] = unit
    db.flush()

    morador_unit = units["804"]
    board_unit = units["1202"]
    db.add_all(
        [
            Membership(user_id=manager.id, condominium_id=condominium.id, role="manager"),
            Membership(user_id=board.id, condominium_id=condominium.id, role="board_member"),
            Membership(user_id=board.id, condominium_id=condominium.id, unit_id=board_unit.id, role="resident"),
            Membership(user_id=resident_user.id, condominium_id=condominium.id, unit_id=morador_unit.id, role="resident"),
        ]
    )

    extra_users: dict[str, User] = {}
    for index, unit in enumerate(list(units.values())[:12], start=1):
        if unit.id in {morador_unit.id, board_unit.id}:
            continue
        user = User(
            name=RESIDENT_NAMES[index % len(RESIDENT_NAMES)],
            email=f"morador{index:02d}@morador.kondo.local",
            password_hash=hash_password(DEMO_PASSWORD),
        )
        db.add(user)
        extra_users[unit.number] = user
    db.flush()

    for index, unit in enumerate(units.values(), start=1):
        user_id = None
        name = RESIDENT_NAMES[index % len(RESIDENT_NAMES)]
        email = f"unidade{unit.number}@morador.kondo.local"
        if unit.id == morador_unit.id:
            user_id = resident_user.id
            name = "Joao Morador"
            email = DEMO_EMAILS["resident"]
        elif unit.id == board_unit.id:
            user_id = board.id
            name = "Carlos Conselho"
            email = DEMO_EMAILS["board"]
        elif unit.number in extra_users:
            user_id = extra_users[unit.number].id
            email = extra_users[unit.number].email

        if user_id and unit.id not in {morador_unit.id, board_unit.id}:
            db.add(Membership(user_id=user_id, condominium_id=condominium.id, unit_id=unit.id, role="resident"))

        db.add(
            Resident(
                unit_id=unit.id,
                user_id=user_id,
                name=name,
                email=email,
                phone=f"1198{index:07d}"[:11],
                emergency_contact=f"Contato emergencia {index}",
                household_info=f"{2 + (index % 3)} moradores",
                vehicles="1 carro" if index % 3 else "2 carros",
                pets="1 pet pequeno" if index % 5 == 0 else None,
                notification_preference="whatsapp",
                onboarding_completed=index % 4 != 0,
                resident_type="owner" if index % 3 == 0 else "tenant",
            )
        )

    vendors = [
        Vendor(condominium_id=condominium.id, name="HidroService", category="hidraulica", phone="11999990000"),
        Vendor(condominium_id=condominium.id, name="Elevadores Atlas Prime", category="elevadores", phone="1133332000"),
        Vendor(condominium_id=condominium.id, name="Portaria Segura 24h", category="seguranca", phone="1144442000"),
        Vendor(condominium_id=condominium.id, name="LimpaMais Condominios", category="limpeza", phone="1155552000"),
    ]
    db.add_all(vendors)
    db.flush()

    months = [(2026, month) for month in range(1, 7)]
    overdue_current_units = {"304", "804", "1103", "1402", "1604"}
    pending_current_units = {"202", "704", "901", "1301", "1503"}
    water_gas_included_units = {number for number in units if int(number[:-2]) <= 4}

    for year, month in months:
        for unit_index, unit in enumerate(units.values(), start=1):
            floor = int(unit.number[:-2])
            amount = money(720 + floor * 8 + (unit_index % 4) * 24)
            status = "paid"
            if month == 6 and unit.number in overdue_current_units:
                status = "overdue"
            elif month == 6 and unit.number in pending_current_units:
                status = "pending"

            mode = "water_gas_included" if unit.number in water_gas_included_units else "separate"
            metadata = {
                "billing_mode": mode,
                "breakdown": charge_breakdown(amount, floor, unit_index, mode),
                "reference_month": f"{year}-{month:02d}",
            }
            due = date(year, month, 10)
            paid_at = datetime(year, month, 9, 15, 30) if status == "paid" else None
            db.add(
                Payment(
                    condominium_id=condominium.id,
                    unit_id=unit.id,
                    amount=amount,
                    due_date=due,
                    paid_at=paid_at,
                    payment_method="boleto" if status == "paid" else "pix",
                    status=status,
                    payment_metadata=metadata,
                )
            )
            db.add(
                Revenue(
                    condominium_id=condominium.id,
                    unit_id=unit.id,
                    description=f"Cota condominial {month:02d}/{year} - unidade {unit.number}",
                    amount=amount,
                    due_date=due,
                    paid_at=paid_at,
                    status=status,
                )
            )

    for unit_number in overdue_current_units:
        floor = int(unit_number[:-2])
        amount_due = money(760 + floor * 8)
        db.add(
            Delinquency(
                unit_id=units[unit_number].id,
                amount_due=amount_due,
                days_late=18 + floor * 3,
                risk="high" if floor >= 11 else "medium",
            )
        )
        db.add(
            Agreement(
                unit_id=units[unit_number].id,
                entry_amount=money("250"),
                installments=4,
                monthly_installment=((amount_due - money("250")) / Decimal("4")).quantize(Decimal("0.01")),
            )
        )

    expense_templates = [
        ("Portaria 24h", "seguranca", "18400"),
        ("Limpeza e conservacao", "limpeza", "9800"),
        ("Manutencao preventiva elevadores", "manutencao", "7400"),
        ("Conta de agua areas comuns", "agua", "5200"),
        ("Energia areas comuns", "energia", "6800"),
        ("Gas central", "gas", "4100"),
        ("Seguro predial", "seguro", "3600"),
        ("Jardinagem", "jardinagem", "1800"),
        ("Dedetizacao e controle de pragas", "operacional", "1200"),
        ("Administradora", "administrativo", "4900"),
        ("Fundo de reserva", "reserva", "6000"),
    ]
    for year, month in months:
        for index, (description, category, amount) in enumerate(expense_templates, start=1):
            variation = money((month - 3) * 45 + (index % 3) * 120)
            final_amount = money(amount) + variation
            db.add(
                Expense(
                    condominium_id=condominium.id,
                    description=f"{description} {month:02d}/{year}",
                    category=category,
                    amount=final_amount,
                    due_date=date(year, month, min(25, 5 + index * 2)),
                    status="paid" if month < 6 or index <= 6 else "pending",
                    paid_at=datetime(year, month, min(24, 6 + index * 2), 11, 0) if month < 6 else None,
                )
            )

    ticket_specs = [
        ("Vazamento no hall", "hidraulica", "alta", "in_review", "304"),
        ("Barulho no motor do elevador social", "elevadores", "critica", "vendor_contacted", "1202"),
        ("Lampada queimada na garagem", "eletrica", "media", "received", "704"),
        ("Portao social travando", "seguranca", "alta", "in_progress", "901"),
        ("Infiltracao na parede da escada", "manutencao", "alta", "waiting_approval", "1402"),
        ("Reserva do salao sem confirmacao", "operacional", "baixa", "resolved", "804"),
    ]
    for title, category, priority, status, unit_number in ticket_specs:
        unit = units[unit_number]
        ticket = Ticket(
            condominium_id=condominium.id,
            unit_id=unit.id,
            created_by_user_id=resident_user.id if unit_number == "804" else None,
            title=title,
            description=f"{title}. Solicitacao registrada pela unidade {unit.number}.",
            location=f"Bloco A - {unit.number}",
            status=status,
            category=category,
            priority=priority,
            ai_analysis={"risk": priority, "next_action": "Priorizar conforme impacto operacional."},
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
                status=status,
                priority="high" if priority in {"alta", "critica"} else "medium",
                source_type="ticket",
                source_id=ticket.id,
            )
        )

    db.add_all(
        [
            CalendarEvent(condominium_id=condominium.id, title="Assembleia ordinaria", category="event", start_at=datetime(2026, 6, 24, 19, 30), location="Salao de festas", visibility="residents", status="scheduled"),
            CalendarEvent(condominium_id=condominium.id, title="Manutencao preventiva dos elevadores", category="maintenance", start_at=datetime(2026, 6, 18, 9, 0), location="Torre A", visibility="residents", status="scheduled"),
            CalendarEvent(condominium_id=condominium.id, title="Lavagem das caixas d'agua", category="maintenance", start_at=datetime(2026, 6, 21, 8, 0), location="Cobertura", visibility="residents", status="scheduled"),
            CalendarEvent(condominium_id=condominium.id, unit_id=morador_unit.id, title="Reserva do salao - unidade 804", category="reservation", start_at=datetime(2026, 6, 28, 18, 0), location="Salao de festas", visibility="unit", status="scheduled"),
            Document(condominium_id=condominium.id, title="Regimento interno", document_type="rules", content="Obras com ruido devem ocorrer em dias uteis, das 9h as 17h.", visibility="residents"),
            Document(condominium_id=condominium.id, title="Ata da assembleia de maio", document_type="minutes", content="Aprovada revisao da manutencao dos elevadores e fundo de reserva.", visibility="residents"),
            Document(condominium_id=condominium.id, title="Contrato portaria 24h", document_type="contract", content="Contrato vigente com Portaria Segura 24h.", visibility="managers"),
            Announcement(condominium_id=condominium.id, title="Lavagem das caixas d'agua", body="Havera interrupcao programada de agua no dia 21/06 das 8h as 14h.", audience="residents", status="published", published_at=datetime(2026, 6, 12, 10, 0)),
            Announcement(condominium_id=condominium.id, title="Assembleia ordinaria", body="Convocamos todos para assembleia em 24/06 as 19h30 no salao de festas.", audience="residents", status="published", published_at=datetime(2026, 6, 10, 9, 0)),
        ]
    )

    db.add_all(
        [
            AuditEvent(condominium_id=condominium.id, actor_user_id=manager.id, action="seed.finance.created", entity_type="seed", event_metadata={"months": 6, "units": 64}),
            AuditEvent(condominium_id=condominium.id, actor_user_id=manager.id, action="payment.boleto.generated", entity_type="payment", entity_id=1, event_metadata={"source": "seed"}),
            AuditEvent(condominium_id=condominium.id, actor_user_id=board.id, action="board.reviewed", entity_type="finance", event_metadata={"focus": "cash_gap"}),
        ]
    )

    db.commit()


def main() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)


if __name__ == "__main__":
    main()
