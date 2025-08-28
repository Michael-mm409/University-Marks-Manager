"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from typing import Any, Dict, Literal, Optional, Union

import streamlit as st  # Use Streamlit for feedback

from model.domain.entities import Assignment, Examination, Subject
from model.repositories.sqlite_persistence import PersistenceProtocol


class Semester:
    """
    A class to represent a semester in the University Marks Manager application.

    This class is responsible for managing the data related to a specific semester,
    including assignments and examinations.

    Args:
        name (str):
            The name of the semester (e.g., "Autumn", "Spring").
        year (str):
            The academic year for the semester.
        data_persistence (DataPersistence):
            An instance of the DataPersistence class for managing data storage and retrieval.
    """

    def __init__(self, name: str, year: str, data_persistence: PersistenceProtocol):
        self.name = name
        self.year = year
        self.data_persistence = data_persistence
        # Initialize subjects from loaded data if available
        # Leverage already loaded cache (data) but perform lightweight object normalization
        cache_subjects = self.data_persistence.data.get(self.name, {})  # type: ignore[attr-defined]
        self.subjects: Dict[str, Subject] = {}
        for code, subj in cache_subjects.items():
            if isinstance(subj, Subject):
                self.subjects[code] = subj
            elif isinstance(subj, dict):  # legacy dict form
                assignments_raw = subj.get("assignments") or subj.get("Assignments") or []
                assignments_list = assignments_raw if isinstance(assignments_raw, list) else []
                assignments = [a if isinstance(a, Assignment) else Assignment(**a) for a in assignments_list]
                examinations_raw: Any = subj.get("examinations") or subj.get("Examinations")
                if examinations_raw and isinstance(examinations_raw, dict):
                    examination = Examination(**examinations_raw)
                else:
                    examination = examinations_raw if isinstance(examinations_raw, Examination) else Examination()
                self.subjects[code] = Subject(
                    subject_code=subj.get("subject_code", code),
                    subject_name=subj.get("subject_name", subj.get("Subject Name", code)),
                    assignments=assignments,
                    total_mark=subj.get("total_mark", subj.get("Total Mark", 0)),
                    examinations=examination,
                    sync_subject=subj.get("sync_subject", subj.get("Sync Subject", False)),
                )

    def get_subject_data(self, subject_code: str, subject_name: Optional[str] = None) -> Subject:
        """
        If the subject code does not exist in the current semester's subjects, a new `Subject`
        instance is created and added to the semester. The new subject is initialized with
        the provided subject code, an optional subject name (defaulting to "N/A" if not provided),
        an empty list of assignments, a total mark of 0, a default `Examination` instance, and
        `sync_subject` set to False. The updated data is then saved using the persistence layer.

        Args:
            subject_code (str): The unique code identifying the subject.
            subject_name (Optional[str]): The name of the subject. Defaults to None.

        Returns:
            Subject: The `Subject` instance corresponding to the given subject code."""
        if subject_code not in self.subjects:
            new_subject = Subject(
                subject_code=subject_code,
                subject_name=subject_name or "N/A",
                assignments=[],
                total_mark=0,
                examinations=Examination(),
                sync_subject=False,
            )
            if hasattr(self.data_persistence, "upsert_subject"):
                self.data_persistence.upsert_subject(self.name, new_subject)  # type: ignore[attr-defined]
            self.subjects[subject_code] = new_subject
        return self.subjects[subject_code]

    def add_subject(self, subject_code: str, subject_name: str, sync_subject: bool = False):
        """
        This method allows adding a new subject to the semester by providing its
        code, name, and an optional flag to indicate if the subject should be
        synchronized. It provides feedback using Streamlit messages.
        Args:
            subject_code (str): The unique code of the subject to be added.
            subject_name (str): The name of the subject to be added.
            sync_subject (bool, optional): A flag indicating whether the subject
                should be synchronized. Defaults to False.
        Returns:
            None
        Raises:
            None
        Feedback:
            - Displays an error message if the subject code already exists.
            - Displays an error message if the subject code or name is empty.
            - Displays a success message upon successful addition of the subject.
        """

        if subject_code in self.subjects:
            st.error(f"Subject '{subject_code}' already exists.")
            return

        if not subject_code or not subject_name:
            st.error("Subject code and name cannot be empty.")
            return

        subject = Subject(
            subject_code=subject_code,
            subject_name=subject_name,
            sync_subject=sync_subject,
        )

        if hasattr(self.data_persistence, "upsert_subject"):
            self.data_persistence.upsert_subject(self.name, subject)  # type: ignore[attr-defined]
        self.subjects[subject_code] = subject
        st.success(f"Added new subject '{subject_name}' with code '{subject_code}'.")

    def delete_subject(self, subject_code: str):
        """
        Deletes a subject from the semester based on the provided subject code.
        Args:
            subject_code (str): The code of the subject to be deleted.

        Behavior:
            - Checks if the subject code exists in the `subjects` dictionary.
            - If the subject code does not exist, displays an error message using `st.error`.
            - If the subject code exists, removes the subject from the `subjects` dictionary.
            - Updates the data persistence layer with the modified subjects data.
            - Saves the updated data to persistent storage.
            - Displays a success message using `st.success` upon successful deletion.

        Raises:
            None
        """

        if subject_code not in self.subjects:
            st.error(f"Subject '{subject_code}' does not exist.")
            return
        if hasattr(self.data_persistence, "delete_subject"):
            self.data_persistence.delete_subject(self.name, subject_code)  # type: ignore[attr-defined]
        self.subjects.pop(subject_code, None)
        st.success(f"Deleted subject '{subject_code}'.")

    def add_entry(
        self,
        subject_code: str,
        subject_assessment: str,
        weighted_mark: Union[float, str],
        unweighted_mark: Optional[float],
        mark_weight: Optional[float],
        grade_type: Literal["numeric", "S", "U"],
    ) -> None:
        """
        Adds or updates an entry for a subject assessment in the semester.

        Args:
            subject_code (str): The code of the subject to which the assessment belongs.
            subject_assessment (str): The name or identifier of the assessment.
            weighted_mark (Union[float, str]): The weighted mark for the assessment, or a grade type ("S" or "U").
            unweighted_mark (Optional[float]): The unweighted mark for the assessment (calculated if not provided).
            mark_weight (Optional[float]): The weight of the assessment in the subject's overall grade.
            grade_type (Literal["numeric", "S", "U"]): The type of grade, either numeric or pass/fail ("S" or "U").

        Returns:
            None

        Behavior:
            - If the subject does not exist in the semester, an error message is displayed.
            - If the grade type is "S" or "U", the unweighted mark and mark weight are set to None, and the weighted mark is set to the grade type.
            - If the grade type is numeric, the weighted mark and mark weight must be provided, and the unweighted mark is calculated.
            - If an assessment with the same name already exists, its details are updated.
            - If no such assessment exists, a new one is added to the subject.
            - The updated data is saved to persistent storage.
            - Displays a success or info message depending on whether the entry was added or updated.
        """
        if subject_code not in self.subjects:
            st.error(f"Subject '{subject_code}' does not exist in {self.name}.")
            return
        # Retrieve subject (already validated existence above) - local ref not needed beyond validation
        if grade_type in ("S", "U"):
            unweighted_mark = None
            mark_weight = None
            weighted_mark = grade_type
        else:
            if weighted_mark is None or mark_weight is None:
                st.error("Weighted mark and mark weight must not be empty.")
                return
            weighted_mark = float(weighted_mark)
            mark_weight = float(mark_weight)
            unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

        # Delegate persistence to assignment upsert
        if hasattr(self.data_persistence, "upsert_assignment"):
            from model.enums import GradeType  # local import to avoid circular

            grade_enum = (
                GradeType.SATISFACTORY
                if weighted_mark == "S"
                else (GradeType.UNSATISFACTORY if weighted_mark == "U" else GradeType.NUMERIC)
            )
            self.data_persistence.upsert_assignment(  # type: ignore[attr-defined]
                self.name,
                subject_code,
                subject_assessment,
                weighted_mark,
                unweighted_mark,
                mark_weight,
                grade_enum,
            )
            # Refresh local cache from persistence fresh data for this subject
            refreshed = self.data_persistence.data.get(self.name, {}).get(subject_code)  # type: ignore[attr-defined]
            if isinstance(refreshed, Subject):
                self.subjects[subject_code] = refreshed
            changed = any(a.subject_assessment == subject_assessment for a in self.subjects[subject_code].assignments)
            st.success(
                f"Entry for '{subject_assessment}' {'updated' if changed else 'added'} in semester '{self.name}'."
            )
        else:
            st.error("Persistence layer missing upsert_assignment; operation not applied.")

    def delete_entry(self, subject_code: str, subject_assessment: str):
        """
        Deletes an assessment entry from a specific subject in the semester.

        Args:
            subject_code (str): The code of the subject from which the assessment will be deleted.
            subject_assessment (str): The name or identifier of the assessment to be deleted.

        Behavior:
            - If the specified subject exists in the semester, it removes the assessment
              matching the given `subject_assessment` from the subject's assignments.
            - Updates the data persistence layer with the modified subject data.
            - Saves the updated data to persistent storage.
            - Displays a success message indicating the assessment has been deleted.

        Raises:
            KeyError: If the `subject_code` does not exist in the semester's subjects.
        """
        if subject_code in self.subjects:
            if hasattr(self.data_persistence, "delete_assignment"):
                self.data_persistence.delete_assignment(self.name, subject_code, subject_assessment)  # type: ignore[attr-defined]
                # refresh subject cache
                refreshed = self.data_persistence.data.get(self.name, {}).get(subject_code)  # type: ignore[attr-defined]
                if isinstance(refreshed, Subject):
                    self.subjects[subject_code] = refreshed
                st.success(f"Deleted assessment '{subject_assessment}' from subject '{subject_code}'.")
            else:
                st.error("Persistence layer missing delete_assignment; operation not applied.")

    def calculate_exam_mark(self, subject_code: str) -> Optional[float]:
        """
        Calculate the exam mark based on total mark and assignment marks, then save it.

        Formula: exam_mark = total_mark - assignment_total

        Args:
            subject_code: The subject to calculate exam mark for

        Returns:
            Calculated exam mark, or None if calculation not possible
        """
        subject = self.subjects.get(subject_code)
        if not subject:
            return None

        # Get current assignment marks (only numeric grades)
        assignment_total = sum(
            a.weighted_mark for a in subject.assignments if isinstance(a.weighted_mark, (float, int))
        )

        # Simple calculation: exam mark = total mark - assignment total
        calculated_exam_mark = subject.total_mark - assignment_total

        # Ensure exam mark is within valid range
        calculated_exam_mark = max(0.0, min(100.0, calculated_exam_mark))
        calculated_exam_mark = round(calculated_exam_mark, 2)

        # Get exam weight (remaining weight after assignments)
        assignment_weight = sum(a.mark_weight for a in subject.assignments if a.mark_weight is not None)
        exam_weight = 100.0 - assignment_weight

        # Update the subject's examination data
        if not subject.examinations:
            subject.examinations = Examination()

        subject.examinations.exam_mark = calculated_exam_mark
        subject.examinations.exam_weight = exam_weight

        # Persist via examination helper if available
        if hasattr(self.data_persistence, "upsert_exam"):
            self.data_persistence.upsert_exam(self.name, subject_code, calculated_exam_mark, exam_weight)  # type: ignore[attr-defined]
            # Refresh cache for subject
            refreshed = self.data_persistence.data.get(self.name, {}).get(subject_code)  # type: ignore[attr-defined]
            if isinstance(refreshed, Subject):
                self.subjects[subject_code] = refreshed
        else:
            # Legacy fallback
            self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
            self.data_persistence.save_data(self.data_persistence.data)

        st.success(f"Calculated and saved exam mark for {subject_code}: {calculated_exam_mark}%")
        return calculated_exam_mark
