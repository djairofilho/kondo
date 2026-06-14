from collections.abc import Callable

from fastapi.testclient import TestClient

from app.main import app


def test_core_endpoints_respond(create_auth_context: Callable[[str, bool], dict]) -> None:
    client = TestClient(app)
    manager = create_auth_context("manager")
    resident = create_auth_context("resident")

    assert client.get("/health").status_code == 200
    assert client.get("/dashboard", headers=resident["headers"]).status_code == 403

    for path in ["/dashboard", "/tickets", "/finance/summary", "/delinquencies"]:
        response = client.get(path, headers=manager["headers"])
        assert response.status_code == 200

