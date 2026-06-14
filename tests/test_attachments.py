from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models import Ticket


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


def test_resident_can_upload_attachment_to_own_ticket(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    with SessionLocal() as db:
        ticket = Ticket(
            condominium_id=resident["condominium_id"],
            unit_id=resident["unit_id"],
            title="Vazamento no banheiro",
            description="A pia do banheiro esta vazando.",
            location="Banheiro",
            status="received",
        )
        db.add(ticket)
        db.commit()
        ticket_id = ticket.id

    response = client.post(
        f"/resident-portal/tickets/{ticket_id}/attachments",
        headers=resident["headers"],
        files={"file": ("banheiro.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["entity_type"] == "ticket"
    assert body["entity_id"] == ticket_id
    assert body["uploaded_by_user_id"] == resident["user_id"]


def test_resident_cannot_upload_attachment_to_other_unit_ticket(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    with SessionLocal() as db:
        ticket = Ticket(
            condominium_id=resident["condominium_id"],
            unit_id=resident["other_unit_id"],
            title="Problema em outra unidade",
            description="Chamado de unidade diferente.",
            location="Unidade B",
            status="received",
        )
        db.add(ticket)
        db.commit()
        ticket_id = ticket.id

    response = client.post(
        f"/resident-portal/tickets/{ticket_id}/attachments",
        headers=resident["headers"],
        files={"file": ("outra.png", b"fake-image", "image/png")},
    )

    assert response.status_code == 403


def test_resident_cannot_list_other_unit_ticket_attachments(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    with SessionLocal() as db:
        ticket = Ticket(
            condominium_id=resident["condominium_id"],
            unit_id=resident["other_unit_id"],
            title="Chamado privado",
            description="Chamado de outra unidade.",
            location="Unidade B",
            status="received",
        )
        db.add(ticket)
        db.commit()
        ticket_id = ticket.id

    response = client.get(f"/tickets/{ticket_id}/attachments", headers=resident["headers"])

    assert response.status_code == 403

