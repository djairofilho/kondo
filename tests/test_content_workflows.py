from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_document_crud_and_ai_helpers(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    create = client.post(
        "/documents",
        headers=manager["headers"],
        json={"condominium_id": manager["condominium_id"], "title": "Regimento Teste", "document_type": "rules", "content": "Obras somente em dias uteis.", "visibility": "residents"},
    )
    assert create.status_code == 200
    document_id = create.json()["id"]

    patch = client.patch(f"/documents/{document_id}", headers=manager["headers"], json={"summary": "Regras de convivencia."})
    assert patch.status_code == 200
    assert patch.json()["summary"] == "Regras de convivencia."

    summary = client.post(f"/documents/{document_id}/summarize", headers=manager["headers"])
    assert summary.status_code == 200
    assert "Obras somente em dias uteis" in summary.json()["summary"]

    answer = client.post(f"/documents/{document_id}/ask", headers=manager["headers"], json={"question": "Pode obra no sabado?"})
    assert answer.status_code == 200
    assert "Obras somente em dias uteis" in answer.json()["answer"]

    upload = client.post(
        "/documents/upload",
        headers=manager["headers"],
        data={"condominium_id": str(manager["condominium_id"]), "document_id": str(document_id), "uploaded_by_user_id": "999999", "visibility": "managers"},
        files={"file": ("regimento.pdf", b"pdf", "application/pdf")},
    )
    assert upload.status_code == 200
    assert upload.json()["entity_type"] == "document"
    assert upload.json()["uploaded_by_user_id"] == manager["user_id"]
    attachment_id = upload.json()["id"]

    attachments = client.get(f"/documents/{document_id}/attachments", headers=manager["headers"])
    assert attachments.status_code == 200
    assert attachments.json()[0]["id"] == attachment_id

    download = client.get(f"/documents/{document_id}/attachments/{attachment_id}/download", headers=manager["headers"])
    assert download.status_code == 200
    assert download.content == b"pdf"


def test_announcement_crud_publish_and_generation(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    create = client.post(
        "/announcements",
        headers=manager["headers"],
        json={"condominium_id": manager["condominium_id"], "title": "Aviso", "body": "Manutencao hoje.", "audience": "residents"},
    )
    assert create.status_code == 200
    announcement_id = create.json()["id"]

    publish = client.post(f"/announcements/{announcement_id}/publish", headers=manager["headers"])
    assert publish.status_code == 200
    assert publish.json()["status"] == "published"

    generated = client.post(
        "/announcements/generate-ai",
        headers=manager["headers"],
        json={"draft": "avisar falta de agua amanha", "tone": "formal"},
    )
    assert generated.status_code == 200

