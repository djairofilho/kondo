from app.schemas.announcements import AnnouncementGenerationRequest, AnnouncementGenerationResponse
from app.schemas.documents import DocumentAnswerRequest, DocumentAnswerResponse, DocumentSummaryResponse
from app.schemas.tickets import Ticket, TicketAIClassification


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


def summarize_document(document_id: int) -> DocumentSummaryResponse:
    return DocumentSummaryResponse(
        document_id=document_id,
        title="Regimento interno",
        summary=(
            "O documento consolida regras de convivencia, horarios de obra, uso de areas comuns "
            "e responsabilidades dos moradores."
        ),
    )


def answer_document_question(document_id: int, payload: DocumentAnswerRequest) -> DocumentAnswerResponse:
    answer = (
        "Segundo o regimento cadastrado, obras com ruido devem ocorrer em dias uteis, "
        "em horario comercial. Aos sabados, apenas servicos sem ruido devem ser permitidos. "
        "Confirme com o sindico em casos excepcionais."
    )

    return DocumentAnswerResponse(document_id=document_id, question=payload.question, answer=answer)

