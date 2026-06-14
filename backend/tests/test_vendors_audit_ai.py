from fastapi.testclient import TestClient

from app.main import app


def test_vendor_quote_audit_and_ai_endpoints() -> None:
    client = TestClient(app)

    vendor = client.post("/vendors", json={"condominium_id": 1, "name": "Fornecedor Teste", "category": "hidraulica"})
    assert vendor.status_code == 200
    vendor_id = vendor.json()["id"]

    quote = client.post(
        "/quotes",
        json={"condominium_id": 1, "vendor_id": vendor_id, "title": "Reparo", "amount": "1200.00", "scope": "Reparo hidraulico"},
    )
    assert quote.status_code == 200

    comparison = client.post("/quotes/compare-ai")
    assert comparison.status_code == 200
    assert "recommendation" in comparison.json()

    audit = client.post(
        "/audit/events",
        json={"condominium_id": 1, "action": "vendor.created", "entity_type": "vendor", "entity_id": vendor_id},
    )
    assert audit.status_code == 200

    for path in [
        "/ai/priorities",
        "/ai/financial-insights",
        "/ai/agreement-recommendation",
        "/ai/vendor-quote-comparison",
    ]:
        response = client.post(path)
        assert response.status_code == 200

