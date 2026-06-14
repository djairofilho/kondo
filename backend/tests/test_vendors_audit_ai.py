from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_vendor_quote_audit_and_ai_endpoints(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")
    admin = create_auth_context("resident", platform_admin=True)

    vendor = client.post("/vendors", headers=manager["headers"], json={"condominium_id": 1, "name": "Fornecedor Teste", "category": "hidraulica"})
    assert vendor.status_code == 200
    vendor_id = vendor.json()["id"]

    quote = client.post(
        "/quotes",
        headers=manager["headers"],
        json={"condominium_id": 1, "vendor_id": vendor_id, "title": "Reparo", "amount": "1200.00", "scope": "Reparo hidraulico"},
    )
    assert quote.status_code == 200

    comparison = client.post("/quotes/compare-ai", headers=manager["headers"])
    assert comparison.status_code == 200
    assert "recommendation" in comparison.json()

    audit = client.post(
        "/audit/events",
        headers=admin["headers"],
        json={"condominium_id": 1, "action": "vendor.created", "entity_type": "vendor", "entity_id": vendor_id},
    )
    assert audit.status_code == 200

    for path in [
        "/ai/priorities",
        "/ai/financial-insights",
        "/ai/agreement-recommendation",
        "/ai/vendor-quote-comparison",
    ]:
        response = client.post(path, headers=manager["headers"])
        assert response.status_code == 200


def test_audit_events_authorization(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    resident = create_auth_context("resident")
    board = create_auth_context("board_member")
    admin = create_auth_context("resident", platform_admin=True)

    assert client.get("/audit/events").status_code == 401
    assert client.get("/audit/events", headers=resident["headers"]).status_code == 403
    assert client.get("/audit/events", headers=board["headers"]).status_code == 200

    payload = {"condominium_id": 1, "action": "security.test", "entity_type": "audit", "entity_id": 1}
    assert client.post("/audit/events", headers=board["headers"], json=payload).status_code == 403
    assert client.post("/audit/events", headers=admin["headers"], json=payload).status_code == 200
