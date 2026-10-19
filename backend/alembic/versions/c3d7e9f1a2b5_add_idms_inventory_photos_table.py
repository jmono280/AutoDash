"""add idms_inventory_photos table

Revision ID: c3d7e9f1a2b5
Revises: b8e4f6a2c1d9
Create Date: 2026-10-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d7e9f1a2b5'
down_revision: Union[str, Sequence[str], None] = 'b8e4f6a2c1d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'idms_inventory_photos',
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('inventory_id', sa.String(length=50), nullable=False),
        sa.Column('dealer_id', sa.String(length=50), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=300), nullable=False),
        sa.Column('image_url', sa.String(length=300), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index('ix_idms_inventory_photo_inventory_id', 'idms_inventory_photos', ['inventory_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_idms_inventory_photo_inventory_id', table_name='idms_inventory_photos')
    op.drop_table('idms_inventory_photos')
