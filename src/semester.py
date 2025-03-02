"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from collections import OrderedDict
from tkinter import messagebox
from typing import List

from data_persistence import DataPersistence
from semester_logic import add_entry, calculate_exam_mark, sort_subjects, view_data


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

    def add_entry(
        self, subject_code, subject_name, subject_assessment, weighted_mark, mark_weight, total_mark, sync_source=False
    ) -> None:
        add_entry(
            self, subject_code, subject_name, subject_assessment, weighted_mark, mark_weight, total_mark, sync_source
        )

    def sort_subjects(self, sort_by: str = "subject_code") -> List[List[str]]:
        return sort_subjects(self, sort_by)

    def view_data(self) -> List[List[str]]:
        return view_data(self)

    def calculate_exam_mark(self, subject_code: str) -> float:
        return calculate_exam_mark(self, subject_code)

    def add_subject(self, subject_code: str, subject_name: str, sync_source: bool = False) -> None:
        sem_data = self.data_persistence.data.get(self.name, {})
        if subject_code in sem_data:
            messagebox.showerror("Error", f"Subject '{subject_code}' already exists.")
            return

        subject_data = OrderedDict(
            [
                ("Subject Name", subject_name),
                ("Assignments", []),
                ("Examinations", {"Exam Mark": 0, "Exam Weight": 100}),
                ("Sync Source", sync_source),
                ("Total Mark", 0),
            ]
        )

        sem_data[subject_code] = subject_data
        self.data_persistence.data[self.name] = sem_data
        self.data_persistence.save_data()

    def remove_subject(self, subject_code: str) -> None:
        sem_data = self.data_persistence.data.get(self.name, {})
        if subject_code in sem_data:
            del sem_data[subject_code]
            self.data_persistence.data[self.name] = sem_data
            self.data_persistence.save_data()
        else:
            # Optionally, log that the subject was not found
            pass
