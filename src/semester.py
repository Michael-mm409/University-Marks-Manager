"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""
from PyQt6.QtWidgets import QMessageBox
from typing import List, Dict, Any
from collections import OrderedDict

from data_persistence import DataPersistence


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
        self.data = self.data_persistence.data.get(self.name, {})

        # print(self.data)

    def __get_subject_data(self, semester: str, subject_code: str, subject_name: str = None) -> Dict[str, Any]:
        """Retrieve the subject data for a given semester and subject code."""
        if semester not in self.data_persistence.data:
            self.data_persistence.data[semester] = {}

        if subject_code not in self.data_persistence.data[semester]:
            self.data_persistence.data[semester][subject_code] = OrderedDict([
                ("Subject Name", subject_name if subject_name else "N/A"),
                ("Assignments", []),
                ("Total Mark", 0),
                ("Examinations", {"Exam Mark": 0, "Exam Weight": 100})
            ])
        else:
            # Update the subject name if it is provided and different from the existing one
            if subject_name and self.data_persistence.data[semester][subject_code].get("Subject Name") != subject_name:
                self.data_persistence.data[semester][subject_code]["Subject Name"] = subject_name
                # Reorder the dictionary to ensure "Subject Name" is the first key
                self.data_persistence.data[semester][subject_code] = OrderedDict([
                    ("Subject Name", self.data_persistence.data[semester][subject_code]["Subject Name"]),
                    ("Assignments", self.data_persistence.data[semester][subject_code]["Assignments"]),
                    ("Total Mark", self.data_persistence.data[semester][subject_code]["Total Mark"]),
                    ("Examinations", self.data_persistence.data[semester][subject_code]["Examinations"])
                ])

        return self.data_persistence.data[semester][subject_code]

    @staticmethod
    def __validate_float(value: Any, error_message: str) -> float:
        """Validate the input value and return it as a float."""
        if value is None or value == "":
            return 0
        try:
            return float(value)
        except ValueError:
            QMessageBox.critical(None, "Error", error_message)
            return -1

    def add_subject(self, subject_code: str, subject_name: str, sync_subject: bool = False):
        """Add a new subject to the semester."""
        if subject_code in self.data:
            raise ValueError(f"Subject '{subject_code}' already exists.")

        self.data[subject_code] = {
            "Subject Name": subject_name,
            "Assignments": [],
            "Total Mark": 0,
            "Examinations": {"Exam Mark": 0, "Exam Weight": 100},
            "Sync Subject": sync_subject  # Add the sync subject flag
        }
        self.data_persistence.save_data()

    def add_entry(self, semester: str, subject_code: str, subject_assessment: str,
                  weighted_mark: float | int, mark_weight: float) -> None:
        """
        Add or update an entry for a subject in the specified semester.

        Args:
            semester (str): The name of the semester.
            subject_code (str): The code of the subject.
            subject_assessment (str): The name of the assessment.
            weighted_mark (float): The weighted mark for the assessment.
            mark_weight (float): The weight of the assessment.

        Raises:
            ValueError: If the subject does not exist in the specified semester.
        """
        # Ensure the semester exists in the data persistence layer
        if semester not in self.data_persistence.data:
            self.data_persistence.data[semester] = {}

        # Retrieve or initialize the subject data for the specified semester
        if subject_code not in self.data_persistence.data[semester]:
            self.data_persistence.data[semester][subject_code] = {
                "Subject Name": "N/A",
                "Assignments": [],
                "Total Mark": 0,
                "Examinations": {"Exam Mark": 0, "Exam Weight": 100}
            }

        # Get the subject data for the specified semester
        subject_data = self.data_persistence.data[semester][subject_code]

        # Remove "No Assignments" placeholder if it exists
        assignments: List[Dict[str, Any]] = subject_data["Assignments"]
        if len(assignments) == 1 and assignments[0].get("Subject Assessment") == "No Assignments":
            assignments.clear()  # Clear the placeholder assignment

        # Validate and calculate the marks
        weighted_mark = self.__validate_float(weighted_mark, "Weighted Mark must be a valid number.")
        mark_weight = self.__validate_float(mark_weight, "Mark Weight must be a valid number.")
        if mark_weight < 0 or mark_weight > 100:
            QMessageBox.critical(None, "Error", "Mark Weight must be between 0 and 100.")
            return

        unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

        # Check if the assessment already exists
        for entry in assignments:
            if entry.get("Subject Assessment") == subject_assessment:
                # Update the existing entry instead of adding a new one
                entry.update(
                    {"Unweighted Mark": unweighted_mark,
                     "Weighted Mark": weighted_mark,
                     "Mark Weight": mark_weight})
                self.data_persistence.save_data()
                QMessageBox.information(None, "Info", f"Updated existing entry for '{subject_assessment}' in semester '{semester}'.")
                return

        # If the assessment does not exist, add it to the list
        new_assessment = {
            "Subject Assessment": subject_assessment,
            "Unweighted Mark": unweighted_mark,
            "Weighted Mark": weighted_mark,
            "Mark Weight": mark_weight
        }
        assignments.append(new_assessment)

        # Adjust exam weight if mark weight was provided
        if mark_weight != -1:
            subject_data["Examinations"]["Exam Weight"] -= mark_weight

        # Save the updated data
        self.data_persistence.save_data()
        QMessageBox.information(None, "Info", f"Added new entry for '{subject_assessment}' in semester '{semester}'.")

    def delete_entry(self, subject_code: str, subject_assessment: str):
        if subject_code in self.data:
            assignments = self.data[subject_code]["Assignments"]
            for assignment in assignments:
                if assignment["Subject Assessment"] == subject_assessment:
                    assignments.remove(assignment)
                    break
            else:
                raise ValueError(f"Assessment '{subject_assessment}' not found for subject '{subject_code}'")
        else:
            raise ValueError(f"Subject '{subject_code}' not found in semester '{self.name}'")

        # Update the data in the persistence layer
        self.data_persistence.data[self.name] = self.data
        self.data_persistence.save_data()

    def delete_subject(self, subject_code: str):
        """Remove a subject from the semester."""
        if subject_code not in self.data:
            raise ValueError(f"Subject '{subject_code}' does not exist.")
        del self.data[subject_code]
        self.data_persistence.save_data()

    def view_data(self) -> List[List[str]]:
        """Retrieve and format semester data for display."""
        sorted_data_list = []

        sorted_subjects = sorted(self.data.items(), key=lambda item: item[0])  # Sort by subject code
        for subject_code, subject_data in sorted_subjects:
            subject_name = subject_data.get("Subject Name", "N/A")
            total_mark = subject_data.get("Total Mark", 0)

            # Check if there are no assignments and add a placeholder if necessary
            if not subject_data["Assignments"]:
                subject_data["Assignments"].append({
                    "Subject Assessment": "No Assignments",
                    "Unweighted Mark": 0.0,
                    "Weighted Mark": 0.0,
                    "Mark Weight": 0.0
                })

            # Add assignments to the list
            for entry in subject_data["Assignments"]:
                sorted_data_list.append([
                    subject_code,
                    subject_name,
                    entry.get("Subject Assessment", "N/A").strip("\n"),
                    f"{entry.get('Unweighted Mark', 0):.2f}",
                    f"{entry.get('Weighted Mark', 0):.2f}",
                    f"{entry.get('Mark Weight', 0):.2f}%",
                    f"{total_mark:.2f}"
                ])

            # Add summary row for the subject
            total_weighted_mark = sum(entry.get("Weighted Mark", 0) for entry in subject_data["Assignments"])
            total_weight = sum(entry.get("Mark Weight", 0) for entry in subject_data["Assignments"])
            exam_mark = subject_data["Examinations"].get("Exam Mark", 0)
            exam_weight = subject_data["Examinations"].get("Exam Weight", 0)

            sorted_data_list.append([
                f"Summary for {subject_code}",
                f"Assessments: {len(subject_data['Assignments'])}",
                f"Total Weighted: {total_weighted_mark:.2f}",
                f"Total Weight: {total_weight:.0f}%",
                f"Total Mark: {total_mark:.0f}",
                f"Exam Mark: {exam_mark:.2f}",
                f"Exam Weight: {exam_weight:.0f}%"
            ])

            # Dynamically create a centered separator line
            max_cell_width = max(len(str(cell)) for row in sorted_data_list[-1:] for cell in row)
            separator_line = "=" * max_cell_width
            centered_separator = [separator_line.center(max_cell_width)] * 7
            sorted_data_list.append(centered_separator)

        return sorted_data_list

    def calculate_exam_mark(self, subject_code: str) -> float:
        """Calculate the exam mark for a given subject based on the current semester's data."""
        subject_data = self.__get_subject_data(self.name, subject_code)
        total_mark = subject_data.get("Total Mark", 0)
        assessments_sum = sum(entry.get("Weighted Mark", 0)
                              for entry in subject_data.get("Assignments", []))
        assessments_weight = sum(entry.get("Mark Weight", 0)
                                 for entry in subject_data.get("Assignments", []))

        # Calculate exam mark
        exam_mark = max(0, round(total_mark - assessments_sum, 2))
        exam_weight = max(0, 100 - assessments_weight)

        subject_data["Examinations"]["Exam Mark"] = exam_mark
        subject_data["Examinations"]["Exam Weight"] = exam_weight

        self.data_persistence.save_data()
        QMessageBox.information(None, "Success", f"Exam mark calculated: {exam_mark}")
        return exam_mark

    def get_synced_subjects(self) -> List[Dict[str, Any]]:
        """Retrieve all subjects with 'sync subject: true'."""
        return [
            {"Subject Code": code, **data}
            for code, data in self.data.items()
            if data.get("Sync Source", False)
        ]
