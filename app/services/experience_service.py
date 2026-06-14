from sqlalchemy.orm import Session

from app.models import Announcement, AuditEvent, Document, Expense, Ticket, Unit, WorkItem
from app.services.document_rag_service import retrieve_document_context
from app.services.finance_service import get_finance_summary


def manager_dashboard(db: Session) -> dict:
    return {
        "finance": get_finance_summary(db).model_dump(),
        "open_tickets": db.query(Ticket).filter(Ticket.status != "resolved").count(),
        "critical_work_items": db.query(WorkItem).filter(WorkItem.priority == "high").count(),
        "kanban_columns": ["received", "in_review", "vendor_contacted", "waiting_approval", "in_progress", "resolved"],
    }


def board_dashboard(db: Session) -> dict:
    finance = get_finance_summary(db)
    return {
        "cash_gap": finance.cash_gap,
        "expenses": finance.expenses,
        "expected_revenue": finance.expected_revenue,
        "open_maintenance": db.query(WorkItem).filter(WorkItem.status != "resolved").count(),
        "recent_decisions": [],
    }


def resident_home(db: Session, unit: Unit | None = None) -> dict:
    tickets_query = db.query(Ticket)
    if unit is not None:
        tickets_query = tickets_query.filter(Ticket.unit_id == unit.id)

    return {
        "unit": {"id": unit.id, "number": unit.number, "block": unit.block} if unit else None,
        "tickets": [ticket.id for ticket in tickets_query.order_by(Ticket.created_at.desc()).limit(5).all()],
        "announcements": [announcement.title for announcement in db.query(Announcement).order_by(Announcement.created_at.desc()).limit(5).all()],
        "rules_available": db.query(Document).filter(Document.document_type == "rules").count(),
    }


def board_financial_transparency(db: Session) -> dict:
    finance = get_finance_summary(db)
    return {
        "summary": finance.model_dump(),
        "top_expenses": [
            {"description": row.description, "amount": row.amount}
            for row in db.query(Expense).order_by(Expense.amount.desc()).limit(5).all()
        ],
    }


def board_maintenance_status(db: Session) -> dict:
    return {
        "items": [
            {"id": item.id, "title": item.title, "status": item.status, "priority": item.priority}
            for item in db.query(WorkItem).order_by(WorkItem.created_at.desc()).limit(20).all()
        ]
    }


def board_decisions(db: Session) -> dict:
    pending_expenses = db.query(Expense).filter(Expense.status != "paid").order_by(Expense.amount.desc()).limit(4).all()
    urgent_items = db.query(WorkItem).filter(WorkItem.status != "resolved").order_by(WorkItem.created_at.desc()).limit(4).all()
    decisions = [
        {
            "title": f"Aprovar pagamento: {expense.description}",
            "status": "pending",
            "amount": expense.amount,
            "category": expense.category,
        }
        for expense in pending_expenses
    ]
    decisions.extend(
        {
            "title": f"Definir encaminhamento: {item.title}",
            "status": item.status,
            "priority": item.priority,
        }
        for item in urgent_items
    )
    return {"decisions": decisions[:6]}


def board_audit_events(db: Session) -> dict:
    events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(20).all()
    return {
        "events": [
            {
                "id": event.id,
                "action": event.action,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "event_metadata": event.event_metadata or {},
                "created_at": event.created_at,
            }
            for event in events
        ]
    }


def resident_rules(db: Session) -> dict:
    docs = db.query(Document).filter(Document.visibility.in_(["residents", "public"])).all()
    return {"documents": [{"id": doc.id, "title": doc.title, "type": doc.document_type} for doc in docs]}


def answer_resident_rules(db: Session, question: str, condominium_id: int | None = None) -> dict:
    docs_query = db.query(Document).filter(
        Document.visibility.in_(["residents", "public"]),
        Document.document_type == "rules",
    )
    if condominium_id is not None:
        docs_query = docs_query.filter(Document.condominium_id == condominium_id)

    snippets: list[str] = []
    for document in docs_query.order_by(Document.created_at.desc()).all():
        for chunk in retrieve_document_context(document, question, limit=2):
            snippets.append(f"{document.title}: {chunk}")
            if len(snippets) >= 3:
                break
        if len(snippets) >= 3:
            break

    if not snippets:
        return {
            "answer": (
                "Nao encontrei uma regra do condominio que responda essa pergunta com seguranca. "
                "Tente perguntar com termos como obras, piscina, pets, garagem ou salao."
            )
        }

    return {
        "answer": (
            "Estas sao as regras encontradas nos documentos do condominio:\n\n"
            + "\n\n".join(f"- {snippet}" for snippet in snippets)
        )
    }
