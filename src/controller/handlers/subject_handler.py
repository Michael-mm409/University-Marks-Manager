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

    def set_total_mark(self, subject: Subject, total_mark: float) -> Tuple[bool, str]:
        """
        Set the total mark for a subject.

        Args:
            subject: Subject object
            total_mark: Total mark to set

        Returns:
            Tuple of (success, message)
        """
        if subject is None:
            return False, "Subject not found."

        try:
            subject.total_mark = total_mark
            self.data_persistence.save_data(self.data_persistence.data)
            return True, f"Total Mark for '{subject.subject_code}' set to {total_mark}."
        except Exception as e:
            return False, f"Failed to set total mark: {str(e)}"


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
