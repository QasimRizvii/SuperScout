"""
SuperScout Backend — Entity Duplicate Detection Engine

Identifies potential duplicate candidates for Players, Teams, Venues, and Matches using fuzzy/exact matching.
Outputs candidate clusters for human review without auto-deleting data.
"""
import re
from typing import Dict, List, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.models.match import Match
from app.services.data_quality.schemas import (
    DuplicateCandidatePair,
    DuplicateReportResponse,
    DuplicateCandidate,
)


def normalize_string(val: Optional[str]) -> str:
    """Normalize string for fuzzy comparison (lowercase, strip punctuation, strip extra whitespace)."""
    if not val:
        return ""
    val = val.lower().strip()
    val = re.sub(r"[^\w\s]", "", val)
    val = re.sub(r"\s+", " ", val)
    return val


def compute_string_similarity(str1: Optional[str], str2: Optional[str]) -> float:
    """Simple Levenshtein / Token similarity score between two normalized strings (0.0 to 100.0)."""
    n1 = normalize_string(str1)
    n2 = normalize_string(str2)
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 100.0
    if n1 in n2 or n2 in n1:
        return 85.0

    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    if not union:
        return 0.0

    jaccard = len(intersection) / len(union)
    return round(jaccard * 100.0, 1)


class DuplicateDetector:
    """Entity deduplication engine identifying duplicate candidate records."""

    def __init__(self, db: Session):
        self.db = db

    def find_duplicate_players(
        self,
        name_similarity_threshold: float = 0.85,
        min_similarity: Optional[float] = None
    ) -> List[DuplicateCandidate]:
        if min_similarity is None:
            min_similarity = name_similarity_threshold * 100.0 if name_similarity_threshold <= 1.0 else name_similarity_threshold

        report = self.find_duplicate_players_report(min_similarity=min_similarity)
        candidates: List[DuplicateCandidate] = []
        for pair in report.duplicates:
            candidates.append(
                DuplicateCandidate(
                    player1_id=pair.entity_1_id,
                    player1_name=pair.entity_1_name,
                    player2_id=pair.entity_2_id,
                    player2_name=pair.entity_2_name,
                    similarity_score=pair.similarity_score / 100.0,
                    matching_fields=pair.matching_factors,
                    recommendation="Merge records into master player entry" if pair.similarity_score >= 90.0 else "Manual review required"
                )
            )
        return candidates

    def find_duplicate_players_report(self, min_similarity: float = 75.0) -> DuplicateReportResponse:
        players = list(self.db.scalars(select(Player)).all())
        pairs: List[DuplicateCandidatePair] = []
        total_checked = 0

        for i in range(len(players)):
            p1 = players[i]
            for j in range(i + 1, len(players)):
                p2 = players[j]
                total_checked += 1

                factors: List[str] = []
                sim = compute_string_similarity(p1.name, p2.name)

                if sim >= 80.0:
                    factors.append(f"Name similarity ({sim:.1f}%)")

                p1_country = p1.nationality
                p2_country = p2.nationality

                if p1_country and p2_country and p1_country.lower() == p2_country.lower():
                    factors.append(f"Matching nationality ({p1_country})")
                    sim += 10.0
                elif p1_country and p2_country and p1_country.lower() != p2_country.lower():
                    sim -= 15.0

                p1_dob = p1.date_of_birth
                p2_dob = p2.date_of_birth

                if p1_dob and p2_dob and p1_dob == p2_dob:
                    factors.append(f"Exact date of birth match ({p1_dob})")
                    sim += 20.0

                final_sim = round(min(100.0, sim), 1)

                if final_sim >= min_similarity and factors:
                    pairs.append(
                        DuplicateCandidatePair(
                            entity_type="Player",
                            entity_1_id=p1.id,
                            entity_1_name=p1.name,
                            entity_2_id=p2.id,
                            entity_2_name=p2.name,
                            similarity_score=final_sim,
                            matching_factors=factors,
                            review_status="PENDING_REVIEW",
                        )
                    )

        pairs.sort(key=lambda x: x.similarity_score, reverse=True)

        return DuplicateReportResponse(
            entity_type="Player",
            total_candidates_checked=total_checked,
            duplicate_pairs_found=len(pairs),
            duplicates=pairs,
        )

    def find_duplicate_teams(self, min_similarity: float = 75.0) -> DuplicateReportResponse:
        teams = list(self.db.scalars(select(Team)).all())
        pairs: List[DuplicateCandidatePair] = []
        total_checked = 0

        for i in range(len(teams)):
            t1 = teams[i]
            for j in range(i + 1, len(teams)):
                t2 = teams[j]
                total_checked += 1

                factors: List[str] = []
                sim = compute_string_similarity(t1.name, t2.name)

                if sim >= 80.0:
                    factors.append(f"Team name similarity ({sim:.1f}%)")

                if t1.abbreviation and t2.abbreviation and t1.abbreviation.lower() == t2.abbreviation.lower():
                    factors.append(f"Matching abbreviation ({t1.abbreviation})")
                    sim += 15.0

                if t1.country and t2.country and t1.country.lower() == t2.country.lower():
                    factors.append(f"Matching country ({t1.country})")
                    sim += 5.0

                final_sim = round(min(100.0, sim), 1)

                if final_sim >= min_similarity and factors:
                    pairs.append(
                        DuplicateCandidatePair(
                            entity_type="Team",
                            entity_1_id=t1.id,
                            entity_1_name=t1.name,
                            entity_2_id=t2.id,
                            entity_2_name=t2.name,
                            similarity_score=final_sim,
                            matching_factors=factors,
                            review_status="PENDING_REVIEW",
                        )
                    )

        pairs.sort(key=lambda x: x.similarity_score, reverse=True)

        return DuplicateReportResponse(
            entity_type="Team",
            total_candidates_checked=total_checked,
            duplicate_pairs_found=len(pairs),
            duplicates=pairs,
        )

    def find_duplicate_matches(self) -> DuplicateReportResponse:
        matches = list(self.db.scalars(select(Match)).all())
        pairs: List[DuplicateCandidatePair] = []
        total_checked = 0

        for i in range(len(matches)):
            m1 = matches[i]
            for j in range(i + 1, len(matches)):
                m2 = matches[j]
                total_checked += 1

                m1_date = m1.match_date
                m2_date = m2.match_date

                if m1_date and m2_date and m1_date == m2_date:
                    same_teams = (
                        (m1.team_1_id == m2.team_1_id and m1.team_2_id == m2.team_2_id) or
                        (m1.team_1_id == m2.team_2_id and m1.team_2_id == m2.team_1_id)
                    )
                    if same_teams:
                        pairs.append(
                            DuplicateCandidatePair(
                                entity_type="Match",
                                entity_1_id=m1.id,
                                entity_1_name=f"Match #{m1.id} ({m1_date})",
                                entity_2_id=m2.id,
                                entity_2_name=f"Match #{m2.id} ({m2_date})",
                                similarity_score=100.0,
                                matching_factors=["Identical match date", "Identical competing teams"],
                                review_status="PENDING_REVIEW",
                            )
                        )

        return DuplicateReportResponse(
            entity_type="Match",
            total_candidates_checked=total_checked,
            duplicate_pairs_found=len(pairs),
            duplicates=pairs,
        )
