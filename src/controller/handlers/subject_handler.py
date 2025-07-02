from typing import Tuple

from model.domain import Semester, Subject
from model.repositories.data_persistence import DataPersistence


class SubjectHandler:
    """Handles subject-related operations."""

    def __init__(self, semester: Semester, data_persistence: DataPersistence):
        self.semester = semester
        self.data_persistence = data_persistence

    def add_subject(self, code: str, name: str, sync_subject: bool = False) -> Tuple[bool, str]:
        """
        Add a new subject to the semester.

        Args:
            code: Unique subject code
            name: Subject name
            sync_subject: Whether to sync across semesters

        Returns:
            Tuple of (success, message)
        """
        if not code or not name:
            return False, "Subject code and name cannot be empty."

        if code in self.semester.subjects:
            return False, "Subject code already exists."

        try:
            self.semester.add_subject(code, name, sync_subject=sync_subject)
            return True, f"Added subject {code}."
        except Exception as e:
            return False, f"Failed to add subject: {str(e)}"

    def delete_subject(self, code: str) -> Tuple[bool, str]:
        """
        Delete a subject from the semester.

        Args:
            code: Subject code to delete

        Returns:
            Tuple of (success, message)
        """
        if code not in self.semester.subjects:
            return False, "Subject not found."

        try:
            self.semester.delete_subject(code)
            return True, f"Deleted subject {code}."
        except Exception as e:
            return False, f"Failed to delete subject: {str(e)}"

    # In your manage tab where total marks are set
    def set_total_mark(self, subject_code: str, total_mark: float):
        """Set total mark and automatically calculate exam mark if needed."""
        subject = self.semester.subjects.get(subject_code)
        if not subject:
            return False, "Subject not found"

        # Set the total mark
        subject.total_mark = total_mark

        # Check if exam should be calculated automatically
        exam_keywords = ["exam", "final", "test", "final exam", "final test"]
        existing_exam = None

        # Look for existing exam in assignments
        for assignment in subject.assignments:
            if any(keyword in assignment.subject_assessment.lower() for keyword in exam_keywords):
                existing_exam = assignment
                break

        # Check if exam already exists in examinations section
        has_exam_in_examinations = (
            hasattr(subject, "examinations")
            and subject.examinations
            and hasattr(subject.examinations, "exam_mark")
            and subject.examinations.exam_mark is not None
            and subject.examinations.exam_mark > 0
        )

        # Calculate what the exam mark should be (always calculate for reference)
        assignment_total = 0.0
        assignment_weight_total = 0.0

        for assignment in subject.assignments:
            # Skip exam assignments and ensure numeric values
            is_exam = any(keyword in assignment.subject_assessment.lower() for keyword in exam_keywords)
            if (
                not is_exam
                and assignment.weighted_mark is not None
                and isinstance(assignment.weighted_mark, (int, float))
                and assignment.mark_weight is not None
                and isinstance(assignment.mark_weight, (int, float))
            ):
                assignment_total += float(assignment.weighted_mark)
                assignment_weight_total += float(assignment.mark_weight)

        exam_mark_needed = total_mark - assignment_total
        exam_weight = 100.0 - assignment_weight_total

        # Auto-create exam only if no exam exists anywhere
        if not existing_exam and not has_exam_in_examinations and exam_weight > 0 and exam_mark_needed >= 0:
            from model.domain.entities.examination import Examination

            subject.examinations = Examination(
                exam_mark=exam_mark_needed,
                exam_weight=exam_weight,
            )

            self.data_persistence.save_data(self.data_persistence.data)
            return (
                True,
                f"Total mark set to {total_mark:.1f}. Exam mark automatically calculated as {exam_mark_needed:.1f}",
            )

        # If exam exists, just update total mark and show info message
        elif has_exam_in_examinations:
            current_exam_mark = subject.examinations.exam_mark
            difference = exam_mark_needed - current_exam_mark

            self.data_persistence.save_data(self.data_persistence.data)

            if abs(difference) > 0.1:
                return (
                    True,
                    f"Total mark set to {total_mark:.1f}. Note: Current exam mark ({current_exam_mark:.1f}) differs from calculated ({exam_mark_needed:.1f}) by {difference:.1f}. Check Analytics tab to update if needed.",
                )
            else:
                return (
                    True,
                    f"Total mark set to {total_mark:.1f}. Exam mark matches calculation.",
                )

        # Save the total mark change
        self.data_persistence.save_data(self.data_persistence.data)
        return True, f"Total mark set to {total_mark:.1f}"


# Backward compatibility functions
def add_subject(sem_obj: Semester, code: str, name: str, sync_subject: bool) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = SubjectHandler(sem_obj, sem_obj.data_persistence)
    return handler.add_subject(code, name, sync_subject)


def delete_subject(sem_obj: Semester, code: str) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = SubjectHandler(sem_obj, sem_obj.data_persistence)
    return handler.delete_subject(code)


def set_total_mark(subject: Subject, total_mark: float, data_persistence: DataPersistence) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    subject.total_mark = total_mark
    data_persistence.save_data(data_persistence.data)
    return True, f"Total Mark for '{subject.subject_code}' set to {total_mark}."
