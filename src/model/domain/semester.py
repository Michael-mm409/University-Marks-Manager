"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from typing import Dict, Literal, Optional, Union

import streamlit as st  # Use Streamlit for feedback

from model.domain.entities import Assignment, Examination, Subject
from model.repositories.data_persistence import DataPersistence


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

    def __init__(self, name: str, year: str, data_persistence: DataPersistence):
        """
        Initializes a Semester instance.
        """
        self.name = name
        self.year = year
        self.data_persistence = data_persistence
        # Initialize subjects from loaded data if available
        loaded_subjects = self.data_persistence.data.get(self.name, {})
        self.subjects: Dict[str, Subject] = {}
        for code, subj in loaded_subjects.items():
            if isinstance(subj, Subject):
                self.subjects[code] = subj
            elif isinstance(subj, dict):
                # Convert assignments
                assignments = [
                    a if isinstance(a, Assignment) else Assignment(**a)
                    for a in list(subj.get("assignments", subj.get("Assignments", [])) or [])
                ]
                # Convert examinations
                examinations = subj.get("examinations", subj.get("Examinations", None))
                if examinations and isinstance(examinations, dict):
                    examinations = Examination(**examinations)
                elif not examinations:
                    examinations = Examination()
                self.subjects[code] = Subject(
                    subject_code=subj.get("subject_code", code),
                    subject_name=subj.get("subject_name", subj.get("Subject Name", "N/A")),
                    assignments=assignments,
                    total_mark=subj.get("total_mark", subj.get("Total Mark", 0)),
                    examinations=examinations,
                    sync_subject=subj.get("sync_subject", subj.get("Sync Subject", False)),
                )

    def get_subject_data(self, subject_code: str, subject_name: Optional[str] = None) -> Subject:
        """
        Retrieves or initializes subject data for a given subject code within the semester.
        """
        if subject_code not in self.subjects:
            self.subjects[subject_code] = Subject(
                subject_code=subject_code,
                subject_name=subject_name or "N/A",
                assignments=[],
                total_mark=0,
                examinations=Examination(),
                sync_subject=False,
            )
            # Update persistence data
            self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
            self.data_persistence.save_data(self.data_persistence.data)
        return self.subjects[subject_code]

    def add_subject(self, subject_code: str, subject_name: str, sync_subject: bool = False):
        """
        Adds a new subject to the semester.
        Uses Streamlit for feedback instead of QMessageBox.
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

        self.subjects[subject_code] = subject

        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)
        st.success(f"Added new subject '{subject_name}' with code '{subject_code}'.")

    def delete_subject(self, subject_code: str):
        """
        Deletes a subject from the semester.
        """
        if subject_code not in self.subjects:
            st.error(f"Subject '{subject_code}' does not exist.")
            return
        del self.subjects[subject_code]
        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)
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
        Uses Streamlit for feedback.
        """
        if subject_code not in self.subjects:
            st.error(f"Subject '{subject_code}' does not exist in {self.name}.")
            return
        subject = self.subjects[subject_code]
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

        updated = False
        for a in subject.assignments:
            if a.subject_assessment == subject_assessment:
                a.unweighted_mark = unweighted_mark
                a.weighted_mark = weighted_mark
                a.mark_weight = mark_weight
                updated = True
                break
        else:
            assignment = Assignment(
                subject_assessment=subject_assessment,
                unweighted_mark=unweighted_mark,
                weighted_mark=weighted_mark,
                mark_weight=mark_weight,
            )
            subject.assignments.append(assignment)

        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)
        if updated:
            st.info(f"Entry for '{subject_assessment}' updated in semester '{self.name}'.")
        else:
            st.success(f"Entry for '{subject_assessment}' added in semester '{self.name}'.")

    def delete_entry(self, subject_code: str, subject_assessment: str):
        """
        Deletes an assignment entry from a subject.
        """
        if subject_code in self.subjects:
            subject = self.subjects[subject_code]
            subject.assignments = [a for a in subject.assignments if a.subject_assessment != subject_assessment]
            self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
            self.data_persistence.save_data(self.data_persistence.data)
            st.success(f"Deleted assessment '{subject_assessment}' from subject '{subject_code}'.")

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

        # Save to JSON file
        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)

        st.success(f"Calculated and saved exam mark for {subject_code}: {calculated_exam_mark}%")
        return calculated_exam_mark
