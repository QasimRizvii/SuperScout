"""
SuperScout Backend — Statistical Anomaly Detection Engine

Detects statistical outliers, extreme performance rates, and unusual metric distributions.
Classifies anomalies into informational, warning, and critical tiers with evidence explanations.
"""
from typing import Dict, List, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.player import Player
from app.services.data_quality.schemas import (
    AnomalyReportResponse,
    PerformanceAnomalyItem,
    AnomalyReport,
)


class AnomalyDetector:
    """Statistical performance anomaly engine."""

    def __init__(self, db: Session):
        self.db = db

    def detect_all_anomalies(self) -> List[AnomalyReport]:
        resp = self.detect_anomalies()
        reports: List[AnomalyReport] = []
        for item in resp.anomalies:
            reports.append(
                AnomalyReport(
                    entity="Performance",
                    entity_id=item.performance_id,
                    anomaly_type=item.anomaly_type,
                    metric_name=item.metric_name,
                    observed_value=item.metric_value,
                    expected_range=item.benchmark_expected,
                    severity=item.severity.upper(),
                    description=item.explanation
                )
            )
        return reports

    def detect_anomalies(self) -> AnomalyReportResponse:
        anomalies: List[PerformanceAnomalyItem] = []

        # Pre-fetch player lookup map for names
        players = {p.id: p.name for p in self.db.scalars(select(Player)).all()}

        # 1. Scan Batting Anomalies
        bat_perfs = list(self.db.scalars(select(BattingPerformance)).all())
        for b in bat_perfs:
            p_name = players.get(b.player_id, f"Player #{b.player_id}")

            # Extreme Strike Rate (> 400 with min 5 balls)
            if b.balls_faced >= 5 and b.strike_rate and b.strike_rate > 400.0:
                anomalies.append(
                    PerformanceAnomalyItem(
                        performance_id=b.id,
                        performance_type="batting",
                        match_id=b.match_id,
                        player_id=b.player_id,
                        player_name=p_name,
                        metric_name="strike_rate",
                        metric_value=b.strike_rate,
                        benchmark_expected="110.0 - 250.0 SR",
                        anomaly_type="EXTREME_STRIKE_RATE",
                        severity="warning" if b.strike_rate <= 500.0 else "critical",
                        explanation=(
                            f"{p_name} scored {b.runs} off {b.balls_faced} balls (SR {b.strike_rate:.1f}). "
                            "Unusually high scoring rate detected."
                        ),
                    )
                )
            # Ultra low SR with large sample (> 30 balls, SR < 50)
            elif b.balls_faced >= 30 and b.strike_rate is not None and b.strike_rate < 50.0:
                anomalies.append(
                    PerformanceAnomalyItem(
                        performance_id=b.id,
                        performance_type="batting",
                        match_id=b.match_id,
                        player_id=b.player_id,
                        player_name=p_name,
                        metric_name="strike_rate",
                        metric_value=b.strike_rate,
                        benchmark_expected="100.0 - 180.0 SR",
                        anomaly_type="ULTRA_LOW_STRIKE_RATE",
                        severity="informational",
                        explanation=(
                            f"{p_name} scored {b.runs} off {b.balls_faced} balls (SR {b.strike_rate:.1f}). "
                            "Unusually low scoring rate in extended innings."
                        ),
                    )
                )

            # 100% Boundary runs with substantial total (> 30 runs)
            if b.fours is not None and b.sixes is not None and b.runs >= 30:
                b_runs = (b.fours * 4) + (b.sixes * 6)
                if b_runs == b.runs:
                    anomalies.append(
                        PerformanceAnomalyItem(
                            performance_id=b.id,
                            performance_type="batting",
                            match_id=b.match_id,
                            player_id=b.player_id,
                            player_name=p_name,
                            metric_name="boundary_percentage",
                            metric_value=100.0,
                            benchmark_expected="50.0% - 85.0%",
                            anomaly_type="PERFECT_BOUNDARY_INNINGS",
                            severity="informational",
                            explanation=(
                                f"{p_name} scored all {b.runs} runs exclusively via boundaries "
                                f"({b.fours} fours, {b.sixes} sixes)."
                            ),
                        )
                    )

        # 2. Scan Bowling Anomalies
        bowl_perfs = list(self.db.scalars(select(BowlingPerformance)).all())
        for bw in bowl_perfs:
            p_name = players.get(bw.player_id, f"Player #{bw.player_id}")

            # Extreme Economy Rate (> 24.0 with min 1 over)
            if bw.overs >= 1.0 and bw.economy_rate and bw.economy_rate > 24.0:
                anomalies.append(
                    PerformanceAnomalyItem(
                        performance_id=bw.id,
                        performance_type="bowling",
                        match_id=bw.match_id,
                        player_id=bw.player_id,
                        player_name=p_name,
                        metric_name="economy_rate",
                        metric_value=bw.economy_rate,
                        benchmark_expected="6.0 - 15.0 Economy",
                        anomaly_type="EXTREME_HIGH_ECONOMY",
                        severity="warning" if bw.economy_rate <= 36.0 else "critical",
                        explanation=(
                            f"{p_name} conceded {bw.runs_conceded} runs in {bw.overs} overs "
                            f"(Economy {bw.economy_rate:.2f}). High run rate leakage."
                        ),
                    )
                )
            # Ultra low Economy / Maiden Heavy (>= 3 overs, Economy < 3.0)
            elif bw.overs >= 3.0 and bw.economy_rate is not None and bw.economy_rate < 3.0:
                anomalies.append(
                    PerformanceAnomalyItem(
                        performance_id=bw.id,
                        performance_type="bowling",
                        match_id=bw.match_id,
                        player_id=bw.player_id,
                        player_name=p_name,
                        metric_name="economy_rate",
                        metric_value=bw.economy_rate,
                        benchmark_expected="6.0 - 10.0 Economy",
                        anomaly_type="ULTRA_LOW_ECONOMY",
                        severity="informational",
                        explanation=(
                            f"{p_name} conceded only {bw.runs_conceded} runs in {bw.overs} overs "
                            f"(Economy {bw.economy_rate:.2f}). Exceptional spell."
                        ),
                    )
                )

            # High Wicket Haul (>= 5 wickets)
            if bw.wickets >= 5:
                anomalies.append(
                    PerformanceAnomalyItem(
                        performance_id=bw.id,
                        performance_type="bowling",
                        match_id=bw.match_id,
                        player_id=bw.player_id,
                        player_name=p_name,
                        metric_name="wickets",
                        metric_value=float(bw.wickets),
                        benchmark_expected="0 - 3 Wickets",
                        anomaly_type="FIVE_WICKET_HAUL",
                        severity="informational",
                        explanation=f"{p_name} took {bw.wickets} wickets for {bw.runs_conceded} runs. Outstanding bowling performance.",
                    )
                )

        total_scanned = len(bat_perfs) + len(bowl_perfs)
        critical_c = sum(1 for a in anomalies if a.severity == "critical")
        warning_c = sum(1 for a in anomalies if a.severity == "warning")
        info_c = sum(1 for a in anomalies if a.severity == "informational")

        return AnomalyReportResponse(
            total_performances_scanned=total_scanned,
            anomalies_detected_count=len(anomalies),
            critical_count=critical_c,
            warning_count=warning_c,
            informational_count=info_c,
            anomalies=anomalies,
        )
