from fastapi.testclient import TestClient

from app.main import app


def test_document_crud_and_ai_helpers() -> None:
    client = TestClient(app)

    create = client.post(
        "/documents",
        json={"condominium_id": 1, "title": "Regimento Teste", "document_type": "rules", "content": "Obras somente em dias uteis.", "visibility": "residents"},
    )
    assert create.status_code == 200
    document_id = create.json()["id"]

    patch = client.patch(f"/documents/{document_id}", json={"summary": "Regras de convivencia."})
    assert patch.status_code == 200
    assert patch.json()["summary"] == "Regras de convivencia."

    summary = client.post(f"/documents/{document_id}/summarize")
    assert summary.status_code == 200

    answer = client.post(f"/documents/{document_id}/ask", json={"question": "Pode obra no sabado?"})
    assert answer.status_code == 200


def test_announcement_crud_publish_and_generation() -> None:
    client = TestClient(app)

    create = client.post(
        "/announcements",
        json={"condominium_id": 1, "title": "Aviso", "body": "Manutencao hoje.", "audience": "residents"},
    )
    assert create.status_code == 200
    announcement_id = create.json()["id"]

    publish = client.post(f"/announcements/{announcement_id}/publish")
    assert publish.status_code == 200
    assert publish.json()["status"] == "published"

    generated = client.post(
        "/announcements/generate-ai",
        json={"draft": "avisar falta de agua amanha", "tone": "formal"},
    )
    assert generated.status_code == 200

