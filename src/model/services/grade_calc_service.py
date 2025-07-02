"""Grade calculation service."""

from typing import List, Tuple

from model.domain.entities.subject import Subject


class GradeCalculationService:
    """Service for grade calculations."""

    @staticmethod
    def calculate_grade_status(subject: Subject) -> Tuple[float, str, bool]:
        """Calculate grade value from available data.

        Returns:
            Tuple of (grade_value, grade_source, has_total_mark)
        """
        has_total_mark = subject.total_mark is not None and subject.total_mark >= 0

        if has_total_mark:
            return subject.total_mark, "Total Mark", True
        else:
            # Calculate from assignments
            assignment_marks = []
            for assignment in subject.assignments:
                if assignment.weighted_mark is not None:
                    try:
                        assignment_marks.append(float(assignment.weighted_mark))
                    except (TypeError, ValueError):
                        continue

            if assignment_marks:
                return GradeCalculationService._calculate_assignment_grade(assignment_marks)
            else:
                return 0, "No data", False

    @staticmethod
    def _calculate_assignment_grade(assignment_marks: List[float]) -> Tuple[float, str, bool]:
        """Calculate grade based on assignment performance."""
        max_mark = max(assignment_marks)

        if max_mark <= 20:  # Smaller scale detected
            assignment_percentages = [(mark / max_mark) * 100 for mark in assignment_marks]
            grade_value = sum(assignment_percentages) / len(assignment_percentages)
            grade_source = f"Assignment Average (scaled from /{max_mark:.0f})"
        else:
            grade_value = sum(assignment_marks) / len(assignment_marks)
            grade_source = "Assignment Average"

        return grade_value, grade_source, False

    @staticmethod
    def get_grade_level(mark: float) -> Tuple[str, str]:
        """Get grade level and emoji for a mark."""
        if mark >= 85:
            return "High Distinction", "🎉"
        elif mark >= 75:
            return "Distinction", "🌟"
        elif mark >= 65:
            return "Credit", "✅"
        elif mark >= 50:
            return "Pass", "📈"
        else:
            return "Fail", "❌"
