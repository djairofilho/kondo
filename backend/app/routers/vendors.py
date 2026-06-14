from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.schemas.vendors import Quote, QuoteComparison, QuoteCreate, Vendor, VendorCreate, VendorUpdate
from app.services.vendor_service import compare_quotes, create_quote, create_vendor, get_vendor, list_quotes, list_vendors, update_vendor


router = APIRouter(tags=["vendors"], dependencies=[Depends(require_roles("manager", "board_member"))])


@router.get("/vendors", response_model=list[Vendor])
def get_vendors(db: Session = Depends(get_db)) -> list[Vendor]:
    return list_vendors(db)


@router.post("/vendors", response_model=Vendor, dependencies=[Depends(require_roles("manager"))])
def post_vendor(payload: VendorCreate, db: Session = Depends(get_db)) -> Vendor:
    return create_vendor(db, payload)


@router.get("/vendors/{vendor_id}", response_model=Vendor)
def get_vendor_route(vendor_id: int, db: Session = Depends(get_db)) -> Vendor:
    return get_vendor(db, vendor_id)


@router.patch("/vendors/{vendor_id}", response_model=Vendor, dependencies=[Depends(require_roles("manager"))])
def patch_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)) -> Vendor:
    return update_vendor(db, vendor_id, payload)


@router.get("/quotes", response_model=list[Quote])
def get_quotes(db: Session = Depends(get_db)) -> list[Quote]:
    return list_quotes(db)


@router.post("/quotes", response_model=Quote, dependencies=[Depends(require_roles("manager"))])
def post_quote(payload: QuoteCreate, db: Session = Depends(get_db)) -> Quote:
    return create_quote(db, payload)


@router.post("/quotes/compare-ai", response_model=QuoteComparison)
def post_compare_quotes(db: Session = Depends(get_db)) -> QuoteComparison:
    return compare_quotes(db)

