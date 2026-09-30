"""add inventory_flags to idms_inventory

Revision ID: a7c2d9e1b4f3
Revises: f1a2b3c4d5e6
Create Date: 2026-09-17 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7c2d9e1b4f3'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'idms_inventory',
        sa.Column('inventory_flags', sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('idms_inventory', 'inventory_flags')
