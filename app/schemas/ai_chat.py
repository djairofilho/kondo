from typing import Literal

from pydantic import BaseModel, Field


class AIChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    profile: Literal["sindico", "conselho", "morador"] | None = None
    route: str | None = None
    # Legado — mantido para compatibilidade com clientes que ainda enviam histórico manual.
    # Ignorado quando session_id é fornecido (o histórico real vem do banco).
    history: list[AIChatHistoryItem] = Field(default_factory=list, max_length=12)
    # ID da sessão de chat para continuar uma conversa existente.
    # None = nova sessão criada automaticamente.
    session_id: int | None = None


class AIChatAction(BaseModel):
    label: str
    to: str
    kind: Literal["navigate"] = "navigate"


class AIChatToolCall(BaseModel):
    tool: str
    summary: str


class AIChatAttachmentRef(BaseModel):
    id: int
    original_file_name: str
    content_type: str
    file_size: int
    download_url: str


class AIChatResponse(BaseModel):
    answer: str
    actions: list[AIChatAction] = Field(default_factory=list)
    tool_calls: list[AIChatToolCall] = Field(default_factory=list)
    attachments: list[AIChatAttachmentRef] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"
    source: Literal["ai", "mock"] = "mock"
    provider: str = "mock"
    model: str = "mock"
    # ID da sessão criada ou continuada — o frontend deve persistir e reenviar.
    session_id: int | None = None
