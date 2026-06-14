from app.schemas.announcements import AnnouncementGenerationRequest, AnnouncementGenerationResponse
from app.schemas.documents import DocumentAnswerRequest, DocumentAnswerResponse, DocumentSummaryResponse
from app.schemas.tickets import Ticket, TicketAIClassification
from app.services.content_service import get_document
from app.services.document_rag_service import answer_from_document, summarize_document_content
from sqlalchemy.orm import Session


def classify_ticket(ticket: Ticket) -> TicketAIClassification:
    description = f"{ticket.title} {ticket.description} {ticket.location}".lower()

    if "vazamento" in description or "agua" in description:
        return TicketAIClassification(
            category="hidraulica",
            priority="alta" if "eletrico" in description or "quadro" in description else "media",
            risk="risco eletrico" if "eletrico" in description or "quadro" in description else "risco de dano estrutural",
            suggested_owner="zelador e fornecedor hidraulico",
            next_action="Isolar a area e acionar fornecedor imediatamente.",
        )

    if "elevador" in description:
        return TicketAIClassification(
            category="elevador",
            priority="alta",
            risk="risco de seguranca e acessibilidade",
            suggested_owner="empresa de manutencao de elevadores",
            next_action="Bloquear uso do equipamento e solicitar atendimento tecnico.",
        )

    return TicketAIClassification(
        category="operacional",
        priority="media",
        risk="risco operacional moderado",
        suggested_owner="zelador",
        next_action="Validar local, registrar evidencia e definir responsavel.",
    )


def generate_announcement(payload: AnnouncementGenerationRequest) -> AnnouncementGenerationResponse:
    title = "Comunicado do condominio"
    if "agua" in payload.draft.lower() or "caixa" in payload.draft.lower():
        title = "Manutencao no abastecimento de agua"

    body = (
        "Informamos que sera realizada uma manutencao programada no condominio. "
        "Durante o periodo informado, podera haver impacto temporario para os moradores. "
        "Agradecemos a compreensao e manteremos todos atualizados sobre a conclusao."
    )

    if payload.tone == "urgente":
        body = f"Atencao: {body}"

    return AnnouncementGenerationResponse(title=title, body=body, tone=payload.tone)


def summarize_document(db: Session, document_id: int) -> DocumentSummaryResponse:
    document = get_document(db, document_id)
    summary = summarize_document_content(document)
    if document.summary != summary:
        document.summary = summary
        db.commit()
        db.refresh(document)
    return DocumentSummaryResponse(
        document_id=document_id,
        title=document.title,
        summary=summary,
    )


def answer_document_question(db: Session, document_id: int, payload: DocumentAnswerRequest) -> DocumentAnswerResponse:
    document = get_document(db, document_id)
    answer = answer_from_document(document, payload.question)

    return DocumentAnswerResponse(document_id=document_id, question=payload.question, answer=answer)

