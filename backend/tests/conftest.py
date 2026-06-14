from collections.abc import Callable
from datetime import timedelta
from uuid import uuid4

import pytest

from app.core.database import SessionLocal, init_db
from app.core.security import create_token, hash_password
from app.models import Condominium, Membership, Unit, User


@pytest.fixture
def create_auth_context() -> Callable[[str, bool], dict]:
    init_db()

    def factory(role: str = "resident", platform_admin: bool = False) -> dict:
        suffix = uuid4().hex
        with SessionLocal() as db:
            condominium = Condominium(
                name=f"Condominio Teste {suffix}",
                address="Rua Teste, 100",
                city="Sao Paulo",
                state="SP",
            )
            db.add(condominium)
            db.flush()

            unit = Unit(condominium_id=condominium.id, number=f"1{suffix[:4]}", block="A")
            other_unit = Unit(condominium_id=condominium.id, number=f"2{suffix[:4]}", block="B")
            db.add_all([unit, other_unit])
            db.flush()

            user = User(
                name=f"User {suffix}",
                email=f"user-{suffix}@kondo.local",
                password_hash=hash_password("kondo123"),
                is_platform_admin=platform_admin,
            )
            db.add(user)
            db.flush()

            if not platform_admin:
                db.add(
                    Membership(
                        user_id=user.id,
                        condominium_id=condominium.id,
                        unit_id=unit.id if role == "resident" else None,
                        role=role,
                    )
                )

            db.commit()
            token = create_token(str(user.id), timedelta(minutes=60), "access")
            return {
                "headers": {"Authorization": f"Bearer {token}"},
                "user_id": user.id,
                "condominium_id": condominium.id,
                "unit_id": unit.id,
                "other_unit_id": other_unit.id,
            }

    return factory
