from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.models import User


def test_admin_endpoints_require_platform_admin() -> None:
    client = TestClient(app)

    common_email = f"common-{uuid4().hex}@kondo.local"
    common = client.post(
        "/auth/register",
        json={"name": "Usuario Comum", "email": common_email, "password": "kondo123"},
    )
    common_token = common.json()["access_token"]
    forbidden = client.get("/admin/overview", headers={"Authorization": f"Bearer {common_token}"})
    assert forbidden.status_code == 403

    admin_email = f"admin-{uuid4().hex}@kondo.local"
    with SessionLocal() as db:
        admin = User(
            name="Admin Teste",
            email=admin_email,
            password_hash=hash_password("kondo123"),
            is_platform_admin=True,
        )
        db.add(admin)
        db.commit()

    login = client.post("/auth/login", json={"email": admin_email, "password": "kondo123"})
    admin_token = login.json()["access_token"]
    allowed = client.get("/admin/overview", headers={"Authorization": f"Bearer {admin_token}"})
    assert allowed.status_code == 200
    assert "condominiums" in allowed.json()

