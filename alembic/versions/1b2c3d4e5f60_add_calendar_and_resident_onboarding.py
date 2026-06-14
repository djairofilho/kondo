"""add calendar and resident onboarding

Revision ID: 1b2c3d4e5f60
Revises: 88da1ed92fd7
Create Date: 2026-06-14 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "1b2c3d4e5f60"
down_revision = "88da1ed92fd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("residents") as batch:
        batch.add_column(sa.Column("phone", sa.String(length=40), nullable=True))
        batch.add_column(sa.Column("emergency_contact", sa.String(length=180), nullable=True))
        batch.add_column(sa.Column("household_info", sa.String(length=500), nullable=True))
        batch.add_column(sa.Column("vehicles", sa.String(length=500), nullable=True))
        batch.add_column(sa.Column("pets", sa.String(length=500), nullable=True))
        batch.add_column(sa.Column("notification_preference", sa.String(length=40), nullable=True))
        batch.add_column(sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("onboarding_metadata", sa.JSON(), nullable=True))

    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("condominium_id", sa.Integer(), nullable=False),
        sa.Column("unit_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location", sa.String(length=160), nullable=True),
        sa.Column("visibility", sa.String(length=40), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["condominium_id"], ["condominiums.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calendar_events_category"), "calendar_events", ["category"], unique=False)
    op.create_index(op.f("ix_calendar_events_condominium_id"), "calendar_events", ["condominium_id"], unique=False)
    op.create_index(op.f("ix_calendar_events_start_at"), "calendar_events", ["start_at"], unique=False)
    op.create_index(op.f("ix_calendar_events_unit_id"), "calendar_events", ["unit_id"], unique=False)
    op.create_index(op.f("ix_calendar_events_visibility"), "calendar_events", ["visibility"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_events_visibility"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_unit_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_start_at"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_condominium_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_category"), table_name="calendar_events")
    op.drop_table("calendar_events")

    with op.batch_alter_table("residents") as batch:
        batch.drop_column("onboarding_metadata")
        batch.drop_column("onboarding_completed")
        batch.drop_column("notification_preference")
        batch.drop_column("pets")
        batch.drop_column("vehicles")
        batch.drop_column("household_info")
        batch.drop_column("emergency_contact")
        batch.drop_column("phone")
