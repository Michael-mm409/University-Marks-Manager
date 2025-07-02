"""Grade calculation service."""

from typing import List, Tuple

from model.domain.entities.assignment import Assignment
from model.domain.entities.subject import Subject


class GradeCalculationService:
    """Service for grade calculations."""

    @staticmethod
    def calculate_grade_status(subject: Subject) -> Tuple[float, str, bool]:
        """Calculate grade status with zero-mark handling.

        Args:
            subject: Subject entity containing assignments and total mark

        Returns:
            Tuple of (grade_value, grade_source, has_total_mark)
        """
        # Check if total mark is set and greater than 0
        if subject.total_mark is not None and subject.total_mark > 0:
            # Use total mark for final grade calculation
            grade_value: float = subject.total_mark
            grade_source: str = "final grade"
            has_total_mark: bool = True
            return grade_value, grade_source, has_total_mark

        # If total mark is 0 or None, check assignment performance
        assignment_total: float = GradeCalculationService._calculate_assignment_total(subject.assignments)

        if assignment_total > 0:
            # Calculate assignment-based percentage
            weight_total: float = GradeCalculationService._calculate_weight_total(subject.assignments)
            if weight_total > 0:
                grade_value: float = (assignment_total / weight_total) * 100
                grade_source: str = "assignments"
                has_total_mark: bool = False
                return grade_value, grade_source, has_total_mark

        # No marks available at all
        return 0.0, "no marks available", False

    @staticmethod
    def _calculate_assignment_total(assignments: List[Assignment]) -> float:
        """Calculate total marks from assignments.

        Args:
            assignments: List of assignment entities

        Returns:
            Total weighted marks from all assignments
        """
        total: float = 0.0
        for assignment in assignments:
            if assignment.weighted_mark is not None:
                try:
                    weighted_mark: float = float(assignment.weighted_mark)
                    total += weighted_mark
                except (TypeError, ValueError):
                    continue
        return total

    @staticmethod
    def _calculate_weight_total(assignments: List[Assignment]) -> float:
        """Calculate total weight from assignments.

        Args:
            assignments: List of assignment entities

        Returns:
            Total weight/maximum marks from all assignments
        """
        total_weight: float = 0.0
        for assignment in assignments:
            # FIX: Use mark_weight instead of weight
            if assignment.mark_weight is not None:
                try:
                    mark_weight: float = float(assignment.mark_weight)
                    total_weight += mark_weight
                except (TypeError, ValueError):
                    continue
        return total_weight

    @staticmethod
    def get_grade_level(grade_value: float) -> Tuple[str, str]:
        """Get grade level and emoji, handling zero values.

        Args:
            grade_value: Percentage grade value (0-100)

        Returns:
            Tuple of (grade_level, emoji)
        """
        # FIX: Don't assign a grade if no marks are available
        if grade_value <= 0:
            return "Not Set", "📋"

        if grade_value >= 85:
            return "High Distinction", "🎉"
        elif grade_value >= 75:
            return "Distinction", "🌟"
        elif grade_value >= 65:
            return "Credit", "✅"
        elif grade_value >= 50:
            return "Pass", "📈"
        else:
            return "Fail", "⚠️"
