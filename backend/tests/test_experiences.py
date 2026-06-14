from fastapi.testclient import TestClient

from app.main import app


def test_manager_board_and_resident_experience_endpoints() -> None:
    client = TestClient(app)

    for path in [
        "/manager/dashboard",
        "/board/dashboard",
        "/board/financial-transparency",
        "/board/maintenance-status",
        "/resident-portal/home",
        "/resident-portal/my-tickets",
        "/resident-portal/rules",
    ]:
        response = client.get(path)
        assert response.status_code == 200


def test_resident_portal_can_create_ticket() -> None:
    client = TestClient(app)

    response = client.post(
        "/resident-portal/tickets",
        json={
            "condominium_id": 1,
            "unit_id": 1,
            "title": "Barulho no portao",
            "description": "Portao faz barulho alto de madrugada.",
            "location": "Entrada da garagem",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Barulho no portao"

