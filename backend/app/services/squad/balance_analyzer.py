"""
SuperScout Backend — Squad Balance Analyzer Module

Calculates deterministic 17-dimension Squad Balance Score (0-100) and produces
human-readable tactical Strengths & Weaknesses audit reports.
"""
from typing import Dict, List, Tuple
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.squad.role_classifier import RoleClassifier
from app.services.squad.schemas import (
    BalanceSubScore,
    PhaseCoverageSummary,
    RoleDistributionSummary,
    SquadBalanceResponse,
)


class SquadBalanceAnalyzer:
    """Analyzer for evaluating squad role coverage, depth, phase resources, and overall balance score."""

    @classmethod
    def analyze_squad(
        cls,
        team_id: int,
        team_name: str,
        players: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
    ) -> SquadBalanceResponse:
        squad_size = len(players)

        # 1. Compute Role Distribution Summary
        batters_cnt = 0
        bowlers_cnt = 0
        all_rounders_cnt = 0
        keepers_cnt = 0
        pace_cnt = 0
        spin_cnt = 0

        for p in players:
            if RoleClassifier.is_wicketkeeper(p):
                keepers_cnt += 1
            if RoleClassifier.is_all_rounder(p):
                all_rounders_cnt += 1
            elif p.role in ("batter", "wicketkeeper_batter", "wicketkeeper"):
                batters_cnt += 1
            elif p.role in ("bowler", "fast_bowler", "spinner", "medium_fast_bowler", "bowling_all_rounder"):
                bowlers_cnt += 1

            if RoleClassifier.is_pace_bowler(p):
                pace_cnt += 1
            if RoleClassifier.is_spin_bowler(p):
                spin_cnt += 1

        role_dist = RoleDistributionSummary(
            total_squad_size=squad_size,
            batters_count=batters_cnt,
            bowlers_count=bowlers_cnt,
            all_rounders_count=all_rounders_cnt,
            wicketkeepers_count=keepers_cnt,
            pace_bowlers_count=pace_cnt,
            spin_bowlers_count=spin_cnt,
        )

        # 2. Compute Phase Coverage Summary
        pp_bowlers = 0
        mid_bowlers = 0
        death_bowlers = 0
        finishers = 0

        for p in players:
            a = analytics_map.get(p.id)
            if RoleClassifier.is_powerplay_bowler(a):
                pp_bowlers += 1
            if a and (a.bowling.phases.middle.overs or 0.0) >= 1.0:
                mid_bowlers += 1
            if RoleClassifier.is_death_bowler(a):
                death_bowlers += 1
            if RoleClassifier.is_finisher(a):
                finishers += 1

        phase_cov = PhaseCoverageSummary(
            powerplay_batters_count=max(2, batters_cnt // 2),
            middle_batters_count=max(2, batters_cnt // 2),
            finishers_count=finishers,
            powerplay_bowlers_count=pp_bowlers,
            middle_bowlers_count=mid_bowlers,
            death_bowlers_count=death_bowlers,
        )

        # 3. Sub-Scores Calculation (0-100 scale)
        # Role Coverage Score
        req_keeper = 100.0 if keepers_cnt >= 1 else 0.0
        req_bowler = min(100.0, (bowlers_cnt + all_rounders_cnt) / 5.0 * 100.0)
        req_batter = min(100.0, (batters_cnt + all_rounders_cnt) / 5.0 * 100.0)
        role_cov_score = round(0.40 * req_keeper + 0.30 * req_bowler + 0.30 * req_batter, 1)

        # Depth Score
        capable_batters = sum(1 for p in players if RoleClassifier.is_capable_batter(p, analytics_map.get(p.id)))
        capable_bowlers = sum(1 for p in players if RoleClassifier.is_capable_bowler(p, analytics_map.get(p.id)))
        bat_depth_score = min(100.0, (capable_batters / 7.0) * 100.0)
        bowl_depth_score = min(100.0, (capable_bowlers / 5.0) * 100.0)
        squad_size_score = min(100.0, (squad_size / 15.0) * 100.0)
        depth_score = round(0.40 * bat_depth_score + 0.40 * bowl_depth_score + 0.20 * squad_size_score, 1)

        # Phase Balance Score
        pp_score = min(100.0, (pp_bowlers / 2.0) * 100.0) if pp_bowlers > 0 else 50.0
        death_score = min(100.0, (death_bowlers / 2.0) * 100.0) if death_bowlers > 0 else 40.0
        fin_score = min(100.0, (finishers / 2.0) * 100.0) if finishers > 0 else 50.0
        phase_score = round(0.35 * death_score + 0.35 * pp_score + 0.30 * fin_score, 1)

        # Specialist Cover Score
        keeper_cover = 100.0 if keepers_cnt >= 2 else (70.0 if keepers_cnt == 1 else 0.0)
        pace_spin_var = 100.0 if (pace_cnt >= 2 and spin_cnt >= 1) else (60.0 if (pace_cnt >= 1 or spin_cnt >= 1) else 20.0)
        specialist_score = round(0.50 * keeper_cover + 0.50 * pace_spin_var, 1)

        # Versatility Score
        all_rounder_score = min(100.0, (all_rounders_cnt / 3.0) * 100.0)
        versatility_score = round(all_rounder_score, 1)

        # Overall Squad Balance Score
        w_role, w_depth, w_phase, w_spec, w_vers = 0.25, 0.20, 0.20, 0.20, 0.15
        overall_score = round(
            (role_cov_score * w_role)
            + (depth_score * w_depth)
            + (phase_score * w_phase)
            + (specialist_score * w_spec)
            + (versatility_score * w_vers),
            1,
        )

        # 4. Generate Strengths & Weaknesses
        strengths: List[str] = []
        weaknesses: List[str] = []

        if keepers_cnt >= 2:
            strengths.append("Strong wicketkeeping depth with primary and backup options.")
        elif keepers_cnt == 1:
            weaknesses.append("Only one specialist wicketkeeper; no backup keeper available.")
        else:
            weaknesses.append("CRITICAL: No specialist wicketkeeper in squad!")

        if death_bowlers >= 2:
            strengths.append("Multiple death-bowling options provide late-overs security.")
        elif death_bowlers == 1:
            weaknesses.append("Heavy dependence on a single death bowler.")
        else:
            weaknesses.append("Weak death-bowling resources; vulnerable in closing overs.")

        if all_rounders_cnt >= 3:
            strengths.append("Exceptional all-rounder depth provides immense tactical flexibility.")
        elif all_rounders_cnt == 0:
            weaknesses.append("Lack of genuine all-rounders reduces tactical balance.")

        if capable_batters >= 8:
            strengths.append("Deep batting lineup extending through the lower-middle order.")

        if pace_cnt >= 2 and spin_cnt >= 2:
            strengths.append("Well-balanced pace and spin variety for different pitch conditions.")
        elif pace_cnt == 0:
            weaknesses.append("No pace bowlers in squad!")
        elif spin_cnt == 0:
            weaknesses.append("No spin bowlers in squad!")

        return SquadBalanceResponse(
            team_id=team_id,
            team_name=team_name,
            squad_size=squad_size,
            overall_balance_score=overall_score,
            role_coverage_score=BalanceSubScore(score=role_cov_score, weight=w_role, weighted_score=round(role_cov_score * w_role, 2), description="Presence of keepers, batters & bowlers"),
            depth_score=BalanceSubScore(score=depth_score, weight=w_depth, weighted_score=round(depth_score * w_depth, 2), description="Batting & bowling squad depth"),
            phase_balance_score=BalanceSubScore(score=phase_score, weight=w_phase, weighted_score=round(phase_score * w_phase, 2), description="Powerplay & Death overs coverage"),
            specialist_cover_score=BalanceSubScore(score=specialist_score, weight=w_spec, weighted_score=round(specialist_score * w_spec, 2), description="Backup keeper & Pace/Spin variety"),
            versatility_score=BalanceSubScore(score=versatility_score, weight=w_vers, weighted_score=round(versatility_score * w_vers, 2), description="All-rounder flexibility"),
            role_distribution=role_dist,
            phase_coverage=phase_cov,
            strengths=strengths,
            weaknesses=weaknesses,
        )
