from typing import Dict, Tuple

from model.domain import Semester
from model.domain.entities import Assignment, Examination, Subject
from model.repositories.data_persistence import DataPersistence


class AnalyticsHandler:
    """Handles analytics and data aggregation operations."""

    def __init__(self, semester: Semester, data_persistence: DataPersistence):
        self.semester = semester
        self.data_persistence = data_persistence

    def get_all_subjects(self) -> Dict[str, Subject]:
        """Retrieve all subjects for the semester, including synchronized subjects."""
        subjects = dict(self.semester.subjects)

        # Add synchronized subjects from other semesters
        for sem_name, sem_data in self.data_persistence.data.items():
            if sem_name == self.semester.name:
                continue

            for subj_code, subj in sem_data.items():
                is_synced = self._is_subject_synced(subj)

                if is_synced and subj_code not in subjects:
                    subject = self._convert_to_subject(subj_code, subj)
                    subjects[subj_code] = subject

        return subjects

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
        """Convert dictionary or object to Subject instance."""
        if isinstance(subj, dict):
            assignments = [Assignment(**a) for a in subj.get("assignments", [])]
            examinations = Examination(**subj.get("examinations", {})) if "examinations" in subj else None

            return Subject(
                subject_code=subj_code,
                subject_name=subj.get("subject_name", "N/A"),
                assignments=assignments,
                total_mark=subj.get("total_mark", 0.0),
                examinations=examinations or Examination(exam_mark=0, exam_weight=100),
                sync_subject=True,
            )
        else:
            return subj


# Backward compatibility functions
def get_all_subjects(sem_obj: Semester, data_persistence: DataPersistence) -> Dict[str, Subject]:
    """Backward compatibility wrapper."""
    handler = AnalyticsHandler(sem_obj, data_persistence)
    return handler.get_all_subjects()


def get_summary(subject: Subject) -> Tuple[float, float, float, float, float]:
    """Backward compatibility wrapper."""
    return AnalyticsHandler.get_subject_summary(subject)
