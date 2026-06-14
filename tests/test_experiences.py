from collections.abc import Callable
from datetime import datetime

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models import CalendarEvent, Document, Membership, Payment, Resident


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


def test_resident_rules_ask_uses_visible_rules_document(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    with SessionLocal() as db:
        db.add(
            Document(
                condominium_id=resident["condominium_id"],
                title="Regimento de obras",
                document_type="rules",
                content="Obras com ruido sao permitidas de segunda a sexta, das 9h as 17h.",
                visibility="residents",
            )
        )
        db.commit()

    response = client.post(
        "/resident-portal/rules/ask",
        headers=resident["headers"],
        json={"question": "Qual horario de obra com ruido?"},
    )

    assert response.status_code == 200
    assert "Obras com ruido" in response.json()["answer"]


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


def test_manager_can_read_board_views(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    response = client.get("/board/dashboard", headers=manager["headers"])

    assert response.status_code == 200


def test_manager_cannot_use_foreign_condominium_unit_override(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")
    foreign_resident = create_auth_context("resident")

    response = client.get(
        f"/resident-portal/home?unit_id={foreign_resident['unit_id']}",
        headers=manager["headers"],
    )

    assert response.status_code == 403


def test_resident_payments_boleto_and_onboarding_are_unit_scoped(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    with SessionLocal() as db:
        own_payment = Payment(
            condominium_id=resident["condominium_id"],
            unit_id=resident["unit_id"],
            amount="516.00",
            status="pending",
            payment_metadata={
                "billing_mode": "separate",
                "breakdown": {
                    "condominio": "360.00",
                    "agua": "58.00",
                    "luz": "72.00",
                    "gas": "26.00",
                },
            },
        )
        other_payment = Payment(
            condominium_id=resident["condominium_id"],
            unit_id=resident["other_unit_id"],
            amount="760.00",
            status="pending",
            payment_metadata={
                "billing_mode": "separate",
                "breakdown": {
                    "condominio": "540.00",
                    "agua": "80.00",
                    "luz": "98.00",
                    "gas": "42.00",
                },
            },
        )
        db.add_all([own_payment, other_payment])
        db.add(
            Resident(
                unit_id=resident["unit_id"],
                name="Morador Teste",
                email="morador@test.local",
            )
        )
        db.flush()
        other_payment_id = other_payment.id
        db.commit()

    payments = client.get("/resident-portal/payments", headers=resident["headers"])
    assert payments.status_code == 200
    assert len(payments.json()) == 1
    payment_id = payments.json()[0]["id"]

    boleto = client.post(
        f"/resident-portal/payments/{payment_id}/generate-boleto",
        headers=resident["headers"],
    )
    assert boleto.status_code == 200
    assert boleto.json()["payment_method"] == "boleto"

    component_boleto = client.post(
        f"/resident-portal/payments/{payment_id}/components/agua/generate-boleto",
        headers=resident["headers"],
    )
    assert component_boleto.status_code == 200
    assert component_boleto.json()["payment_metadata"]["component_boletos"]["agua"]["barcode"]

    foreign_component_boleto = client.post(
        f"/resident-portal/payments/{other_payment_id}/components/agua/generate-boleto",
        headers=resident["headers"],
    )
    assert foreign_component_boleto.status_code == 403

    onboarding = client.post(
        "/resident-portal/onboarding",
        headers=resident["headers"],
        json={"phone": "11999990000", "household_info": "2 moradores", "completed": True},
    )
    assert onboarding.status_code == 200
    assert onboarding.json()["completed"] is True


def test_resident_calendar_filters_public_and_own_unit(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    with SessionLocal() as db:
        db.add_all(
            [
                CalendarEvent(
                    condominium_id=resident["condominium_id"],
                    title="Assembleia",
                    category="event",
                    start_at=datetime(2026, 6, 24, 19, 30),
                    visibility="residents",
                    status="scheduled",
                ),
                CalendarEvent(
                    condominium_id=resident["condominium_id"],
                    unit_id=resident["other_unit_id"],
                    title="Reserva vizinho",
                    category="reservation",
                    start_at=datetime(2026, 6, 25, 19, 30),
                    visibility="unit",
                    status="scheduled",
                ),
            ]
        )
        db.commit()

    response = client.get("/resident-portal/calendar", headers=resident["headers"])

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert "Assembleia" in titles
    assert "Reserva vizinho" not in titles


def test_board_member_can_only_view_own_resident_unit(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    board = create_auth_context("board_member")

    with SessionLocal() as db:
        db.add(
            Membership(
                user_id=board["user_id"],
                condominium_id=board["condominium_id"],
                unit_id=board["unit_id"],
                role="resident",
            )
        )
        db.commit()

    own = client.get(f"/resident-portal/home?unit_id={board['unit_id']}", headers=board["headers"])
    other = client.get(
        f"/resident-portal/home?unit_id={board['other_unit_id']}",
        headers=board["headers"],
    )

    assert own.status_code == 200
    assert other.status_code == 403


def test_resident_portal_can_create_ticket_for_own_unit_only(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")

    simple_response = client.post(
        "/resident-portal/tickets",
        headers=resident["headers"],
        json={
            "title": "Infiltracao na parede",
            "description": "A parede do quarto esta com umidade.",
            "location": "Quarto",
        },
    )

    assert simple_response.status_code == 200
    assert simple_response.json()["unit_id"] == resident["unit_id"]

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
