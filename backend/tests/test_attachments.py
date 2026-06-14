from fastapi.testclient import TestClient

from app.main import app


def test_upload_download_and_delete_attachment() -> None:
    client = TestClient(app)

    response = client.post(
        "/attachments",
        data={"condominium_id": "1", "entity_type": "ticket", "entity_id": "1", "visibility": "residents"},
        files={"file": ("leak.png", b"fake-image", "image/png")},
    )
    assert response.status_code == 200
    attachment = response.json()
    assert attachment["original_file_name"] == "leak.png"
    assert attachment["storage_provider"] == "local"

    download = client.get(f"/attachments/{attachment['id']}/download")
    assert download.status_code == 200
    assert download.content == b"fake-image"

    delete = client.delete(f"/attachments/{attachment['id']}")
    assert delete.status_code == 200
    assert delete.json()["status"] == "deleted"


def test_rejects_unsupported_file_type() -> None:
    client = TestClient(app)

    response = client.post(
        "/attachments",
        data={"condominium_id": "1", "entity_type": "ticket", "entity_id": "1"},
        files={"file": ("notes.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400

