from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import WorkItem
from app.schemas.kanban import KanbanColumn, WorkItemCreate, WorkItemMove, WorkItemUpdate


KANBAN_COLUMNS = [
    KanbanColumn(id="received", title="Recebido", order=1),
    KanbanColumn(id="in_review", title="Em analise", order=2),
    KanbanColumn(id="vendor_contacted", title="Fornecedor acionado", order=3),
    KanbanColumn(id="waiting_approval", title="Aguardando aprovacao", order=4),
    KanbanColumn(id="in_progress", title="Em execucao", order=5),
    KanbanColumn(id="resolved", title="Resolvido", order=6),
]


def list_columns() -> list[KanbanColumn]:
    return KANBAN_COLUMNS


def list_work_items(db: Session) -> list[WorkItem]:
    return db.query(WorkItem).order_by(WorkItem.created_at.desc()).all()


def get_work_item_or_404(db: Session, item_id: int) -> WorkItem:
    item = db.get(WorkItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work item not found")
    return item


def create_work_item(db: Session, payload: WorkItemCreate) -> WorkItem:
    item = WorkItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_work_item(db: Session, item_id: int, payload: WorkItemUpdate) -> WorkItem:
    item = get_work_item_or_404(db, item_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def move_work_item(db: Session, item_id: int, payload: WorkItemMove) -> WorkItem:
    item = get_work_item_or_404(db, item_id)
    item.status = payload.status
    db.commit()
    db.refresh(item)
    return item

