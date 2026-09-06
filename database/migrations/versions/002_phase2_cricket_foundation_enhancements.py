"""Phase 2 Cricket Foundation Schema Enhancements

Revision ID: 002_phase2_enhancements
Revises: 001_phase2_foundation
Create Date: 2026-09-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_phase2_enhancements'
down_revision: Union[str, None] = '001_phase2_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Players Enhancements ─────────────────────────────────────────────
    op.add_column('players', sa.Column('is_wicketkeeper', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('players', sa.Column('profile_image_url', sa.String(length=255), nullable=True))
    op.create_index('ix_players_is_active', 'players', ['is_active'])

    # ── 2. Teams Enhancements ───────────────────────────────────────────────
    op.add_column('teams', sa.Column('country', sa.String(length=100), nullable=True))
    op.add_column('teams', sa.Column('team_type', sa.String(length=50), server_default='franchise', nullable=False))
    op.add_column('teams', sa.Column('logo_url', sa.String(length=255), nullable=True))
    op.create_index('ix_teams_country', 'teams', ['country'])
    op.create_index('ix_teams_team_type', 'teams', ['team_type'])
    op.create_index('ix_teams_is_active', 'teams', ['is_active'])

    # ── 3. Venues Enhancements ──────────────────────────────────────────────
    op.add_column('venues', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('venues', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('venues', sa.Column('timezone', sa.String(length=50), nullable=True))
    op.create_index('ix_venues_country', 'venues', ['country'])
    op.create_check_constraint('chk_venue_capacity_non_negative', 'venues', 'capacity IS NULL OR capacity >= 0')

    # ── 4. Matches Enhancements ─────────────────────────────────────────────
    op.add_column('matches', sa.Column('competition', sa.String(length=100), nullable=True))
    op.add_column('matches', sa.Column('status', sa.String(length=50), server_default='completed', nullable=False))
    op.add_column('matches', sa.Column('toss_winner_id', sa.Integer(), nullable=True))
    op.add_column('matches', sa.Column('toss_decision', sa.String(length=20), nullable=True))
    op.create_foreign_key('fk_matches_toss_winner_id', 'matches', 'teams', ['toss_winner_id'], ['id'])
    op.create_index('ix_matches_competition', 'matches', ['competition'])
    op.create_index('ix_matches_status', 'matches', ['status'])
    op.create_index('ix_matches_match_type', 'matches', ['match_type'])

    # ── 5. Innings Enhancements ─────────────────────────────────────────────
    op.add_column('innings', sa.Column('run_rate', sa.Float(), nullable=True))
    op.add_column('innings', sa.Column('extras', sa.Integer(), server_default='0', nullable=False))
    op.add_column('innings', sa.Column('powerplay_runs', sa.Integer(), nullable=True))
    op.create_check_constraint('chk_innings_total_runs_non_negative', 'innings', 'total_runs >= 0')
    op.create_check_constraint('chk_innings_wickets_valid', 'innings', 'wickets >= 0 AND wickets <= 10')
    op.create_check_constraint('chk_innings_overs_non_negative', 'innings', 'overs >= 0.0')
    op.create_check_constraint('chk_innings_extras_non_negative', 'innings', 'extras >= 0')

    # ── 6. Batting Performances Enhancements ────────────────────────────────
    op.add_column('batting_performances', sa.Column('dot_balls', sa.Integer(), server_default='0', nullable=False))
    op.add_column('batting_performances', sa.Column('runs_powerplay', sa.Integer(), nullable=True))
    op.add_column('batting_performances', sa.Column('runs_middle', sa.Integer(), nullable=True))
    op.add_column('batting_performances', sa.Column('runs_death', sa.Integer(), nullable=True))
    op.add_column('batting_performances', sa.Column('fielder_player_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_batting_fielder_player_id', 'batting_performances', 'players', ['fielder_player_id'], ['id'])
    op.create_check_constraint('chk_batting_runs_non_negative', 'batting_performances', 'runs >= 0')
    op.create_check_constraint('chk_batting_balls_non_negative', 'batting_performances', 'balls_faced >= 0')
    op.create_check_constraint('chk_batting_fours_non_negative', 'batting_performances', 'fours >= 0')
    op.create_check_constraint('chk_batting_sixes_non_negative', 'batting_performances', 'sixes >= 0')
    op.create_check_constraint('chk_batting_dot_balls_non_negative', 'batting_performances', 'dot_balls >= 0')

    # ── 7. Bowling Performances Enhancements ────────────────────────────────
    op.add_column('bowling_performances', sa.Column('bowling_position', sa.Integer(), nullable=True))
    op.add_column('bowling_performances', sa.Column('dot_balls', sa.Integer(), server_default='0', nullable=False))
    op.add_column('bowling_performances', sa.Column('overs_powerplay', sa.Float(), nullable=True))
    op.add_column('bowling_performances', sa.Column('overs_middle', sa.Float(), nullable=True))
    op.add_column('bowling_performances', sa.Column('overs_death', sa.Float(), nullable=True))
    op.create_check_constraint('chk_bowling_runs_non_negative', 'bowling_performances', 'runs_conceded >= 0')
    op.create_check_constraint('chk_bowling_balls_non_negative', 'bowling_performances', 'balls_bowled >= 0')
    op.create_check_constraint('chk_bowling_wickets_non_negative', 'bowling_performances', 'wickets >= 0')
    op.create_check_constraint('chk_bowling_maidens_non_negative', 'bowling_performances', 'maidens >= 0')
    op.create_check_constraint('chk_bowling_wides_non_negative', 'bowling_performances', 'wides >= 0')
    op.create_check_constraint('chk_bowling_no_balls_non_negative', 'bowling_performances', 'no_balls >= 0')
    op.create_check_constraint('chk_bowling_dot_balls_non_negative', 'bowling_performances', 'dot_balls >= 0')

    # ── 8. Player Matchups Enhancements ─────────────────────────────────────
    op.add_column('player_matchups', sa.Column('dot_balls', sa.Integer(), server_default='0', nullable=False))
    op.add_column('player_matchups', sa.Column('boundary_percentage', sa.Float(), nullable=True))
    op.create_check_constraint('chk_matchup_balls_non_negative', 'player_matchups', 'balls >= 0')
    op.create_check_constraint('chk_matchup_runs_non_negative', 'player_matchups', 'runs >= 0')
    op.create_check_constraint('chk_matchup_dismissals_non_negative', 'player_matchups', 'dismissals >= 0')
    op.create_check_constraint('chk_matchup_fours_non_negative', 'player_matchups', 'fours >= 0')
    op.create_check_constraint('chk_matchup_sixes_non_negative', 'player_matchups', 'sixes >= 0')
    op.create_check_constraint('chk_matchup_dot_balls_non_negative', 'player_matchups', 'dot_balls >= 0')


def downgrade() -> None:
    # Matchups
    op.drop_constraint('chk_matchup_dot_balls_non_negative', 'player_matchups', type_='check')
    op.drop_constraint('chk_matchup_sixes_non_negative', 'player_matchups', type_='check')
    op.drop_constraint('chk_matchup_fours_non_negative', 'player_matchups', type_='check')
    op.drop_constraint('chk_matchup_dismissals_non_negative', 'player_matchups', type_='check')
    op.drop_constraint('chk_matchup_runs_non_negative', 'player_matchups', type_='check')
    op.drop_constraint('chk_matchup_balls_non_negative', 'player_matchups', type_='check')
    op.drop_column('player_matchups', 'boundary_percentage')
    op.drop_column('player_matchups', 'dot_balls')

    # Bowling
    op.drop_constraint('chk_bowling_dot_balls_non_negative', 'bowling_performances', type_='check')
    op.drop_constraint('chk_bowling_no_balls_non_negative', 'bowling_performances', type_='check')
    op.drop_constraint('chk_bowling_wides_non_negative', 'bowling_performances', type_='check')
    op.drop_constraint('chk_bowling_maidens_non_negative', 'bowling_performances', type_='check')
    op.drop_constraint('chk_bowling_wickets_non_negative', 'bowling_performances', type_='check')
    op.drop_constraint('chk_bowling_balls_non_negative', 'bowling_performances', type_='check')
    op.drop_constraint('chk_bowling_runs_non_negative', 'bowling_performances', type_='check')
    op.drop_column('bowling_performances', 'overs_death')
    op.drop_column('bowling_performances', 'overs_middle')
    op.drop_column('bowling_performances', 'overs_powerplay')
    op.drop_column('bowling_performances', 'dot_balls')
    op.drop_column('bowling_performances', 'bowling_position')

    # Batting
    op.drop_constraint('chk_batting_dot_balls_non_negative', 'batting_performances', type_='check')
    op.drop_constraint('chk_batting_sixes_non_negative', 'batting_performances', type_='check')
    op.drop_constraint('chk_batting_fours_non_negative', 'batting_performances', type_='check')
    op.drop_constraint('chk_batting_balls_non_negative', 'batting_performances', type_='check')
    op.drop_constraint('chk_batting_runs_non_negative', 'batting_performances', type_='check')
    op.drop_constraint('fk_batting_fielder_player_id', 'batting_performances', type_='foreignkey')
    op.drop_column('batting_performances', 'fielder_player_id')
    op.drop_column('batting_performances', 'runs_death')
    op.drop_column('batting_performances', 'runs_middle')
    op.drop_column('batting_performances', 'runs_powerplay')
    op.drop_column('batting_performances', 'dot_balls')

    # Innings
    op.drop_constraint('chk_innings_extras_non_negative', 'innings', type_='check')
    op.drop_constraint('chk_innings_overs_non_negative', 'innings', type_='check')
    op.drop_constraint('chk_innings_wickets_valid', 'innings', type_='check')
    op.drop_constraint('chk_innings_total_runs_non_negative', 'innings', type_='check')
    op.drop_column('innings', 'powerplay_runs')
    op.drop_column('innings', 'extras')
    op.drop_column('innings', 'run_rate')

    # Matches
    op.drop_index('ix_matches_match_type', table_name='matches')
    op.drop_index('ix_matches_status', table_name='matches')
    op.drop_index('ix_matches_competition', table_name='matches')
    op.drop_constraint('fk_matches_toss_winner_id', 'matches', type_='foreignkey')
    op.drop_column('matches', 'toss_decision')
    op.drop_column('matches', 'toss_winner_id')
    op.drop_column('matches', 'status')
    op.drop_column('matches', 'competition')

    # Venues
    op.drop_constraint('chk_venue_capacity_non_negative', 'venues', type_='check')
    op.drop_index('ix_venues_country', table_name='venues')
    op.drop_column('venues', 'timezone')
    op.drop_column('venues', 'longitude')
    op.drop_column('venues', 'latitude')

    # Teams
    op.drop_index('ix_teams_is_active', table_name='teams')
    op.drop_index('ix_teams_team_type', table_name='teams')
    op.drop_index('ix_teams_country', table_name='teams')
    op.drop_column('teams', 'logo_url')
    op.drop_column('teams', 'team_type')
    op.drop_column('teams', 'country')

    # Players
    op.drop_index('ix_players_is_active', table_name='players')
    op.drop_column('players', 'profile_image_url')
    op.drop_column('players', 'is_wicketkeeper')
