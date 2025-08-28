from typing import Any, Tuple

from model import Semester, Subject

# NOTE: This handler has been refactored to prefer direct SQLite persistence
# operations (upsert_subject, delete_subject, set_total_mark) instead of
# mutating the in-memory JSON-like structure then calling save_data(). The
# underlying DataPersistence alias now points at the SQLite implementation
# which exposes these helper methods. Fallbacks are retained for safety if a
# different persistence backend lacking these helpers is ever supplied.


class SubjectHandler:
    """
    SubjectHandler is responsible for managing subjects within a semester, including adding, deleting,
    and setting total marks for subjects. It interacts with the Semester and DataPersistence classes
    to perform these operations.

    Args:
        semester (Semester): The semester object containing subjects and their details.
        data_persistence (DataPersistence): The persistence layer for saving and retrieving data.

    Methods:
        __init__(semester: Semester, data_persistence: DataPersistence):
            Initializes the SubjectHandler with a semester and data persistence instance.
        add_subject(code: str, name: str, sync_subject: bool = False) -> Tuple[bool, str]:
            Adds a new subject to the semester. Returns a tuple indicating success and a message.
        delete_subject(code: str) -> Tuple[bool, str]:
            Deletes a subject from the semester. Returns a tuple indicating success and a message.
        set_total_mark(subject_code: str, total_mark: float) -> Tuple[bool, str]:
            Sets the total mark for a subject and calculates the exam mark if necessary.
            Returns a tuple indicating success and a message.
    """

    def __init__(self, semester: Semester, data_persistence: Any):  # Using Any to accept protocol/implementation
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
            # Create Subject entity and persist via upsert_subject when available
            subject = Subject(
                subject_code=code,
                subject_name=name,
                sync_subject=sync_subject,
            )

            persistence = self.semester.data_persistence
            if hasattr(persistence, "upsert_subject"):
                # Persist first so cache reload / consistency is ensured
                persistence.upsert_subject(self.semester.name, subject)  # type: ignore[attr-defined]
                # Refresh semester subjects mapping (lightweight cache update already done in persistence)
                self.semester.subjects[code] = subject
            else:
                # Fallback to legacy in-memory add
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
            persistence = self.semester.data_persistence
            if hasattr(persistence, "delete_subject"):
                persistence.delete_subject(self.semester.name, code)  # type: ignore[attr-defined]
                # Remove from semester cache
                self.semester.subjects.pop(code, None)
            else:
                self.semester.delete_subject(code)
            return True, f"Deleted subject {code}."
        except Exception as e:
            return False, f"Failed to delete subject: {str(e)}"

    # In your manage tab where total marks are set
    def set_total_mark(self, subject_code: str, total_mark: float):
        """Set total mark and (legacy) calculate exam mark if needed, persisting via SQLite.

        This keeps the prior behaviour of optionally auto-calculating an exam but now
        persists the total mark through the persistence layer's set_total_mark method
        when available. Exam persistence (examinations table) is currently handled by
        higher-level analytics/exam controllers; here we adjust only the total_mark.
        """
        subject = self.semester.subjects.get(subject_code)
        if not subject:
            return False, "Subject not found"

        subject.total_mark = total_mark

        persistence = self.semester.data_persistence
        if hasattr(persistence, "set_total_mark"):
            persistence.set_total_mark(self.semester.name, subject_code, total_mark)  # type: ignore[attr-defined]
        else:
            # Fallback legacy save
            persistence.save_data(persistence.data)  # type: ignore[attr-defined]

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


def set_total_mark(subject: Subject, total_mark: float, data_persistence: Any) -> Tuple[bool, str]:
    """Backward compatibility wrapper using persistence.set_total_mark when present."""
    subject.total_mark = total_mark
    if hasattr(data_persistence, "set_total_mark"):
        data_persistence.set_total_mark(
            subject.semester_name if hasattr(subject, "semester_name") else "", subject.subject_code, total_mark
        )  # type: ignore[attr-defined]
    else:
        data_persistence.save_data(data_persistence.data)
    return True, f"Total Mark for '{subject.subject_code}' set to {total_mark}."
