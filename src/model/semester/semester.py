"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from model.persistence.data_persistence import DataPersistence
from model.subject.subject_manager import SubjectManager
from model.utils.data_formatter import DataFormatter  # Direct import to avoid circular dependency
from view.dialogs import ask_add_total_mark

from .assignment_manager import AssignmentManager
from .examination_manager import ExaminationManager


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
        self.subject_manager = SubjectManager(self)
        self.assignment_manager = AssignmentManager(self)
        self.examination_manager = ExaminationManager(self)

    def sort_subjects(self, sort_by: str = "subject_code"):
        return DataFormatter.sort_subjects(self, sort_by)

    def add_total_mark(self, subject_code: str, parent_window) -> None:
        """
        Add or update the total mark for a subject in the semester.

        Args:
            subject_code (str): The code of the subject.
            parent_window: The parent window for the dialog.

        Raises:
            ValueError: If the subject code is not found or the total mark is invalid.
        """
        # Retrieve the semester data
        sem_data = self.data_persistence.data.get(self.name, {})
        subject_data = sem_data.get(subject_code)

        if not subject_data:
            raise ValueError(f"Subject '{subject_code}' does not exist in semester '{self.name}'.")

        # Use the ask_add_total_mark dialog to get the total mark
        total_mark = ask_add_total_mark(parent_window, title="Add Total Mark", message="Enter the total mark:")
        if total_mark is None:
            raise ValueError("No total mark was provided.")

        # Validate the total mark
        if total_mark < 0 or total_mark > 100:
            raise ValueError("Total mark must be between 0 and 100.")

        # Update the total mark for the subject
        subject_data["Total Mark"] = total_mark
        self.data_persistence.data[self.name][subject_code] = subject_data
        self.data_persistence.save_data()
