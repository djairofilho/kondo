from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.schemas.announcements import AnnouncementGenerationRequest, AnnouncementGenerationResponse
from app.schemas.documents import DocumentAnswerRequest, DocumentAnswerResponse, DocumentSummaryResponse
from app.schemas.tickets import TicketAIClassification, TicketCreate
from app.schemas.vendors import QuoteComparison
from app.services.ai_service import answer_document_question, classify_ticket, generate_announcement, summarize_document
from app.services.dashboard_service import get_dashboard_summary
from app.services.finance_service import get_finance_summary
from app.services.ticket_service import create_ticket
from app.services.vendor_service import compare_quotes


router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(require_roles("manager", "board_member"))])


@router.post("/priorities")
def ai_priorities() -> dict:
    return {"priorities": get_dashboard_summary().ai_priorities}


@router.post("/ticket-classification", response_model=TicketAIClassification)
def ai_ticket_classification(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketAIClassification:
    ticket = create_ticket(db, payload)
    return classify_ticket(ticket)


@router.post("/financial-insights")
def ai_financial_insights(db: Session = Depends(get_db)) -> dict:
    return {"insights": get_finance_summary(db).insights}


@router.post("/agreement-recommendation")
def ai_agreement_recommendation() -> dict:
    return {"recommendation": "Entrada minima de 20% e ate 4 parcelas para reduzir risco de caixa."}


@router.post("/announcement-generation", response_model=AnnouncementGenerationResponse)
def ai_announcement_generation(payload: AnnouncementGenerationRequest) -> AnnouncementGenerationResponse:
    return generate_announcement(payload)


@router.post("/document-summary/{document_id}", response_model=DocumentSummaryResponse)
def ai_document_summary(document_id: int) -> DocumentSummaryResponse:
    return summarize_document(document_id)


@router.post("/document-question/{document_id}", response_model=DocumentAnswerResponse)
def ai_document_question(document_id: int, payload: DocumentAnswerRequest) -> DocumentAnswerResponse:
    return answer_document_question(document_id, payload)


@router.post("/vendor-quote-comparison", response_model=QuoteComparison)
def ai_vendor_quote_comparison(db: Session = Depends(get_db)) -> QuoteComparison:
    return compare_quotes(db)

