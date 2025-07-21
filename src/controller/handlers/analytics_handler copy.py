from typing import Dict, Tuple

from model.domain import Semester
from model.domain.entities import Assignment, Examination, Subject
from model.repositories.data_persistence import DataPersistence


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

    def get_all_subjects(self) -> Dict[str, Subject]:
        """Retrieve all subjects for the semester, including synchronized subjects."""
        # Build a lookup for all subjects by (semester, subject_code)
        subject_lookup = {}
        for sem_name, sem_data in self.data_persistence.data.items():
            for subj_code, subj in sem_data.items():
                subject_lookup[(sem_name, subj_code)] = subj

        # Use DuckDB to get the list of (semester, subject_code) to include
        import pandas as pd
        import duckdb

        rows = []
        for (sem_name, subj_code), subj in subject_lookup.items():
            sync_subject = False
            if isinstance(subj, dict):
                sync_subject = subj.get("sync_subject", False)
            elif hasattr(subj, "sync_subject"):
                sync_subject = subj.sync_subject
            rows.append({
                "semester": sem_name,
                "subject_code": subj_code,
                "sync_subject": sync_subject,
            })
        df = pd.DataFrame(rows)
        con = duckdb.connect(database=':memory:')
        con.register('subjects', df)
        query = f"""
            SELECT * FROM subjects
            WHERE semester = '{self.semester.name}'
            UNION
            SELECT * FROM subjects
            WHERE semester != '{self.semester.name}'
                AND sync_subject = TRUE
                AND subject_code NOT IN (
                    SELECT subject_code FROM subjects WHERE semester = '{self.semester.name}'
                )
        """
        selected = con.execute(query).df()

        # Now, fetch the original objects
        result_subjects = {}
        for _, row in selected.iterrows():
            subj = subject_lookup[(row['semester'], row['subject_code'])]
            # If subj is a dict, convert to Subject, else use as-is
            if isinstance(subj, dict):
                subj_obj = self._convert_to_subject(row['subject_code'], subj)
            else:
                subj_obj = subj
            result_subjects[row['subject_code']] = subj_obj

        return result_subjects

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
