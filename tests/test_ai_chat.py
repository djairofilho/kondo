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
