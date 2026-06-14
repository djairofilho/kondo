from fastapi.testclient import TestClient

from app.main import app


def test_core_endpoints_respond() -> None:
    client = TestClient(app)

    for path in ["/health", "/dashboard", "/tickets", "/finance/summary", "/delinquencies"]:
        response = client.get(path)
        assert response.status_code == 200

