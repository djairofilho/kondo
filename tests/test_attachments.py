from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_upload_download_and_delete_attachment(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    response = client.post(
        "/attachments",
        headers=manager["headers"],
        data={"condominium_id": "1", "entity_type": "ticket", "entity_id": "1", "uploaded_by_user_id": "999999", "visibility": "residents"},
        files={"file": ("leak.png", b"fake-image", "image/png")},
    )
    assert response.status_code == 200
    attachment = response.json()
    assert attachment["original_file_name"] == "leak.png"
    assert attachment["uploaded_by_user_id"] == manager["user_id"]
    assert attachment["storage_provider"] == "local"

    download = client.get(f"/attachments/{attachment['id']}/download", headers=manager["headers"])
    assert download.status_code == 200
    assert download.content == b"fake-image"

    delete = client.delete(f"/attachments/{attachment['id']}", headers=manager["headers"])
    assert delete.status_code == 200
    assert delete.json()["status"] == "deleted"


def test_rejects_unsupported_file_type(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    response = client.post(
        "/attachments",
        headers=manager["headers"],
        data={"condominium_id": "1", "entity_type": "ticket", "entity_id": "1"},
        files={"file": ("notes.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400

