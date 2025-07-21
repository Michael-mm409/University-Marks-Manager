# domain/services/grade_calculator.py
from typing import Optional

from domain.entities.subject import Subject


class GradeCalculatorService:
    """Service for grade calculations."""

    @staticmethod
    def calculate_required_exam_mark(subject: Subject) -> Optional[float]:
        """Calculate required exam mark to achieve target."""
        # Move the calculation logic here from Semester class
        pass

    @staticmethod
    def calculate_current_total(subject: Subject) -> float:
        """Calculate current total based on completed work."""
        pass
