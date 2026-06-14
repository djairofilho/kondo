from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Quote, Vendor
from app.schemas.vendors import QuoteComparison, QuoteCreate, QuoteUpdate, VendorCreate, VendorUpdate


def _get_or_404(db: Session, model, entity_id: int):
    entity = db.get(model, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return entity


def list_vendors(db: Session) -> list[Vendor]:
    return db.query(Vendor).order_by(Vendor.name).all()


def create_vendor(db: Session, payload: VendorCreate) -> Vendor:
    entity = Vendor(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def get_vendor(db: Session, vendor_id: int) -> Vendor:
    return _get_or_404(db, Vendor, vendor_id)


def update_vendor(db: Session, vendor_id: int, payload: VendorUpdate) -> Vendor:
    entity = get_vendor(db, vendor_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    db.commit()
    db.refresh(entity)
    return entity


def list_quotes(db: Session) -> list[Quote]:
    return db.query(Quote).order_by(Quote.created_at.desc()).all()


def create_quote(db: Session, payload: QuoteCreate) -> Quote:
    entity = Quote(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def compare_quotes(db: Session) -> QuoteComparison:
    quotes = db.query(Quote).filter(Quote.amount.isnot(None)).order_by(Quote.amount.asc()).limit(3).all()
    if not quotes:
        return QuoteComparison(recommendation="Nenhum orçamento comparável.", rationale="Cadastre valores para comparar.")

    best = quotes[0]
    return QuoteComparison(
        recommendation=f"Priorizar orçamento {best.id}: {best.title}.",
        rationale="Recomendação simulada considerando menor custo entre orçamentos com valor informado.",
    )

