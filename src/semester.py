"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""
from tkinter import messagebox
from typing import List, Dict, Any

from data_persistence import DataPersistence
from semester_logic import (
    add_entry,
    sort_subjects,
    view_data,
    calculate_exam_mark)


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

    def add_entry(self, subject_code, subject_name, subject_assessment,
                  weighted_mark, mark_weight, total_mark, sync_source=False) -> None:
        add_entry(self, subject_code, subject_name, subject_assessment,
                  weighted_mark, mark_weight, total_mark, sync_source)

    def sort_subjects(self, sort_by: str = "subject_code") -> List[List[str]]:
        return sort_subjects(self, sort_by)

    def view_data(self) -> List[List[str]]:
        return view_data(self)

    def calculate_exam_mark(self, subject_code: str) -> float:
        return calculate_exam_mark(self, subject_code)
