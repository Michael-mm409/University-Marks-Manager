"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from typing import Any, Dict, List, Optional, Union

import streamlit as st

from model import DataKeys, DataPersistence, GradeType
from model.models import Assignment, Examination, Subject


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

    def __init__(self, name: str, year: str, data_persistence: DataPersistence) -> None:
        """
        Initializes a Semester instance.
        """
        self.name: str = name
        self.year: str = year
        self.data_persistence: DataPersistence = data_persistence
        # Initialize subjects from loaded data if available
        loaded_subjects: Dict[str, Any] = self.data_persistence.data.get(self.name, {})
        self.subjects: Dict[str, Subject] = {}

        for code, subj in loaded_subjects.items():
            if isinstance(subj, Subject):
                self.subjects[code] = subj
            elif isinstance(subj, dict):
                # Convert assignments with proper typing
                assignment_data: List[Union[Assignment, Dict[str, Any]]] = (
                    subj.get(DataKeys.ASSIGNMENTS.value, subj.get(DataKeys.ASSIGNMENTS_LEGACY.value, [])) or []
                )

                assignments: List[Assignment] = [
                    a if isinstance(a, Assignment) else Assignment(**a) for a in assignment_data
                ]

                # Convert examinations with proper typing
                examinations_data: Optional[Union[Examination, Dict[str, Any]]] = subj.get(
                    DataKeys.EXAMINATIONS.value, subj.get(DataKeys.EXAMINATIONS_LEGACY.value, None)
                )

                examinations: Examination
                if examinations_data and isinstance(examinations_data, dict):
                    examinations = Examination(**examinations_data)
                elif isinstance(examinations_data, Examination):
                    examinations = examinations_data
                else:
                    examinations = Examination()

                self.subjects[code] = Subject(
                    subject_code=subj.get(DataKeys.SUBJECT_CODE.value, code),
                    subject_name=subj.get(
                        DataKeys.SUBJECT_NAME.value, subj.get(DataKeys.SUBJECT_NAME_LEGACY.value, "N/A")
                    ),
                    assignments=assignments,
                    total_mark=subj.get(DataKeys.TOTAL_MARK.value, subj.get(DataKeys.TOTAL_MARK_LEGACY.value, 0.0)),
                    examinations=examinations,
                    sync_subject=subj.get(
                        DataKeys.SYNC_SUBJECT.value, subj.get(DataKeys.SYNC_SUBJECT_LEGACY.value, False)
                    ),
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
                total_mark=0.0,
                examinations=Examination(),
                sync_subject=False,
            )
            # Update persistence data
            self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
            self.data_persistence.save_data(self.data_persistence.data)
        return self.subjects[subject_code]

    def add_subject(self, subject_code: str, subject_name: str, sync_subject: bool = False) -> None:
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

        subject: Subject = Subject(
            subject_code=subject_code,
            subject_name=subject_name,
            sync_subject=sync_subject,
        )

        self.subjects[subject_code] = subject

        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)
        st.success(f"Added new subject '{subject_name}' with code '{subject_code}'.")

    def delete_subject(self, subject_code: str) -> None:
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
        grade_type: GradeType = GradeType.NUMERIC,
    ) -> None:
        """
        Adds or updates an entry for a subject assessment in the semester.
        Uses Streamlit for feedback.
        """
        if subject_code not in self.subjects:
            st.error(f"Subject '{subject_code}' does not exist in {self.name}.")
            return

        subject: Subject = self.subjects[subject_code]

        # Handle different grade types using GradeType enum
        if grade_type in [GradeType.SATISFACTORY, GradeType.UNSATISFACTORY]:
            unweighted_mark = None
            mark_weight = None
            weighted_mark = grade_type.value  # Use enum value
        else:
            if weighted_mark is None or mark_weight is None:
                st.error("Weighted mark and mark weight must not be empty.")
                return
            weighted_mark_float: float = float(weighted_mark)
            mark_weight_float: float = float(mark_weight)
            weighted_mark = weighted_mark_float
            mark_weight = mark_weight_float
            unweighted_mark = round(weighted_mark_float / mark_weight_float, 4) if mark_weight_float > 0 else 0.0

        updated: bool = False
        for assignment in subject.assignments:
            if assignment.subject_assessment == subject_assessment:
                assignment.unweighted_mark = unweighted_mark
                assignment.weighted_mark = weighted_mark
                assignment.mark_weight = mark_weight
                assignment.grade_type = grade_type
                updated = True
                break
        else:
            new_assignment: Assignment = Assignment(
                subject_assessment=subject_assessment,
                unweighted_mark=unweighted_mark,
                weighted_mark=weighted_mark,
                mark_weight=mark_weight,
                grade_type=grade_type,
            )
            subject.assignments.append(new_assignment)

        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)

        if updated:
            st.info(f"Entry for '{subject_assessment}' updated in semester '{self.name}'.")
        else:
            st.success(f"Entry for '{subject_assessment}' added in semester '{self.name}'.")

    def delete_entry(self, subject_code: str, subject_assessment: str) -> None:
        """
        Deletes an assignment entry from a subject.
        """
        if subject_code in self.subjects:
            subject: Subject = self.subjects[subject_code]
            original_count: int = len(subject.assignments)
            subject.assignments = [
                assignment for assignment in subject.assignments if assignment.subject_assessment != subject_assessment
            ]

            if len(subject.assignments) < original_count:
                self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
                self.data_persistence.save_data(self.data_persistence.data)
                st.success(f"Deleted assessment '{subject_assessment}' from subject '{subject_code}'.")
            else:
                st.warning(f"Assessment '{subject_assessment}' not found in subject '{subject_code}'.")

    def calculate_exam_mark(self, subject_code: str) -> Optional[float]:
        """
        Calculate the required exam percentage for a given subject to achieve the target total mark.

        Formula: Required Exam Percentage = (Target Total - Assignment Contribution) / (Exam Weight / 100)

        Args:
            subject_code: The subject code to calculate for

        Returns:
            Required exam percentage (0-100), or None if calculation is not possible
        """
        subject: Optional[Subject] = self.subjects.get(subject_code)
        if not subject:
            return None

        # Get target total mark
        target_total: float = subject.total_mark
        if target_total <= 0:
            return None

        # Calculate total assignment contribution (sum of weighted marks)
        assignment_contribution: float = 0.0

        for assignment in subject.assignments:
            # Only include numeric grades in calculation, use GradeType enum
            if assignment.grade_type == GradeType.NUMERIC and isinstance(assignment.weighted_mark, (int, float)):
                assignment_contribution += float(assignment.weighted_mark)

        # Get exam weight
        examinations: Optional[Examination] = subject.examinations
        if not examinations or examinations.exam_weight <= 0:
            return None

        exam_weight: float = examinations.exam_weight

        # Calculate required exam percentage
        # If target_total = assignment_contribution + (exam_percentage * exam_weight / 100)
        # Then: exam_percentage = (target_total - assignment_contribution) / (exam_weight / 100)
        required_exam_contribution: float = target_total - assignment_contribution
        required_exam_percentage: float = required_exam_contribution / (exam_weight / 100)

        calculated_percentage: float = round(required_exam_percentage, 2)

        # Save the calculated exam mark to the examination data
        subject.examinations.exam_mark = calculated_percentage

        # Update persistence data and save to JSON
        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)

        # Provide feedback to user
        st.success(f"Calculated and saved required exam percentage for {subject_code}: {calculated_percentage}%")

        return calculated_percentage
