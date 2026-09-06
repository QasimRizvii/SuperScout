"""Expand players role column length to VARCHAR(50)

Revision ID: 003_expand_player_role
Revises: 002_phase2_enhancements
Create Date: 2026-09-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_expand_player_role'
down_revision: Union[str, None] = '002_phase2_enhancements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'players',
        'role',
        existing_type=sa.String(length=12),
        type_=sa.String(length=50),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'players',
        'role',
        existing_type=sa.String(length=50),
        type_=sa.String(length=12),
        existing_nullable=False,
    )
