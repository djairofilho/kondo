from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_financial_crud_and_payment_flow(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    revenue_response = client.post(
        "/revenues",
        headers=manager["headers"],
        json={"condominium_id": 1, "unit_id": 1, "description": "Taxa julho", "amount": "516.00"},
    )
    assert revenue_response.status_code == 200
    revenue_id = revenue_response.json()["id"]

    paid_revenue = client.patch(f"/revenues/{revenue_id}", headers=manager["headers"], json={"status": "paid"})
    assert paid_revenue.status_code == 200
    assert paid_revenue.json()["status"] == "paid"
    assert client.get(f"/revenues/{revenue_id}", headers=manager["headers"]).status_code == 200

    expense_response = client.post(
        "/expenses",
        headers=manager["headers"],
        json={"condominium_id": 1, "description": "Limpeza", "category": "operacional", "amount": "250.00"},
    )
    assert expense_response.status_code == 200
    assert client.get(f"/expenses/{expense_response.json()['id']}", headers=manager["headers"]).status_code == 200

    payment_response = client.post(
        "/payments",
        headers=manager["headers"],
        json={
            "condominium_id": 1,
            "unit_id": 1,
            "amount": "516.00",
            "payment_method": "pix",
            "payment_metadata": {
                "billing_mode": "separate",
                "breakdown": {
                    "condominio": "360.00",
                    "agua": "58.00",
                    "luz": "72.00",
                    "gas": "26.00",
                },
            },
        },
    )
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]
    assert client.get(f"/payments/{payment_id}", headers=manager["headers"]).status_code == 200

    boleto_response = client.post(f"/payments/{payment_id}/generate-boleto", headers=manager["headers"])
    assert boleto_response.status_code == 200
    assert boleto_response.json()["payment_method"] == "boleto"

    component_boleto_response = client.post(
        f"/payments/{payment_id}/components/agua/generate-boleto",
        headers=manager["headers"],
    )
    assert component_boleto_response.status_code == 200
    metadata = component_boleto_response.json()["payment_metadata"]
    assert metadata["component_boletos"]["agua"]["boleto_url"]
    assert metadata["component_boletos"]["agua"]["barcode"]

    paid_response = client.post(f"/payments/{payment_id}/mark-paid", headers=manager["headers"])
    assert paid_response.status_code == 200
    assert paid_response.json()["status"] == "paid"

    assert client.get("/finance/cashflow", headers=manager["headers"]).status_code == 200
    radar_response = client.get("/finance/expense-radar", headers=manager["headers"])
    assert radar_response.status_code == 200
    assert radar_response.json()["categories"]
    assert "confidence" in radar_response.json()

    report_response = client.get("/finance/monthly-report", headers=manager["headers"])
    assert report_response.status_code == 200
    assert report_response.json()["risks"]
    assert report_response.json()["next_steps"]
    assert report_response.json()["council_summary"]

    assert client.post("/finance/insights-ai", headers=manager["headers"]).status_code == 200

    insights_response = client.post("/finance/expense-insights-ai", headers=manager["headers"])
    assert insights_response.status_code == 200
    assert insights_response.json()["recommendations"]
    assert insights_response.json()["council_summary"]


def test_board_member_cannot_write_finance_and_denial_is_audited(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    board = create_auth_context("board_member")

    denied = client.post(
        "/revenues",
        headers=board["headers"],
        json={"condominium_id": board["condominium_id"], "unit_id": board["unit_id"], "description": "Taxa", "amount": "100.00"},
    )

    assert denied.status_code == 403

    audit = client.get("/audit/events", headers=board["headers"])
    assert audit.status_code == 200
    assert any(event["action"] == "authorization.denied" and event["actor_user_id"] == board["user_id"] for event in audit.json())


def test_agreement_lifecycle(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")

    simulate_response = client.post(
        "/agreements/simulate",
        headers=manager["headers"],
        json={
            "unit_id": manager["unit_id"],
            "amount_due": "1548.00",
            "entry_amount": "300.00",
            "installments": 4,
            "fine_amount": "77.40",
        },
    )
    assert simulate_response.status_code == 200
    assert simulate_response.json()["total_due"] == "1625.40"
    assert simulate_response.json()["financed_amount"] == "1325.40"

    create_response = client.post(
        "/agreements",
        headers=manager["headers"],
        json={
            "unit_id": manager["unit_id"],
            "entry_amount": "400.00",
            "installments": 4,
            "monthly_installment": "287.00",
        },
    )
    assert create_response.status_code == 200
    agreement_id = create_response.json()["id"]

    payment_response = client.post(f"/agreements/{agreement_id}/payments", headers=manager["headers"])
    assert payment_response.status_code == 200
    assert payment_response.json()["agreement_id"] == agreement_id

    cancel_response = client.post(f"/agreements/{agreement_id}/cancel", headers=manager["headers"])
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

