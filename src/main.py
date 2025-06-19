from datetime import datetime

import streamlit as st

from model.data_persistence import DataPersistence
from model.semester import Semester
from view.streamlit_views import render_main_page


class App:
    def __init__(self):
        col1, col2, col3 = st.columns(3)
        # Set up year options and default
        self.years = [str(y) for y in range(datetime.now().year - 2, datetime.now().year + 3)]
        with col1:
            self.year = st.selectbox("Select Year", self.years, index=self.years.index(str(datetime.now().year)))

        # Data persistence for selected year
        self.data_persistence = DataPersistence(self.year)
        self.semester_names = list(self.data_persistence.data.keys()) or ["Autumn", "Spring", "Annual"]

        with col2:
            # Semester selection
            self.semester = st.selectbox("Select Semester", self.semester_names, index=0)

        # Semester object for selected semester/year
        self.sem_obj = Semester(self.semester or "Autumn", self.year, self.data_persistence)

        # Subject selection
        self.subject_codes = list(self.sem_obj.subjects.keys())
        with col3:
            self.subject_code = st.selectbox("Select Subject", self.subject_codes) if self.subject_codes else None


def main():
    app = App()
    render_main_page(app)


if __name__ == "__main__":
    main()
