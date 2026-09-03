"""add idms_sales table

Revision ID: e7c7c0474609
Revises: b1da0cd3226f
Create Date: 2026-09-03 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7c7c0474609'
down_revision: Union[str, Sequence[str], None] = 'b1da0cd3226f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'idms_sales',
        sa.Column('report_year', sa.Integer(), nullable=False),
        sa.Column('acct_id', sa.String(length=50), nullable=False),
        sa.Column('acct_type', sa.String(length=100), nullable=True),
        sa.Column('borrower', sa.String(length=200), nullable=True),
        sa.Column('booked_date', sa.Date(), nullable=True),
        sa.Column('contract_date', sa.Date(), nullable=True),
        sa.Column('vin', sa.String(length=50), nullable=True),
        sa.Column('sales_price', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('cur_total_prin_bal_plus_tax', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('cash_down', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('deferred_down', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('trade_in_acv', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('trade_in_payoff', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('year_model', sa.String(length=20), nullable=True),
        sa.Column('make', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('inventory_cost', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('cost_with_pack_fee', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_expenses', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('orig_payments', sa.Integer(), nullable=True),
        sa.Column('orig_term_months', sa.Integer(), nullable=True),
        sa.Column('regz_apr', sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column('payment_frequency', sa.String(length=20), nullable=True),
        sa.Column('amount_financed', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('finance_charge', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_of_payments', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('reg_payment', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('monthly_payment', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('sales_location', sa.String(length=100), nullable=True),
        sa.Column('salesperson', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=20), nullable=True),
        sa.Column('zipcode', sa.String(length=20), nullable=True),
        sa.Column('referral', sa.String(length=100), nullable=True),
        sa.Column('gross_profit', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('inventory_type', sa.String(length=50), nullable=True),
        sa.Column('days_on_lot', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('acct_flags', sa.String(length=200), nullable=True),
        sa.Column('udf_text_value1', sa.String(length=50), nullable=True),
        sa.Column('branch_name', sa.String(length=100), nullable=True),
        sa.Column('branch_desc', sa.String(length=100), nullable=True),
        sa.Column('portfolio_name', sa.String(length=100), nullable=True),
        sa.Column('source_name', sa.String(length=100), nullable=True),
        sa.Column('lender_name', sa.String(length=100), nullable=True),
        sa.Column('imported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index('ix_idms_sales_year', 'idms_sales', ['report_year'], unique=False)
    op.create_index('ix_idms_sales_booked_date', 'idms_sales', ['booked_date'], unique=False)
    op.create_index('ix_idms_sales_acct', 'idms_sales', ['acct_id'], unique=False)
    op.create_index('ix_idms_sales_salesperson', 'idms_sales', ['salesperson'], unique=False)
    op.create_index('ix_idms_sales_make', 'idms_sales', ['make'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_idms_sales_make', table_name='idms_sales')
    op.drop_index('ix_idms_sales_salesperson', table_name='idms_sales')
    op.drop_index('ix_idms_sales_acct', table_name='idms_sales')
    op.drop_index('ix_idms_sales_booked_date', table_name='idms_sales')
    op.drop_index('ix_idms_sales_year', table_name='idms_sales')
    op.drop_table('idms_sales')
