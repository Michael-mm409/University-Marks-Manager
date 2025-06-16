"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from collections import OrderedDict
from typing import Any, Dict, List, Literal, Optional, Union

from PyQt6.QtWidgets import QMessageBox

from model import Assignment, DataPersistence, Examination, Subject


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
        """Initialize Semester with its name, year, and data persistence."""
        self.name = name
        self.year = year
        self.data_persistence = data_persistence
        # Initialize subjects from loaded data if available
        self.subjects: Dict[str, Subject] = self.data_persistence.data.get(self.name, {})

    def get_subject_data(self, subject_code: str, subject_name: Optional[str] = None) -> Dict[str, Any]:
        if self.name not in self.data_persistence.data:
            self.data_persistence.data[self.name] = {}

        if subject_code not in self.data_persistence.data[self.name]:
            self.data_persistence.data[self.name][subject_code] = Subject(
                subject_code=subject_code,
                subject_name=self.data_persistence.data[self.name][subject_code].get(
                    "Subject Name", subject_name or "N/A"
                ),
                assignments=[],
                total_mark=0,
                examinations=Examination(),  # Initialize with an instance of Examination
                sync_subject=False,
            )
        else:
            # Update the subject name if it is provided and different from the existing one
            if subject_code not in self.data_persistence.data[self.name]:
                self.data_persistence.data[self.name][subject_code] = OrderedDict(
                    [
                        ("Subject Name", subject_name if subject_name else "N/A"),
                        ("Assignments", []),
                        ("Total Mark", 0),
                        ("Examinations", {"Exam Mark": 0, "Exam Weight": 100}),
                    ]
                )

        return self.data_persistence.data[self.name][subject_code]

    def add_subject(self, subject_code: str, subject_name: str, sync_subject: bool = False):
        if subject_code in self.subjects:
            QMessageBox.critical(None, "Error", f"Subject '{subject_code}' already exists.")
            return

        # Validate the subject code and name
        if not subject_code or not subject_name:
            QMessageBox.critical(None, "Error", "Subject code and name cannot be empty.")
            return

        # Create a new Subject instance
        subject = Subject(
            subject_code=subject_code,
            subject_name=subject_name,
            sync_subject=sync_subject,
        )

        # Add the subject to the semester's subjects
        self.subjects[subject_code] = subject

        # Save the updated data
        self.data_persistence.data[self.name] = self.subjects
        self.data_persistence.save_data(self.data_persistence.data)
        QMessageBox.information(None, "Info", f"Added new subject '{subject_name}' with code '{subject_code}'.")

    def add_entry(
        self,
        subject_code: str,
        subject_assessment: str,
        weighted_mark: Union[float, str],
        unweighted_mark: Optional[float],
        mark_weight: Optional[float],
        grade_type: Literal["numeric", "S", "U"],
    ) -> None:
        if subject_code not in self.subjects:
            QMessageBox.critical(None, "Error", f"Subject '{subject_code}' does not exist in {self.name}.")
            return
        subject = self.subjects[subject_code]
        # Only assign float or None to unweighted_mark and mark_weight
        if grade_type in ("S", "U"):
            unweighted_mark = None
            mark_weight = None
            weighted_mark = grade_type  # "S" or "U"
        else:
            if weighted_mark is None or mark_weight is None:
                QMessageBox.critical(None, "Error", "Weighted mark and mark weight must not be empty.")
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

        self.data_persistence.data[self.name] = self.subjects
        self.data_persistence.save_data(self.data_persistence.data)
        if updated:
            QMessageBox.information(
                None, "Info", f"Entry for '{subject_assessment}' updated in semester '{self.name}'."
            )
        else:
            QMessageBox.information(None, "Info", f"Entry for '{subject_assessment}' added in semester '{self.name}'.")

    def delete_entry(self, subject_code: str, subject_assessment: str):
        if subject_code in self.subjects:
            subject = self.subjects[subject_code]
            subject.assignments = [a for a in subject.assignments if a.subject_assessment != subject_assessment]
            self.data_persistence.data[self.name] = self.subjects
            self.data_persistence.save_data(self.data_persistence.data)

    def delete_subject(self, subject_code: str):
        if subject_code not in self.subjects:
            raise ValueError(f"Subject '{subject_code}' does not exist.")
        del self.subjects[subject_code]
        self.data_persistence.data[self.name] = self.subjects
        self.data_persistence.save_data(self.data_persistence.data)

    def view_data(self) -> List[List[str]]:
        sorted_data_list = []
        sorted_subjects = sorted(self.subjects.items(), key=lambda item: item[0])

        for subject_code, subject_data in sorted_subjects:
            subject_name = subject_data.subject_name
            total_mark = subject_data.total_mark if hasattr(subject_data, "total_mark") else 0
            # Add assignment rows
            for entry in subject_data.assignments:
                weighted_mark_display = (
                    entry.weighted_mark if isinstance(entry.weighted_mark, str) else f"{entry.weighted_mark:.2f}"
                )
                unweighted_mark_display = "" if entry.unweighted_mark is None else f"{entry.unweighted_mark:.2f}"
                mark_weight_display = "" if entry.mark_weight is None else f"{entry.mark_weight:.2f}"
                sorted_data_list.append(
                    [
                        subject_code,
                        subject_name,
                        entry.subject_assessment.strip("\n") if entry.subject_assessment else "N/A",
                        unweighted_mark_display,
                        weighted_mark_display,
                        mark_weight_display,
                        f"{total_mark:.2f}",
                    ]
                )
            # Add summary row
            total_weighted_mark = sum(
                entry.weighted_mark
                for entry in subject_data.assignments
                if isinstance(entry.weighted_mark, (float, int))
            )
            total_weight = sum(entry.mark_weight for entry in subject_data.assignments if entry.mark_weight is not None)
            exam_mark = subject_data.examinations.exam_mark if hasattr(subject_data, "examinations") else 0
            exam_weight = subject_data.examinations.exam_weight if hasattr(subject_data, "examinations") else 100
            sorted_data_list.append(
                [
                    f"Summary for {subject_code}",
                    f"Assessments: {len(subject_data.assignments)}",
                    f"Total Weighted: {total_weighted_mark:.2f}",
                    f"Total Weight: {total_weight:.0f}%",
                    f"Exam Mark: {exam_mark:.2f}",
                    f"Exam Weight: {exam_weight:.0f}%",
                    f"Total Mark: {total_mark:.0f}",
                ]
            )
            # Add separator row
            separator_row = ["=" * 25 for _ in range(7)]
            sorted_data_list.append(separator_row)
        return sorted_data_list

    def calculate_exam_mark(self, subject_code: str) -> float:
        subject_obj = self.subjects[subject_code]
        total_mark = getattr(subject_obj, "total_mark", 0)
        assessments_sum = sum(getattr(entry, "weighted_mark", 0) for entry in subject_obj.assignments)
        assessments_weight = sum(getattr(entry, "mark_weight", 0) for entry in subject_obj.assignments)

        # Calculate exam mark
        exam_mark = max(0, round(total_mark - assessments_sum, 2))
        exam_weight = max(0, 100 - assessments_weight)

        subject_obj.examinations.exam_mark = exam_mark
        subject_obj.examinations.exam_weight = exam_weight

        self.data_persistence.save_data(self.data_persistence.data)
        QMessageBox.information(None, "Success", f"Exam mark calculated: {exam_mark}")
        return exam_mark

    def get_synced_subjects(self) -> List[Dict[str, Any]]:
        return [
            {
                "Subject Code": code,
                "Subject Name": getattr(data, "subject_name", ""),
                "Sync Subject": getattr(data, "sync_subject", False),
            }
            for code, data in self.subjects.items()
            if hasattr(data, "sync_subject") and getattr(data, "sync_subject", False)
        ]
