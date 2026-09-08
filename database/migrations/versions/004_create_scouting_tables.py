"""Create scouting_watchlists and scouting_notes tables

Revision ID: 004_create_scouting_tables
Revises: 003_expand_player_role
Create Date: 2026-09-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_create_scouting_tables'
down_revision: Union[str, None] = '003_expand_player_role'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create scouting_watchlists table
    op.create_table(
        'scouting_watchlists',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='NEW'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scouting_watchlists_player_id'), 'scouting_watchlists', ['player_id'], unique=False)
    op.create_index(op.f('ix_scouting_watchlists_priority'), 'scouting_watchlists', ['priority'], unique=False)
    op.create_index(op.f('ix_scouting_watchlists_status'), 'scouting_watchlists', ['status'], unique=False)

    # Create scouting_notes table
    op.create_table(
        'scouting_notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=30), nullable=False, server_default='GENERAL'),
        sa.Column('observation', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scouting_notes_player_id'), 'scouting_notes', ['player_id'], unique=False)
    op.create_index(op.f('ix_scouting_notes_category'), 'scouting_notes', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scouting_notes_category'), table_name='scouting_notes')
    op.drop_index(op.f('ix_scouting_notes_player_id'), table_name='scouting_notes')
    op.drop_table('scouting_notes')

    op.drop_index(op.f('ix_scouting_watchlists_status'), table_name='scouting_watchlists')
    op.drop_index(op.f('ix_scouting_watchlists_priority'), table_name='scouting_watchlists')
    op.drop_index(op.f('ix_scouting_watchlists_player_id'), table_name='scouting_watchlists')
    op.drop_table('scouting_watchlists')
