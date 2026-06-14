from fastapi.testclient import TestClient

from app.main import app


def test_financial_crud_and_payment_flow() -> None:
    client = TestClient(app)

    revenue_response = client.post(
        "/revenues",
        json={"condominium_id": 1, "unit_id": 1, "description": "Taxa julho", "amount": "516.00"},
    )
    assert revenue_response.status_code == 200
    revenue_id = revenue_response.json()["id"]

    paid_revenue = client.patch(f"/revenues/{revenue_id}", json={"status": "paid"})
    assert paid_revenue.status_code == 200
    assert paid_revenue.json()["status"] == "paid"

    expense_response = client.post(
        "/expenses",
        json={"condominium_id": 1, "description": "Limpeza", "category": "operacional", "amount": "250.00"},
    )
    assert expense_response.status_code == 200

    payment_response = client.post(
        "/payments",
        json={"condominium_id": 1, "unit_id": 1, "amount": "516.00", "payment_method": "pix"},
    )
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    boleto_response = client.post(f"/payments/{payment_id}/generate-boleto")
    assert boleto_response.status_code == 200
    assert boleto_response.json()["payment_method"] == "boleto"

    paid_response = client.post(f"/payments/{payment_id}/mark-paid")
    assert paid_response.status_code == 200
    assert paid_response.json()["status"] == "paid"


def test_agreement_lifecycle() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/agreements",
        json={
            "unit_id": 1,
            "entry_amount": "400.00",
            "installments": 4,
            "monthly_installment": "287.00",
        },
    )
    assert create_response.status_code == 200
    agreement_id = create_response.json()["id"]

    payment_response = client.post(f"/agreements/{agreement_id}/payments")
    assert payment_response.status_code == 200
    assert payment_response.json()["agreement_id"] == agreement_id

    cancel_response = client.post(f"/agreements/{agreement_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

