from typing import Dict, List, Tuple

from model import DataPersistence, Semester, Subject


class AnalyticsHandler:
    """
    AnalyticsHandler is responsible for managing analytics and data aggregation operations
    related to subjects within a semester. It provides methods to retrieve all subjects,
    including synchronized subjects from other semesters, and calculate summary statistics
    for a given subject.

    Args:
        semester (Semester): The current semester for which analytics are being handled.
        data_persistence (DataPersistence): The persistence layer for accessing and storing data.

    Methods:
        get_all_subjects() -> Dict[str, Subject]:
            Retrieve all subjects for the current semester, including synchronized subjects
            from other semesters.
        get_subject_summary(subject: Subject) -> Tuple[float, float, float, float, float]:
            Calculate and return summary statistics for a given subject, including total
            weighted mark, total weight, exam mark, exam weight, and total mark.
        _is_subject_synced(subj) -> bool:
            Check if a subject is marked for synchronization. This is used to determine
            whether a subject from another semester should be included in the current semester's
            analytics.
        _convert_to_subject(subj_code: str, subj) -> Subject:
            Convert a dictionary or object representation of a subject into a Subject instance.
            This is used to standardize subject data for analytics purposes.
    """

    def __init__(self, semester: Semester, data_persistence: DataPersistence):
        self.semester = semester
        self.data_persistence = data_persistence

    def get_all_subjects_flat(self) -> List[Dict]:
        """Fetch subjects (primary + synced) via direct SQL helper."""
        fetcher = getattr(self.data_persistence, "fetch_subjects_for_analytics", None)
        if callable(fetcher):
            result = fetcher(self.semester.name, include_synced=True)
            if isinstance(result, list):
                return result  # type: ignore[return-value]
            return []
        # Fallback to object version if helper missing
        return [
            {
                "subject_code": s.subject_code,
                "subject_name": s.subject_name,
                "semester_name": self.semester.name,
                "total_mark": s.total_mark,
                "sync_subject": s.sync_subject,
            }
            for s in self.get_all_subjects().values()
        ]

    @staticmethod
    def get_subject_summary(subject: Subject) -> Tuple[float, float, float, float, float]:
        """
        Calculate summary statistics for a subject.

        Args:
            subject: Subject to analyze

        Returns:
            Tuple of (total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark)
        """
        total_weighted_mark = sum(
            entry.weighted_mark for entry in subject.assignments if isinstance(entry.weighted_mark, (int, float))
        )

        total_weight = sum(
            entry.mark_weight for entry in subject.assignments if isinstance(entry.mark_weight, (int, float))
        )

        exam_mark = subject.examinations.exam_mark if subject.examinations else 0
        exam_weight = subject.examinations.exam_weight if subject.examinations else 100
        total_mark = subject.total_mark

        return total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark

    def _is_subject_synced(self, subj) -> bool:
        """Check if a subject is marked for synchronization."""
        if isinstance(subj, dict):
            return subj.get("sync_subject", False)
        elif hasattr(subj, "sync_subject"):
            return subj.sync_subject
        return False

    def _convert_to_subject(self, subj_code: str, subj) -> Subject:
        return subj  # With SQLite backend, subjects already hydrated

    def get_all_subjects(self) -> Dict[str, Subject]:
        """Retrieve all subjects for the semester, including synchronized subjects (returns Subject objects)."""
        # Use existing semester subjects + SQL synced fetch
        subjects = dict(self.semester.subjects)
        fetch_helper = getattr(self.data_persistence, "fetch_synced_subjects", None)
        if callable(fetch_helper):
            synced_obj = fetch_helper(self.semester.name)
            if isinstance(synced_obj, list):
                for s in synced_obj:
                    if getattr(s, "subject_code", None) and s.subject_code not in subjects:
                        subjects[s.subject_code] = s
        return subjects


# Backward compatibility functions
def get_all_subjects(sem_obj: Semester, data_persistence: DataPersistence) -> Dict[str, Subject]:
    """Backward compatibility wrapper."""
    handler = AnalyticsHandler(sem_obj, data_persistence)
    return handler.get_all_subjects()


def get_summary(subject: Subject) -> Tuple[float, float, float, float, float]:
    """Backward compatibility wrapper."""
    return AnalyticsHandler.get_subject_summary(subject)
