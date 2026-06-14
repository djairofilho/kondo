from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_ai_chat_manager_uses_mock_without_anthropic_key(create_auth_context) -> None:
    settings = get_settings()
    previous_key = settings.anthropic_api_key
    settings.anthropic_api_key = None
    client = TestClient(app)
    auth = create_auth_context("manager")

    response = client.post(
        "/ai/chat",
        headers=auth["headers"],
        data={"message": "organize meu dia", "profile": "sindico", "route": "/sindico"},
    )

    settings.anthropic_api_key = previous_key
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "mock"
    assert payload["actions"]
    assert payload["answer"]


def test_ai_chat_allows_resident_without_restricted_finance_context(create_auth_context) -> None:
    settings = get_settings()
    previous_key = settings.anthropic_api_key
    settings.anthropic_api_key = None
    client = TestClient(app)
    auth = create_auth_context("resident")

    response = client.post(
        "/ai/chat",
        headers=auth["headers"],
        data={"message": "me mostre caixa e inadimplencia", "profile": "morador", "route": "/morador"},
    )

    settings.anthropic_api_key = previous_key
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "mock"
    assert "restritos" in payload["answer"]
    assert all(action["to"] != "/financeiro" for action in payload["actions"])


def test_ai_chat_blocks_resident_creating_announcement(create_auth_context) -> None:
    settings = get_settings()
    previous_key = settings.anthropic_api_key
    settings.anthropic_api_key = None
    client = TestClient(app)
    auth = create_auth_context("resident")

    response = client.post(
        "/ai/chat",
        headers=auth["headers"],
        data={
            "message": "cria um comunicado avisando manutencao no elevador",
            "profile": "morador",
            "route": "/morador",
        },
    )

    settings.anthropic_api_key = previous_key
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "guardrail"
    assert payload["tool_calls"] == [
        {"tool": "guardrail", "summary": "resident_announcement_write_denied"}
    ]
    assert "nao podem criar" in payload["answer"].lower()


def test_ai_chat_blocks_board_expense_write(create_auth_context) -> None:
    settings = get_settings()
    previous_key = settings.anthropic_api_key
    settings.anthropic_api_key = None
    client = TestClient(app)
    auth = create_auth_context("board_member")

    response = client.post(
        "/ai/chat",
        headers=auth["headers"],
        data={
            "message": "registre uma despesa de 300 reais para limpeza",
            "profile": "conselho",
            "route": "/conselho",
        },
    )

    settings.anthropic_api_key = previous_key
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "guardrail"
    assert payload["tool_calls"] == [
        {"tool": "guardrail", "summary": "board_expense_write_denied"}
    ]
    assert "exclusivo do sindico" in payload["answer"].lower()
