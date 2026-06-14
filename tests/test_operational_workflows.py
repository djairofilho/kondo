from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_ticket_creation_creates_kanban_item_and_can_move(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    ticket_response = client.post(
        "/tickets",
        headers=manager["headers"],
        json={
            "condominium_id": 1,
            "unit_id": 304,
            "title": "Portao travando",
            "description": "Portao da garagem esta travando ao abrir.",
            "location": "Garagem",
        },
    )
    assert ticket_response.status_code == 201
    ticket = ticket_response.json()
    assert ticket["status"] == "received"

    kanban_response = client.get("/kanban", headers=manager["headers"])
    assert kanban_response.status_code == 200
    items = kanban_response.json()
    item = next(row for row in items if row["ticket_id"] == ticket["id"])

    move_response = client.patch(f"/kanban/items/{item['id']}/move", headers=manager["headers"], json={"status": "in_progress"})
    assert move_response.status_code == 200
    assert move_response.json()["status"] == "in_progress"


def test_ticket_status_update_moves_related_work_items(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    ticket_response = client.post(
        "/tickets",
        headers=manager["headers"],
        json={
            "condominium_id": 1,
            "unit_id": 304,
            "title": "Luz do corredor",
            "description": "Luz do corredor do terceiro andar esta piscando.",
            "location": "3 andar",
        },
    )
    ticket_id = ticket_response.json()["id"]

    response = client.patch(f"/tickets/{ticket_id}/status", headers=manager["headers"], json={"status": "resolved"})

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_ticket_comments_and_assign(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    ticket_response = client.post(
        "/tickets",
        headers=manager["headers"],
        json={
            "condominium_id": 1,
            "unit_id": 1,
            "title": "Comentario teste",
            "description": "Chamado para comentario.",
            "location": "Hall",
        },
    )
    ticket_id = ticket_response.json()["id"]

    comment = client.post(
        f"/tickets/{ticket_id}/comments",
        headers=manager["headers"],
        json={"body": "Fornecedor acionado.", "visibility": "residents"},
    )
    assert comment.status_code == 200
    assert comment.json()["body"] == "Fornecedor acionado."

    comments = client.get(f"/tickets/{ticket_id}/comments", headers=manager["headers"])
    assert comments.status_code == 200
    assert len(comments.json()) >= 1

    assigned = client.patch(f"/tickets/{ticket_id}/assign", headers=manager["headers"], json={"assigned_to_user_id": 1})
    assert assigned.status_code == 200


def test_ticket_comment_author_spoof_payload_is_ignored(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")
    other_user = create_auth_context("resident")

    ticket_response = client.post(
        "/tickets",
        headers=manager["headers"],
        json={
            "condominium_id": 1,
            "unit_id": 1,
            "title": "Spoof comentario",
            "description": "Chamado para validar autor.",
            "location": "Hall",
        },
    )
    ticket_id = ticket_response.json()["id"]

    comment = client.post(
        f"/tickets/{ticket_id}/comments",
        headers=manager["headers"],
        json={"author_user_id": other_user["user_id"], "body": "Autor real vem do token.", "visibility": "managers"},
    )

    assert comment.status_code == 200
    assert comment.json()["author_user_id"] == manager["user_id"]
