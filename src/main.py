from datetime import datetime
from typing import List

import streamlit as st

from model.data_persistence import DataPersistence
from model.semester import Semester
from view.streamlit_views import render_main_page


class App:
    """
    A Streamlit-based application for managing university marks.
    This class provides a user interface for selecting a year, semester, and subject,
    and manages data persistence and semester-specific operations.
    Attributes:
        years (list): A list of year options for selection, ranging from two years
                      before the current year to two years after.
        year (str): The currently selected year.
        data_persistence (DataPersistence): An instance of the DataPersistence class
                                            for managing data storage and retrieval
                                            for the selected year.
        semester_names (list): A list of semester names available for selection.
        semester (str): The currently selected semester.
        sem_obj (Semester): An instance of the Semester class for managing semester-specific
                            operations for the selected semester and year.
        subject_codes (list): A list of subject codes available for the selected semester.
        subject_code (str or None): The currently selected subject code, or None if no
                                    subjects are available.
    Methods:
        __init__(): Initializes the application, sets up the user interface, and manages
                    data persistence and semester-specific operations.
    """

    def __init__(self):
        col1, col2, col3 = st.columns(3)
        # Set up year options and default
        self.years: List[str] = [str(y) for y in range(datetime.now().year - 2, datetime.now().year + 3)]
        with col1:
            self.year: str = st.selectbox("Select Year", self.years, index=self.years.index(str(datetime.now().year)))

        # Data persistence for selected year
        self.data_persistence: DataPersistence = DataPersistence(self.year)
        self.semester_names: List[str] = list(self.data_persistence.data.keys()) or ["Autumn", "Spring", "Annual"]

        with col2:
            # Semester selection
            self.semester: str | None = st.selectbox("Select Semester", self.semester_names, index=0)

        # Semester object for selected semester/year
        self.sem_obj: Semester = Semester(self.semester or "Autumn", self.year, self.data_persistence)

        # Subject selection
        self.subject_codes: List[str] = list(self.sem_obj.subjects.keys())
        with col3:
            self.subject_code: str | None = (
                st.selectbox("Select Subject", self.subject_codes) if self.subject_codes else None
            )


def main():
    app = App()
    render_main_page(app)


if __name__ == "__main__":
    main()
