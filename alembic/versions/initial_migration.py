"""Initial migration

Revision ID: initial
Create Date: 2025-03-28 18:28:16.886933+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cryptocurrencies table
    op.create_table(
        'cryptocurrencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coingecko_id', sa.String(length=100), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('total_volume', sa.Float(), nullable=True),
        sa.Column('price_change_24h', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes
    op.create_index(op.f('ix_cryptocurrencies_id'), 'cryptocurrencies', ['id'], unique=False)


def downgrade() -> None:
    # Drop cryptocurrencies table
    op.drop_index(op.f('ix_cryptocurrencies_id'), table_name='cryptocurrencies')
    op.drop_table('cryptocurrencies') 