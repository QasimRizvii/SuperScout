"""Create data_provenance_logs table

Revision ID: 005_add_data_provenance_tables
Revises: 004_create_scouting_tables
Create Date: 2026-09-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005_add_data_provenance_tables'
down_revision: Union[str, None] = '004_create_scouting_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'data_provenance_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_id', sa.String(length=100), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='csv'),
        sa.Column('source_url', sa.String(length=255), nullable=True),
        sa.Column('dataset_version', sa.String(length=50), nullable=True, server_default='1.0'),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('imported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_provenance_logs_batch_id'), 'data_provenance_logs', ['batch_id'], unique=False)
    op.create_index(op.f('ix_data_provenance_logs_source_name'), 'data_provenance_logs', ['source_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_data_provenance_logs_source_name'), table_name='data_provenance_logs')
    op.drop_index(op.f('ix_data_provenance_logs_batch_id'), table_name='data_provenance_logs')
    op.drop_table('data_provenance_logs')
