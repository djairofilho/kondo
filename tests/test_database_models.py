from app.core.database import Base, engine, init_db


def test_database_models_create_expected_tables() -> None:
    init_db()

    expected_tables = {
        "agreements",
        "announcements",
        "attachments",
        "audit_events",
        "condominiums",
        "delinquencies",
        "documents",
        "expenses",
        "memberships",
        "payments",
        "quotes",
        "residents",
        "revenues",
        "tickets",
        "units",
        "users",
        "vendors",
        "work_items",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))

    with engine.connect() as connection:
        table_names = set(connection.dialect.get_table_names(connection))

    assert expected_tables.issubset(table_names)

