"""
SuperScout Backend — Squad Scenario Analyzer Module

Simulates player unavailability/injury scenarios and evaluates balance impact & bench replacements.
"""
from typing import Dict, List, Set
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.squad.balance_analyzer import SquadBalanceAnalyzer
from app.services.squad.role_classifier import RoleClassifier
from app.services.squad.schemas import (
    InternalReplacementOption,
    ScenarioAnalysisResponse,
)


class ScenarioAnalyzer:
    """Simulates squad player unavailability and identifies exposed gaps & internal replacements."""

    @classmethod
    def run_scenario(
        cls,
        team_id: int,
        team_name: str,
        all_players: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        unavailable_player_ids: List[int],
    ) -> ScenarioAnalysisResponse:

        unavail_set = set(unavailable_player_ids)
        available_players = [p for p in all_players if p.id not in unavail_set]
        unavailable_players = [p for p in all_players if p.id in unavail_set]

        # 1. Compute Baseline & Scenario Balance Reports
        baseline_report = SquadBalanceAnalyzer.analyze_squad(
            team_id, team_name, all_players, analytics_map
        )
        scenario_report = SquadBalanceAnalyzer.analyze_squad(
            team_id, team_name, available_players, analytics_map
        )

        score_delta = round(scenario_report.overall_balance_score - baseline_report.overall_balance_score, 1)

        # 2. Identify Newly Exposed Gaps
        newly_exposed: List[str] = []
        base_weaknesses = set(baseline_report.weaknesses)
        for w in scenario_report.weaknesses:
            if w not in base_weaknesses:
                newly_exposed.append(w)

        for unavail in unavailable_players:
            if RoleClassifier.is_wicketkeeper(unavail):
                newly_exposed.append(f"Unavailable player '{unavail.name}' was primary Wicketkeeper!")
            if RoleClassifier.is_death_bowler(analytics_map.get(unavail.id)):
                newly_exposed.append(f"Unavailable player '{unavail.name}' was key Death Bowler!")

        # Deduplicate gaps
        newly_exposed = list(dict.fromkeys(newly_exposed))

        # 3. Recommend Internal Bench Replacements
        replacements: List[InternalReplacementOption] = []
        for unavail in unavailable_players:
            # Find bench player of similar role
            best_bench = None
            best_score = -1.0
            for bench_p in available_players:
                if bench_p.role == unavail.role or (RoleClassifier.is_all_rounder(bench_p) and RoleClassifier.is_all_rounder(unavail)):
                    a = analytics_map.get(bench_p.id)
                    s = a.intelligence_score.overall_score if a else 50.0
                    if s > best_score:
                        best_score = s
                        best_bench = bench_p

            if best_bench:
                replacements.append(
                    InternalReplacementOption(
                        player_id=best_bench.id,
                        player_name=best_bench.name,
                        role=best_bench.role,
                        intelligence_score=best_score,
                        replacement_fit_reason=f"Recommended internal replacement for '{unavail.name}' ({unavail.role.value.upper()}).",
                    )
                )

        explanation = (
            f"Scenario simulation for {team_name} with {len(unavailable_player_ids)} unavailable player(s). "
            f"Squad balance score changed from {baseline_report.overall_balance_score} to "
            f"{scenario_report.overall_balance_score} (delta: {score_delta:+.1f})."
        )

        return ScenarioAnalysisResponse(
            team_id=team_id,
            team_name=team_name,
            unavailable_player_ids=unavailable_player_ids,
            baseline_balance_score=baseline_report.overall_balance_score,
            scenario_balance_score=scenario_report.overall_balance_score,
            score_delta=score_delta,
            newly_exposed_gaps=newly_exposed,
            recommended_replacements=replacements,
            explanation=explanation,
        )
