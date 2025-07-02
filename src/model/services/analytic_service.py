"""Core analytics calculations and business logic."""

from typing import Dict, List, Optional, Tuple

from model import Assignment, Subject


class AnalyticsService:
    """Service for performing analytics calculations."""

    @staticmethod
    def calculate_assignment_total(assignments: List[Assignment]) -> float:
        """Calculate total assignment marks."""
        total = 0.0
        for assignment in assignments:
            if assignment.weighted_mark is not None:
                try:
                    total += float(assignment.weighted_mark)
                except (TypeError, ValueError):
                    continue
        return total

    @staticmethod
    def calculate_weight_total(assignments: List[Assignment]) -> float:
        """Calculate total assignment weights."""
        total = 0.0
        for assignment in assignments:
            if assignment.mark_weight is not None:
                try:
                    total += float(assignment.mark_weight)
                except (TypeError, ValueError):
                    continue
        return total

    @staticmethod
    def get_exam_mark(subject: Subject) -> Optional[float]:
        """Get exam mark if available."""
        if hasattr(subject, "examinations") and subject.examinations:
            if hasattr(subject.examinations, "exam_mark"):
                return subject.examinations.exam_mark
        return None

    @staticmethod
    def detect_marking_scale(marks: List[float]) -> Tuple[float, float]:
        """Detect marking scale and return max_mark and scale_factor."""
        if not marks:
            return 100, 1.0

        max_mark = max(marks)
        if max_mark <= 20:
            return max_mark, max_mark / 100
        else:
            return max_mark, 1.0

    @staticmethod
    def calculate_grade_distribution(marks: List[float], scale_factor: float = 1.0) -> Dict[str, int]:
        """Calculate grade distribution based on marks and scale."""
        return {
            "HD": len([m for m in marks if m >= (85 * scale_factor)]),
            "D": len([m for m in marks if (75 * scale_factor) <= m < (85 * scale_factor)]),
            "C": len([m for m in marks if (65 * scale_factor) <= m < (75 * scale_factor)]),
            "P": len([m for m in marks if (50 * scale_factor) <= m < (65 * scale_factor)]),
            "F": len([m for m in marks if m < (50 * scale_factor)]),
        }

    @staticmethod
    def calculate_exam_requirements(subject: Subject) -> Dict[str, float]:
        """Calculate exam mark requirements."""
        if subject.total_mark is None:
            return {}

        assignment_total = AnalyticsService.calculate_assignment_total(subject.assignments)
        required_exam = max(0, subject.total_mark - assignment_total)

        return {
            "total_mark": subject.total_mark,
            "assignment_total": assignment_total,
            "required_exam": required_exam,
            "achievable": required_exam <= 100,
        }
