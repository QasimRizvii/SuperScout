"""
SuperScout Backend — Playing XI Optimizer Module

Constraint-satisfaction recommendation engine for selecting an optimal, explainable 11-player lineup.
"""
from typing import Dict, List, Optional, Set, Tuple
from app.models.enums import PlayerRole
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.squad.role_classifier import RoleClassifier
from app.services.squad.schemas import PlayingXIOptimizationResponse, PlayingXIPlayer


class PlayingXIOptimizer:
    """Constraint-satisfaction optimizer for building balanced 11-player lineups."""

    @classmethod
    def optimize_xi(
        cls,
        team_id: int,
        team_name: str,
        players: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        excluded_player_ids: Optional[Set[int]] = None,
    ) -> PlayingXIOptimizationResponse:

        available_players = [p for p in players if not (excluded_player_ids and p.id in excluded_player_ids)]
        squad_size = len(available_players)

        # Sort available players by intelligence score (highest first)
        def get_score(p: Player) -> float:
            a = analytics_map.get(p.id)
            return a.intelligence_score.overall_score if a else 50.0

        available_players.sort(key=get_score, reverse=True)

        selected_ids: Set[int] = set()
        selected_players: List[Player] = []

        # 1. Select Wicketkeeper (Mandatory if available)
        keeper = next((p for p in available_players if RoleClassifier.is_wicketkeeper(p)), None)
        if not keeper and available_players:
            keeper = available_players[0]

        if keeper:
            selected_players.append(keeper)
            selected_ids.add(keeper.id)

        # 2. Select Bowlers
        bowler_candidates = [
            p for p in available_players
            if p.id not in selected_ids and RoleClassifier.is_capable_bowler(p, analytics_map.get(p.id))
        ]
        bowlers_picked = bowler_candidates[:5]
        for b in bowlers_picked:
            selected_players.append(b)
            selected_ids.add(b.id)

        # 3. Fill remaining slots to reach 11 (or total available)
        remaining_candidates = [p for p in available_players if p.id not in selected_ids]
        needed = min(11 - len(selected_players), len(remaining_candidates))
        for r in remaining_candidates[:needed]:
            selected_players.append(r)
            selected_ids.add(r.id)

        # 4. Batting Order Construction (1 to len(selected_players))
        top_order: List[Player] = []
        middle_order: List[Player] = []
        tailenders: List[Player] = []

        for p in selected_players:
            if p.role in (PlayerRole.BATTER, PlayerRole.WICKETKEEPER_BATTER):
                top_order.append(p)
            elif p.role in (PlayerRole.ALL_ROUNDER, PlayerRole.BOWLING_ALL_ROUNDER, PlayerRole.WICKETKEEPER):
                middle_order.append(p)
            else:
                tailenders.append(p)

        top_order.sort(key=get_score, reverse=True)
        middle_order.sort(key=get_score, reverse=True)
        tailenders.sort(key=get_score, reverse=True)

        ordered_xi: List[Player] = top_order + middle_order + tailenders

        # 5. Captain Selection
        captain = max(selected_players, key=get_score) if selected_players else None

        # 6. Bowling Phase Assignments & Breakdown
        pp_bowlers: List[str] = []
        mid_bowlers: List[str] = []
        death_bowlers: List[str] = []

        for p in selected_players:
            a = analytics_map.get(p.id)
            if RoleClassifier.is_powerplay_bowler(a):
                pp_bowlers.append(p.name)
            if a and (a.bowling.phases.middle.overs or 0.0) >= 1.0:
                mid_bowlers.append(p.name)
            if RoleClassifier.is_death_bowler(a):
                death_bowlers.append(p.name)

        if not pp_bowlers and selected_players:
            pp_bowlers = [p.name for p in selected_players if RoleClassifier.is_pace_bowler(p)][:2]
        if not death_bowlers and selected_players:
            death_bowlers = [p.name for p in selected_players if RoleClassifier.is_capable_bowler(p, analytics_map.get(p.id))][:2]

        # 7. Construct XI Response Items with Selection Reasons
        xi_items: List[PlayingXIPlayer] = []
        batting_summary: List[str] = []

        for pos, p in enumerate(ordered_xi, start=1):
            a = analytics_map.get(p.id)
            score = a.intelligence_score.overall_score if a else 50.0

            if RoleClassifier.is_wicketkeeper(p):
                cap = "Wicketkeeper-Batter"
            elif RoleClassifier.is_all_rounder(p):
                cap = "All-Rounder"
            elif p.role in (PlayerRole.FAST_BOWLER, PlayerRole.MEDIUM_FAST_BOWLER, PlayerRole.SPINNER, PlayerRole.BOWLER):
                cap = "Primary Bowler"
            else:
                cap = "Specialist Batter"

            b_phase = None
            if RoleClassifier.is_death_bowler(a):
                b_phase = "Death Overs"
            elif RoleClassifier.is_powerplay_bowler(a):
                b_phase = "Powerplay"
            elif RoleClassifier.is_capable_bowler(p, a):
                b_phase = "Middle Overs"

            reason = f"Selected at #{pos} for {cap} role (Intelligence Score: {score:.1f}/100)."
            if captain and p.id == captain.id:
                reason += " Designated Team Captain."
            if keeper and p.id == keeper.id:
                reason += " Designated Wicketkeeper."

            xi_items.append(
                PlayingXIPlayer(
                    player_id=p.id,
                    player_name=p.name,
                    role=p.role,
                    batting_position=pos,
                    is_captain=(captain is not None and p.id == captain.id),
                    is_wicketkeeper=(keeper is not None and p.id == keeper.id),
                    primary_capability=cap,
                    bowling_phase_assignment=b_phase,
                    selection_reason=reason,
                )
            )
            batting_summary.append(f"#{pos}: {p.name} ({cap})")

        # 8. Impact Substitutes (Bench players not in XI)
        bench = [p for p in available_players if p.id not in selected_ids]
        bench.sort(key=get_score, reverse=True)
        impact_subs = [p.name for p in bench[:4]]

        warning_str = f" [Note: Squad size is {squad_size}/11; partial lineup constructed.]" if squad_size < 11 else ""
        captain_name = captain.name if captain else "None"
        keeper_name = keeper.name if keeper else "None"

        tactical = (
            f"Recommended Playing XI for {team_name} features {len(pp_bowlers)} powerplay bowling options, "
            f"{len(death_bowlers)} death bowlers, and designated keeper {keeper_name}. "
            f"Captain candidate: {captain_name}.{warning_str}"
        )

        return PlayingXIOptimizationResponse(
            team_id=team_id,
            team_name=team_name,
            recommended_xi=xi_items,
            captain_player_id=captain.id if captain else None,
            captain_player_name=captain_name,
            wicketkeeper_player_id=keeper.id if keeper else None,
            wicketkeeper_player_name=keeper_name,
            batting_order_summary=batting_summary,
            powerplay_bowlers=pp_bowlers,
            middle_bowlers=mid_bowlers,
            death_bowlers=death_bowlers,
            impact_substitute_candidates=impact_subs,
            tactical_summary=tactical,
        )
