from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_and_me_flow() -> None:
    client = TestClient(app)
    email = f"user-{uuid4().hex}@kondo.local"

    register_response = client.post(
        "/auth/register",
        json={"name": "Teste Kondo", "email": email, "password": "kondo123"},
    )
    assert register_response.status_code == 200
    register_payload = register_response.json()
    assert register_payload["token_type"] == "bearer"
    assert register_payload["user"]["email"] == email

    login_response = client.post("/auth/login", json={"email": email, "password": "kondo123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email


def test_me_requires_token() -> None:
    client = TestClient(app)

    response = client.get("/me")

    assert response.status_code == 401

