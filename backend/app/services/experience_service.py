from sqlalchemy.orm import Session

from app.models import Announcement, Document, Expense, Ticket, Unit, WorkItem
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


def resident_rules(db: Session) -> dict:
    docs = db.query(Document).filter(Document.visibility.in_(["residents", "public"])).all()
    return {"documents": [{"id": doc.id, "title": doc.title, "type": doc.document_type} for doc in docs]}
