"""add idms_inventory table

Revision ID: f1a2b3c4d5e6
Revises: e7c7c0474609
Create Date: 2026-09-07 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'e7c7c0474609'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'idms_inventory',
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('inventory_id', sa.String(length=50), nullable=True),
        sa.Column('dealer_id', sa.String(length=50), nullable=True),
        sa.Column('stock_number', sa.String(length=50), nullable=True),
        sa.Column('vehicle_year', sa.String(length=10), nullable=True),
        sa.Column('vin_last6', sa.String(length=20), nullable=True),
        sa.Column('make', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('exterior_color', sa.String(length=60), nullable=True),
        sa.Column('inventory_type', sa.String(length=60), nullable=True),
        sa.Column('acq_date', sa.Date(), nullable=True),
        sa.Column('dol', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=60), nullable=True),
        sa.Column('status_detail', sa.String(length=80), nullable=True),
        sa.Column('acquired_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_expense', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('down', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('pics_count', sa.Integer(), nullable=True),
        sa.Column('gps_device', sa.String(length=80), nullable=True),
        sa.Column('gps_device_number', sa.String(length=80), nullable=True),
        sa.Column('readiness_status', sa.String(length=60), nullable=True),
        sa.Column('readiness_expire_year', sa.String(length=10), nullable=True),
        sa.Column('readiness_expire_month', sa.String(length=10), nullable=True),
        sa.Column('floorplan', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('dup_key_code', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('shop_audit', sa.String(length=60), nullable=True),
        sa.Column('imported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index('ix_idms_inventory_snapshot', 'idms_inventory', ['snapshot_date'], unique=False)
    op.create_index('ix_idms_inventory_inventory_id', 'idms_inventory', ['inventory_id'], unique=False)
    op.create_index('ix_idms_inventory_type', 'idms_inventory', ['inventory_type'], unique=False)
    op.create_index('ix_idms_inventory_make', 'idms_inventory', ['make'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_idms_inventory_make', table_name='idms_inventory')
    op.drop_index('ix_idms_inventory_type', table_name='idms_inventory')
    op.drop_index('ix_idms_inventory_inventory_id', table_name='idms_inventory')
    op.drop_index('ix_idms_inventory_snapshot', table_name='idms_inventory')
    op.drop_table('idms_inventory')
