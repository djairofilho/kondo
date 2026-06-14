from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.schemas.kanban import KanbanColumn, WorkItem, WorkItemCreate, WorkItemMove, WorkItemUpdate
from app.services.kanban_service import (
    create_work_item,
    list_columns,
    list_work_items,
    move_work_item,
    update_work_item,
    get_work_item_or_404,
)


router = APIRouter(prefix="/kanban", tags=["kanban"], dependencies=[Depends(require_roles("manager", "board_member"))])


@router.get("", response_model=list[WorkItem])
def get_kanban_items(db: Session = Depends(get_db)) -> list[WorkItem]:
    return list_work_items(db)


@router.get("/columns", response_model=list[KanbanColumn])
def get_kanban_columns() -> list[KanbanColumn]:
    return list_columns()


@router.post("/items", response_model=WorkItem, dependencies=[Depends(require_roles("manager"))])
def create_kanban_item(payload: WorkItemCreate, db: Session = Depends(get_db)) -> WorkItem:
    return create_work_item(db, payload)


@router.get("/items/{item_id}", response_model=WorkItem)
def get_kanban_item(item_id: int, db: Session = Depends(get_db)) -> WorkItem:
    return get_work_item_or_404(db, item_id)


@router.patch("/items/{item_id}", response_model=WorkItem, dependencies=[Depends(require_roles("manager"))])
def patch_kanban_item(item_id: int, payload: WorkItemUpdate, db: Session = Depends(get_db)) -> WorkItem:
    return update_work_item(db, item_id, payload)


@router.patch("/items/{item_id}/move", response_model=WorkItem, dependencies=[Depends(require_roles("manager"))])
def move_kanban_item(item_id: int, payload: WorkItemMove, db: Session = Depends(get_db)) -> WorkItem:
    return move_work_item(db, item_id, payload)

