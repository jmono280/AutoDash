"""add payment report tables

Revision ID: b4c5d6e7f8a9
Revises: a1b2c3d4e5f6
Create Date: 2026-05-25

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b4c5d6e7f8a9"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_start",        sa.Date(), nullable=False),
        sa.Column("period_end",          sa.Date(), nullable=False),
        sa.Column("payment_date",        sa.DateTime(timezone=True), nullable=False),
        sa.Column("account_id",          sa.Integer(), nullable=True),
        sa.Column("customer_name",       sa.String(200), nullable=False),
        sa.Column("payment_method",      sa.String(50), nullable=True),
        sa.Column("card_last_4",         sa.Integer(), nullable=True),
        sa.Column("amount",              sa.Numeric(10, 2), nullable=False),
        sa.Column("convenience_fee",     sa.Numeric(10, 2), nullable=False),
        sa.Column("status",              sa.String(50), nullable=True),
        sa.Column("reason_code",         sa.String(100), nullable=True),
        sa.Column("payment_origin",      sa.String(100), nullable=True),
        sa.Column("collector",           sa.String(150), nullable=True),
        sa.Column("reference_number",    sa.String(100), nullable=True),
        sa.Column("notes",               sa.Text(), nullable=True),
        sa.Column("refund_amount",       sa.Numeric(10, 2), nullable=True),
        sa.Column("refund_date",         sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_initiated_by", sa.String(200), nullable=True),
        sa.Column("imported_at",         sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index("ix_payment_tx_period",    "payment_transactions", ["period_start", "period_end"])
    op.create_index("ix_payment_tx_collector", "payment_transactions", ["collector"])

    op.create_table(
        "collection_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at",          sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at",          sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at",          sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_start",        sa.Date(), nullable=False),
        sa.Column("period_end",          sa.Date(), nullable=False),
        sa.Column("collector",           sa.String(150), nullable=False),
        sa.Column("payments_count",      sa.Integer(), nullable=False),
        sa.Column("payments_amount",     sa.Numeric(10, 2), nullable=False),
        sa.Column("autopay_created",     sa.Integer(), nullable=False),
        sa.Column("promise_sent",        sa.Integer(), nullable=False),
        sa.Column("promise_confirmed",   sa.Integer(), nullable=False),
        sa.Column("messages_sent",       sa.Integer(), nullable=False),
        sa.Column("notes_count",         sa.Integer(), nullable=False),
        sa.Column("waived_fees_count",   sa.Integer(), nullable=False),
        sa.Column("waived_fees_amount",  sa.Numeric(10, 2), nullable=False),
        sa.Column("worked",              sa.Integer(), nullable=False),
        sa.Column("imported_at",         sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index("ix_collection_stat_period", "collection_stats", ["period_start", "period_end"])


def downgrade() -> None:
    op.drop_index("ix_collection_stat_period", table_name="collection_stats")
    op.drop_table("collection_stats")
    op.drop_index("ix_payment_tx_collector", table_name="payment_transactions")
    op.drop_index("ix_payment_tx_period",    table_name="payment_transactions")
    op.drop_table("payment_transactions")
