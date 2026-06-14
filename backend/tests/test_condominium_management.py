from fastapi.testclient import TestClient

from app.main import app


def test_condominium_unit_resident_and_membership_flow() -> None:
    client = TestClient(app)

    condo_response = client.post(
        "/condominiums",
        json={"name": "Condominio Teste", "address": "Rua Teste, 1", "city": "Sao Paulo", "state": "SP"},
    )
    assert condo_response.status_code == 200
    condominium_id = condo_response.json()["id"]

    unit_response = client.post(
        f"/condominiums/{condominium_id}/units",
        json={"condominium_id": condominium_id, "number": "101", "block": "A"},
    )
    assert unit_response.status_code == 200
    unit_id = unit_response.json()["id"]

    resident_response = client.post(
        f"/units/{unit_id}/residents",
        json={"unit_id": unit_id, "name": "Morador Teste", "email": "morador@kondo.local", "resident_type": "tenant"},
    )
    assert resident_response.status_code == 200

    user_response = client.post(
        "/auth/register",
        json={"name": "Gestor Teste", "email": "gestor-mgmt@kondo.local", "password": "kondo123"},
    )
    user_id = user_response.json()["user"]["id"]

    membership_response = client.post(
        f"/condominiums/{condominium_id}/memberships",
        json={"user_id": user_id, "condominium_id": condominium_id, "role": "manager"},
    )
    assert membership_response.status_code == 200

    overview = client.get(f"/condominiums/{condominium_id}/overview")
    assert overview.status_code == 200
    assert overview.json()["units"] == 1
    assert overview.json()["active_memberships"] == 1

