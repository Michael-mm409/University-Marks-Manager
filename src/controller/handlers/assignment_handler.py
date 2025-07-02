from typing import Optional, Tuple, Union

from model.domain import Semester
from model.enums import GradeType


class AssignmentHandler:
    """Handles assignment-related operations."""

    def __init__(self, semester: Semester):
        self.semester = semester

    def add_assignment(
        self, subject_code: str, assessment: str, weighted_mark: Union[float, str], mark_weight: Optional[float]
    ) -> Tuple[bool, str]:
        """
        Add an assignment to a subject.

        Args:
            subject_code: The subject code to add the assignment to
            assessment: Name of the assessment
            weighted_mark: The weighted mark (numeric or S/U)
            mark_weight: Weight of the assignment (None for S/U grades)

        Returns:
            Tuple of (success, message)
        """
        if not assessment:
            return False, "Assessment name cannot be empty."

        # Determine grade type and handle S/U grades
        if isinstance(weighted_mark, str) and weighted_mark.upper() in ["S", "U"]:
            grade_type = GradeType.SATISFACTORY if weighted_mark.upper() == "S" else GradeType.UNSATISFACTORY
            unweighted_mark = None
            final_mark_weight = None
        else:
            try:
                weighted_mark = float(weighted_mark)
                grade_type = GradeType.NUMERIC
                unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight and mark_weight > 0 else 0
                final_mark_weight = mark_weight
            except (ValueError, TypeError):
                return False, "Invalid weighted mark value."

        self.semester.add_entry(
            subject_code=subject_code,
            subject_assessment=assessment,
            weighted_mark=weighted_mark,
            unweighted_mark=unweighted_mark,
            mark_weight=final_mark_weight,
            grade_type=grade_type.value if isinstance(grade_type, GradeType) else grade_type,
        )
        return True, f"Added assignment '{assessment}' to {subject_code}."

    def delete_assignment(self, subject_code: str, assessment: str) -> Tuple[bool, str]:
        """
        Delete an assignment from a subject.

        Args:
            subject_code: The subject code
            assessment: Name of the assessment to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            self.semester.delete_entry(subject_code, assessment)
            return True, f"Deleted assessment '{assessment}' from {subject_code}."
        except Exception as e:
            return False, f"Failed to delete assignment: {str(e)}"


# Backward compatibility functions
def add_assignment(
    sem_obj: Semester,
    subject_code: str,
    assessment: str,
    weighted_mark: Union[float, str],
    mark_weight: Optional[float],
) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = AssignmentHandler(sem_obj)
    return handler.add_assignment(subject_code, assessment, weighted_mark, mark_weight)


def delete_assignment(sem_obj: Semester, subject_code: str, assessment: str) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = AssignmentHandler(sem_obj)
    return handler.delete_assignment(subject_code, assessment)
