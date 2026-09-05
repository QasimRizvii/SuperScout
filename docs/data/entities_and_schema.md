# SuperScout Database Entities & Schema Reference

## Core Entities

### 1. `players`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `name`, `short_name`, `role` (batter, wicketkeeper, all_rounder, bowler), `batting_style`, `bowling_style`, `nationality`, `date_of_birth`, `is_active`, `created_at`, `updated_at`.
- **Indexes**: `name`, `role`, `nationality`.

### 2. `teams`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `name`, `short_name`, `abbreviation`, `city`, `is_active`, `created_at`, `updated_at`.
- **Indexes**: `name`, `abbreviation`.

### 3. `venues`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `name`, `city`, `country`, `capacity` (nullable), `pitch_type` (nullable), `created_at`, `updated_at`.
- **Indexes**: `name`, `city`.

### 4. `matches`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `external_id` (UNIQUE), `season`, `match_date`, `match_type` (T20, ODI, Test, T10, Other), `venue_id`, `team_1_id`, `team_2_id`, `winner_team_id` (nullable), `result_description`, `created_at`, `updated_at`.
- **Indexes**: `season`, `match_date`, `venue_id`, `team_1_id`, `team_2_id`.

### 5. `innings`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `match_id`, `innings_number`, `batting_team_id`, `bowling_team_id`, `total_runs`, `wickets`, `overs`, `created_at`.
- **Constraints**: Unique constraint on `(match_id, innings_number)`.

### 6. `batting_performances`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `match_id`, `innings_id`, `player_id`, `team_id`, `batting_position`, `runs`, `balls_faced`, `fours`, `sixes`, `strike_rate`, `dismissal_type`, `dismissed_by_player_id`, `created_at`.
- **Derived Field**: `strike_rate` = `(runs / balls_faced * 100)` when `balls_faced > 0` else `0.0`.

### 7. `bowling_performances`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `match_id`, `innings_id`, `player_id`, `team_id`, `overs`, `balls_bowled`, `maidens`, `runs_conceded`, `wickets`, `wides`, `no_balls`, `economy`, `created_at`.
- **Derived Field**: `economy` = `(runs_conceded / (balls_bowled / 6.0))` when `balls_bowled > 0` else `0.0`.

### 8. `player_matchups`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `batter_id`, `bowler_id`, `matches`, `balls`, `runs`, `dismissals`, `fours`, `sixes`, `strike_rate`, `average`, `created_at`, `updated_at`.
- **Constraints**: Unique constraint on `(batter_id, bowler_id)`.

### 9. `auctions`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `season`, `auction_name`, `auction_date`, `auction_type` (mega, mini, other), `created_at`.
- **Indexes**: `season`, `auction_type`.

### 10. `auction_transactions`
- **Primary Key**: `id` (INTEGER)
- **Attributes**: `auction_id`, `player_id`, `team_id` (nullable), `base_price`, `final_price`, `status` (sold, unsold, retained, other), `purse_before`, `purse_after`, `created_at`.
- **Indexes**: `status`, `auction_id`, `player_id`.
