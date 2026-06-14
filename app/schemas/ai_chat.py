from typing import Literal

from pydantic import BaseModel, Field


class AIChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    profile: Literal["sindico", "conselho", "morador"] | None = None
    route: str | None = None
    history: list[AIChatHistoryItem] = Field(default_factory=list, max_length=12)


class AIChatAction(BaseModel):
    label: str
    to: str
    kind: Literal["navigate"] = "navigate"


class AIChatResponse(BaseModel):
    answer: str
    actions: list[AIChatAction] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"
    source: Literal["ai", "mock"] = "mock"
    provider: str = "mock"
    model: str = "mock"
