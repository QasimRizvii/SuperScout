"""Phase 2 Cricket Data Foundation Initial Migration

Revision ID: 001_phase2_foundation
Revises: 
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_phase2_foundation'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Players
    op.create_table(
        'players',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('short_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.Enum('batter', 'wicketkeeper', 'all_rounder', 'bowler', name='playerrole', native_enum=False), nullable=False),
        sa.Column('batting_style', sa.String(length=100), nullable=True),
        sa.Column('bowling_style', sa.String(length=100), nullable=True),
        sa.Column('nationality', sa.String(length=100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_players_name', 'players', ['name'])
    op.create_index('ix_players_role', 'players', ['role'])
    op.create_index('ix_players_nationality', 'players', ['nationality'])

    # Teams
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('short_name', sa.String(length=100), nullable=True),
        sa.Column('abbreviation', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teams_name', 'teams', ['name'])
    op.create_index('ix_teams_abbreviation', 'teams', ['abbreviation'])

    # Venues
    op.create_table(
        'venues',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('pitch_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_venues_name', 'venues', ['name'])
    op.create_index('ix_venues_city', 'venues', ['city'])

    # Matches
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('season', sa.String(length=50), nullable=False),
        sa.Column('match_date', sa.Date(), nullable=False),
        sa.Column('match_type', sa.Enum('T20', 'ODI', 'Test', 'T10', 'Other', name='matchtype', native_enum=False), nullable=False),
        sa.Column('venue_id', sa.Integer(), nullable=False),
        sa.Column('team_1_id', sa.Integer(), nullable=False),
        sa.Column('team_2_id', sa.Integer(), nullable=False),
        sa.Column('winner_team_id', sa.Integer(), nullable=True),
        sa.Column('result_description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id']),
        sa.ForeignKeyConstraint(['team_1_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['team_2_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['winner_team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    op.create_index('ix_matches_season', 'matches', ['season'])
    op.create_index('ix_matches_match_date', 'matches', ['match_date'])

    # Innings
    op.create_table(
        'innings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('innings_number', sa.Integer(), nullable=False),
        sa.Column('batting_team_id', sa.Integer(), nullable=False),
        sa.Column('bowling_team_id', sa.Integer(), nullable=False),
        sa.Column('total_runs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wickets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('overs', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['batting_team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['bowling_team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id', 'innings_number', name='uq_match_innings_number')
    )

    # Batting Performances
    op.create_table(
        'batting_performances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('innings_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('batting_position', sa.Integer(), nullable=True),
        sa.Column('runs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('balls_faced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fours', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sixes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('strike_rate', sa.Float(), nullable=True),
        sa.Column('dismissal_type', sa.String(length=50), nullable=True),
        sa.Column('dismissed_by_player_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['innings_id'], ['innings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['dismissed_by_player_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Bowling Performances
    op.create_table(
        'bowling_performances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('innings_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('overs', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('balls_bowled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('maidens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('runs_conceded', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wickets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wides', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('no_balls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('economy', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['innings_id'], ['innings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Player Matchups
    op.create_table(
        'player_matchups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batter_id', sa.Integer(), nullable=False),
        sa.Column('bowler_id', sa.Integer(), nullable=False),
        sa.Column('matches', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('balls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('runs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dismissals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fours', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sixes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('strike_rate', sa.Float(), nullable=True),
        sa.Column('average', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['batter_id'], ['players.id']),
        sa.ForeignKeyConstraint(['bowler_id'], ['players.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batter_id', 'bowler_id', name='uq_batter_bowler_matchup')
    )

    # Auctions
    op.create_table(
        'auctions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('season', sa.String(length=50), nullable=False),
        sa.Column('auction_name', sa.String(length=150), nullable=False),
        sa.Column('auction_date', sa.Date(), nullable=True),
        sa.Column('auction_type', sa.Enum('mega', 'mini', 'other', name='auctiontype', native_enum=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_auctions_season', 'auctions', ['season'])
    op.create_index('ix_auctions_auction_type', 'auctions', ['auction_type'])

    # Auction Transactions
    op.create_table(
        'auction_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('auction_id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('base_price', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('final_price', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.Enum('sold', 'unsold', 'retained', 'other', name='auctionstatus', native_enum=False), nullable=False),
        sa.Column('purse_before', sa.Float(), nullable=True),
        sa.Column('purse_after', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_auction_transactions_status', 'auction_transactions', ['status'])


def downgrade() -> None:
    op.drop_table('auction_transactions')
    op.drop_table('auctions')
    op.drop_table('player_matchups')
    op.drop_table('bowling_performances')
    op.drop_table('batting_performances')
    op.drop_table('innings')
    op.drop_table('matches')
    op.drop_table('venues')
    op.drop_table('teams')
    op.drop_table('players')
