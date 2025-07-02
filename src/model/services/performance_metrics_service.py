"""Performance metrics and statistics service."""

import statistics
from typing import Any, Dict, List


class PerformanceMetricsService:
    """Service for calculating and analyzing academic performance metrics.

    This service provides statistical analysis capabilities for student marks,
    including performance metrics, trend analysis, and progress tracking towards
    grade targets. All methods are static as this is a stateless service.

    Example:
        >>> marks = [75.0, 80.0, 85.0]
        >>> metrics = PerformanceMetricsService.calculate_performance_metrics(marks)
        >>> print(metrics['average'])  # 80.0
    """

    @staticmethod
    def calculate_performance_metrics(marks: List[float]) -> Dict[str, float]:
        """Calculate comprehensive performance metrics for a set of marks.

        Args:
            marks: List of numerical marks/grades to analyze

        Returns:
            Dictionary containing:
                - average: Mean of all marks
                - highest: Maximum mark
                - lowest: Minimum mark
                - std_dev: Standard deviation (0.0 if only one mark)
                - consistency: Consistency percentage (100% = perfectly consistent)

        Example:
            >>> marks = [75.0, 80.0, 85.0]
            >>> metrics = PerformanceMetricsService.calculate_performance_metrics(marks)
            >>> metrics['average']
            80.0
        """
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
        """Calculate consistency percentage based on coefficient of variation.

        Consistency is measured as the inverse of the coefficient of variation,
        where 100% means all marks are identical, and lower percentages indicate
        more variation in performance.

        Args:
            marks: List of marks to analyze

        Returns:
            Consistency percentage (0-100)
        """
        if len(marks) <= 1:
            return 100.0

        std_dev: float = statistics.stdev(marks)
        mean: float = statistics.mean(marks)

        if mean > 0:
            return (1 - (std_dev / mean)) * 100
        else:
            return 100.0

    @staticmethod
    def analyze_trend(marks: List[float]) -> Dict[str, Any]:
        """Analyze performance trend from first to last mark.

        Compares the first and last marks to determine if performance is
        improving, declining, or stable. Uses a threshold of ±5 points
        to determine significance.

        Args:
            marks: List of marks in chronological order

        Returns:
            Dictionary containing trend analysis:
                - has_trend: Whether trend analysis is possible (requires ≥2 marks)
                - first_mark: First mark in the sequence
                - last_mark: Last mark in the sequence
                - trend_change: Numeric change (last - first)
                - trend_direction: "improving", "declining", or "stable"
        """
        if len(marks) < 2:
            return {"has_trend": False}

        first_mark: float = marks[0]
        last_mark: float = marks[-1]
        trend_change: float = last_mark - first_mark

        if trend_change > 5:
            direction: str = "improving"
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
        """Calculate progress towards standard academic grade targets.

        Evaluates current performance against Pass (50%), Credit (65%),
        Distinction (75%), and High Distinction (85%) thresholds.

        Args:
            current_mark: Current mark/grade as a percentage

        Returns:
            Dictionary with progress towards each grade target:
                - target_value: The threshold percentage for this grade
                - progress_percent: Progress towards target (0-100+)
                - achieved: Whether target has been reached
                - emoji: Visual indicator for the grade level
                - status: Text status ("Achieved", "Almost there", "Needs work")
        """
        targets: Dict[str, Dict[str, Any]] = {
            "Pass": {"value": 50, "emoji": "🔴"},
            "Credit": {"value": 65, "emoji": "🟠"},
            "Distinction": {"value": 75, "emoji": "🔵"},
            "High Distinction": {"value": 85, "emoji": "🟢"},
        }

        progress: Dict[str, Dict[str, Any]] = {}
        for name, target in targets.items():
            target_value: int = target["value"]
            progress_percent: float = min(100, (current_mark / target_value) * 100)

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
        """Get descriptive status based on progress percentage.

        Args:
            progress_percent: Progress towards target (0-100+)

        Returns:
            Status message: "Achieved", "Almost there", or "Needs work"
        """
        if progress_percent >= 100:
            return "Achieved"
        elif progress_percent >= 80:
            return "Almost there"
        else:
            return "Needs work"
