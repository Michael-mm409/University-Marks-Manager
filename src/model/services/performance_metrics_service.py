"""Performance metrics and statistics service."""

import statistics
from typing import Any, Dict, List


class PerformanceMetricsService:
    """Service for performance metrics calculations."""

    @staticmethod
    def calculate_performance_metrics(marks: List[float]) -> Dict[str, float]:
        """Calculate performance metrics."""
        if not marks:
            return {}

        return {
            "average": sum(marks) / len(marks),
            "highest": max(marks),
            "lowest": min(marks),
            "std_dev": statistics.stdev(marks) if len(marks) > 1 else 0.0,
            "consistency": PerformanceMetricsService._calculate_consistency(marks),
        }

    @staticmethod
    def _calculate_consistency(marks: List[float]) -> float:
        """Calculate consistency percentage."""
        if len(marks) <= 1:
            return 100.0

        std_dev = statistics.stdev(marks)
        mean = statistics.mean(marks)

        if mean > 0:
            return (1 - (std_dev / mean)) * 100
        else:
            return 100.0

    @staticmethod
    def analyze_trend(marks: List[float]) -> Dict[str, Any]:
        """Analyze performance trend."""
        if len(marks) < 2:
            return {"has_trend": False}

        first_mark = marks[0]
        last_mark = marks[-1]
        trend_change = last_mark - first_mark

        if trend_change > 5:
            direction = "improving"
        elif trend_change < -5:
            direction = "declining"
        else:
            direction = "stable"

        return {
            "has_trend": True,
            "first_mark": first_mark,
            "last_mark": last_mark,
            "trend_change": trend_change,
            "trend_direction": direction,
        }

    @staticmethod
    def calculate_progress_to_targets(current_mark: float) -> Dict[str, Dict[str, Any]]:
        """Calculate progress to grade targets."""
        targets = {
            "Pass": {"value": 50, "emoji": "🔴"},
            "Credit": {"value": 65, "emoji": "🟠"},
            "Distinction": {"value": 75, "emoji": "🔵"},
            "High Distinction": {"value": 85, "emoji": "🟢"},
        }

        progress = {}
        for name, target in targets.items():
            target_value = target["value"]
            progress_percent = min(100, (current_mark / target_value) * 100)

            progress[name] = {
                "target_value": target_value,
                "progress_percent": progress_percent,
                "achieved": progress_percent >= 100,
                "emoji": target["emoji"],
                "status": PerformanceMetricsService._get_progress_status(progress_percent),
            }

        return progress

    @staticmethod
    def _get_progress_status(progress_percent: float) -> str:
        """Get status message based on progress percentage."""
        if progress_percent >= 100:
            return "Achieved"
        elif progress_percent >= 80:
            return "Almost there"
        else:
            return "Needs work"
