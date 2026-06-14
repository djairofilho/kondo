import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models import User
from app.schemas.ai_chat import AIChatHistoryItem, AIChatRequest, AIChatResponse
from app.schemas.announcements import AnnouncementGenerationRequest, AnnouncementGenerationResponse
from app.schemas.documents import DocumentAnswerRequest, DocumentAnswerResponse, DocumentSummaryResponse
from app.schemas.tickets import TicketAIClassification, TicketCreate
from app.schemas.vendors import QuoteComparison
from app.services.ai_chat_service import chat_with_kondo_ai
from app.services.ai_service import answer_document_question, classify_ticket, generate_announcement, summarize_document
from app.services.dashboard_service import get_dashboard_summary
from app.services.finance_service import get_finance_summary
from app.services.ticket_service import create_ticket
from app.services.vendor_service import compare_quotes


router = APIRouter(prefix="/ai", tags=["ai"])

manager_or_board = Depends(require_roles("manager", "board_member"))


@router.post(
    "/chat",
    response_model=AIChatResponse,
    dependencies=[Depends(require_roles("manager", "board_member", "resident"))],
)
async def ai_chat(
    message: str = Form(...),
    profile: str | None = Form(None),
    route: str | None = Form(None),
    session_id: int | None = Form(None),
    history: str = Form(default="[]"),
    files: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIChatResponse:
    try:
        parsed_history = [AIChatHistoryItem(**item) for item in json.loads(history)]
    except Exception:
        parsed_history = []

    valid_profiles = {"sindico", "conselho", "morador"}
    safe_profile = profile if profile in valid_profiles else None

    payload = AIChatRequest(
        message=message,
        profile=safe_profile,
        route=route,
        session_id=session_id,
        history=parsed_history,
    )
    valid_files = [f for f in files if f.filename or f.size]
    return await chat_with_kondo_ai(db, current_user, payload, files=valid_files or None)


@router.post("/priorities", dependencies=[manager_or_board])
def ai_priorities() -> dict:
    return {"priorities": get_dashboard_summary().ai_priorities}


@router.post("/ticket-classification", response_model=TicketAIClassification, dependencies=[manager_or_board])
def ai_ticket_classification(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketAIClassification:
    ticket = create_ticket(db, payload)
    return classify_ticket(ticket)


@router.post("/financial-insights", dependencies=[manager_or_board])
def ai_financial_insights(db: Session = Depends(get_db)) -> dict:
    return {"insights": get_finance_summary(db).insights}


@router.post("/agreement-recommendation", dependencies=[manager_or_board])
def ai_agreement_recommendation() -> dict:
    return {"recommendation": "Entrada minima de 20% e ate 4 parcelas para reduzir risco de caixa."}


@router.post("/announcement-generation", response_model=AnnouncementGenerationResponse, dependencies=[manager_or_board])
def ai_announcement_generation(payload: AnnouncementGenerationRequest) -> AnnouncementGenerationResponse:
    return generate_announcement(payload)


@router.post("/document-summary/{document_id}", response_model=DocumentSummaryResponse, dependencies=[manager_or_board])
def ai_document_summary(document_id: int) -> DocumentSummaryResponse:
    return summarize_document(document_id)


@router.post("/document-question/{document_id}", response_model=DocumentAnswerResponse, dependencies=[manager_or_board])
def ai_document_question(document_id: int, payload: DocumentAnswerRequest) -> DocumentAnswerResponse:
    return answer_document_question(document_id, payload)


@router.post("/vendor-quote-comparison", response_model=QuoteComparison, dependencies=[manager_or_board])
def ai_vendor_quote_comparison(db: Session = Depends(get_db)) -> QuoteComparison:
    return compare_quotes(db)
