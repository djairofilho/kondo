from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_manager_board_and_resident_experience_endpoints(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")
    board = create_auth_context("board_member")
    resident = create_auth_context("resident")

    for path in ["/manager/dashboard"]:
        response = client.get(path, headers=manager["headers"])
        assert response.status_code == 200

    for path in ["/board/dashboard", "/board/financial-transparency", "/board/maintenance-status"]:
        response = client.get(path, headers=board["headers"])
        assert response.status_code == 200

    for path in ["/resident-portal/home", "/resident-portal/my-tickets", "/resident-portal/rules"]:
        response = client.get(path, headers=resident["headers"])
        assert response.status_code == 200


def test_resident_portal_requires_auth() -> None:
    client = TestClient(app)

    response = client.get("/resident-portal/home")

    assert response.status_code == 401


def test_resident_portal_ignores_unit_override(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    response = client.get(
        f"/resident-portal/home?unit_id={resident['other_unit_id']}",
        headers=resident["headers"],
    )

    assert response.status_code == 200
    assert response.json()["unit"]["id"] == resident["unit_id"]


def test_manager_can_use_resident_portal_unit_override(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    response = client.get(
        f"/resident-portal/home?unit_id={manager['other_unit_id']}",
        headers=manager["headers"],
    )

    assert response.status_code == 200
    assert response.json()["unit"]["id"] == manager["other_unit_id"]


def test_manager_cannot_use_foreign_condominium_unit_override(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")
    foreign_resident = create_auth_context("resident")

    response = client.get(
        f"/resident-portal/home?unit_id={foreign_resident['unit_id']}",
        headers=manager["headers"],
    )

    assert response.status_code == 403


def test_resident_portal_can_create_ticket_for_own_unit_only(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    response = client.post(
        "/resident-portal/tickets",
        headers=resident["headers"],
        json={
            "condominium_id": 999999,
            "unit_id": resident["other_unit_id"],
            "title": "Barulho no portao",
            "description": "Portao faz barulho alto de madrugada.",
            "location": "Entrada da garagem",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Barulho no portao"
    assert response.json()["condominium_id"] == resident["condominium_id"]
    assert response.json()["unit_id"] == resident["unit_id"]
