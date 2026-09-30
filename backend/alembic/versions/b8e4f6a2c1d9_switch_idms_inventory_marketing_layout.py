"""switch idms_inventory to Marketing (wip) layout

Revision ID: b8e4f6a2c1d9
Revises: a7c2d9e1b4f3
Create Date: 2026-09-18 09:00:00.000000

IDMS layout for the native inventory lookup was switched from the account's
default queue layout to "Marketing (wip)" (icon Layout Settings,
QueueDataSourceId 20). It's a narrower, one-value-per-cell layout meant for
marketing/listing purposes: it drops cost/ops fields (Total Cost, Down,
Pics, GPS, Readiness Expire, Floorplan, Dup Key, Shop Audit, Inventory Type)
and adds Wholesale $. Since idms_inventory is a wiped-and-reloaded snapshot
(no history), the dropped columns carry no data worth preserving.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8e4f6a2c1d9'
down_revision: Union[str, Sequence[str], None] = 'a7c2d9e1b4f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index('ix_idms_inventory_type', table_name='idms_inventory')

    op.drop_column('idms_inventory', 'inventory_type')
    op.drop_column('idms_inventory', 'acquired_amount')
    op.drop_column('idms_inventory', 'total_expense')
    op.drop_column('idms_inventory', 'total_cost')
    op.drop_column('idms_inventory', 'down')
    op.drop_column('idms_inventory', 'pics_count')
    op.drop_column('idms_inventory', 'gps_device')
    op.drop_column('idms_inventory', 'gps_device_number')
    op.drop_column('idms_inventory', 'readiness_status')
    op.drop_column('idms_inventory', 'readiness_expire_year')
    op.drop_column('idms_inventory', 'readiness_expire_month')
    op.drop_column('idms_inventory', 'floorplan')
    op.drop_column('idms_inventory', 'dup_key_code')
    op.drop_column('idms_inventory', 'shop_audit')

    op.alter_column('idms_inventory', 'model', new_column_name='model_trim')
    op.alter_column('idms_inventory', 'status_detail', new_column_name='alternate_lot')

    op.add_column(
        'idms_inventory',
        sa.Column('wholesale_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('idms_inventory', 'wholesale_price')

    op.alter_column('idms_inventory', 'alternate_lot', new_column_name='status_detail')
    op.alter_column('idms_inventory', 'model_trim', new_column_name='model')

    op.add_column('idms_inventory', sa.Column('shop_audit', sa.String(length=60), nullable=True))
    op.add_column('idms_inventory', sa.Column('dup_key_code', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('idms_inventory', sa.Column('floorplan', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('idms_inventory', sa.Column('readiness_expire_month', sa.String(length=10), nullable=True))
    op.add_column('idms_inventory', sa.Column('readiness_expire_year', sa.String(length=10), nullable=True))
    op.add_column('idms_inventory', sa.Column('readiness_status', sa.String(length=60), nullable=True))
    op.add_column('idms_inventory', sa.Column('gps_device_number', sa.String(length=80), nullable=True))
    op.add_column('idms_inventory', sa.Column('gps_device', sa.String(length=80), nullable=True))
    op.add_column('idms_inventory', sa.Column('pics_count', sa.Integer(), nullable=True))
    op.add_column('idms_inventory', sa.Column('down', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('idms_inventory', sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('idms_inventory', sa.Column('total_expense', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('idms_inventory', sa.Column('acquired_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
    op.add_column('idms_inventory', sa.Column('inventory_type', sa.String(length=60), nullable=True))

    op.create_index('ix_idms_inventory_type', 'idms_inventory', ['inventory_type'], unique=False)
