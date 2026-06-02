"""add_call_analytics

Revision ID: a1b2c3d4e5f6
Revises: b3125e7d2623
Create Date: 2026-05-22 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "b3125e7d2623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "call_analytics",
        sa.Column("time_from",        sa.DateTime(timezone=True), nullable=False),
        sa.Column("time_to",          sa.DateTime(timezone=True), nullable=False),
        sa.Column("extension_number", sa.String(length=20),       nullable=False),
        sa.Column("extension_name",   sa.String(length=150),      nullable=False),
        sa.Column("total_calls",      sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inbound",          sa.Integer(), nullable=False, server_default="0"),
        sa.Column("outbound",         sa.Integer(), nullable=False, server_default="0"),
        sa.Column("direct",           sa.Integer(), nullable=False, server_default="0"),
        sa.Column("from_queue",       sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transferred",      sa.Integer(), nullable=False, server_default="0"),
        sa.Column("portal_equiv",     sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("external",         sa.Integer(), nullable=False, server_default="0"),
        sa.Column("internal",         sa.Integer(), nullable=False, server_default="0"),
        sa.Column("answered",         sa.Integer(), nullable=False, server_default="0"),
        sa.Column("not_answered",     sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed",        sa.Integer(), nullable=False, server_default="0"),
        sa.Column("abandoned",        sa.Integer(), nullable=False, server_default="0"),
        sa.Column("voicemail",        sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id",         sa.UUID(),                     nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),    nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True),    nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True),    nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index("ix_call_analytics_time_from",        "call_analytics", ["time_from"],                          unique=False)
    op.create_index("ix_call_analytics_extension_number", "call_analytics", ["extension_number"],                   unique=False)
    op.create_index("ix_call_analytics_range_ext",        "call_analytics", ["time_from", "time_to", "extension_number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_call_analytics_range_ext",        table_name="call_analytics")
    op.drop_index("ix_call_analytics_extension_number", table_name="call_analytics")
    op.drop_index("ix_call_analytics_time_from",        table_name="call_analytics")
    op.drop_table("call_analytics")
