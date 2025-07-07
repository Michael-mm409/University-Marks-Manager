"""
Navigation bar component.

This module defines the `NavigationBar` class, responsible for rendering
the top-level navigation controls in the Streamlit interface. These controls
allow users to select:
    - Year
    - Semester
    - Subject

Selections are handled via dropdown menus and update the Streamlit session state
or controller state accordingly.

Dependencies:
    - streamlit
    - AppController
"""

import streamlit as st

from controller.app_controller import AppController


class NavigationBar:
    """
    Handles navigation controls in the application UI.

    This component provides dropdown-based navigation for year, semester,
    and subject selection. Changes to the dropdowns trigger updates to
    the application state via the AppController.

    Args:
        controller (AppController): The main application controller that manages
            current year, semester, and subject selections.
    """

    def __init__(self, controller: AppController):
        """
        Initialize the NavigationBar with the main application controller.

        Args:
            controller (AppController): Controller instance used to access and update
            available years, semesters, and subjects.
        """
        self.controller = controller

    def render(self) -> None:
        """
        Render the navigation bar layout, which includes:

        - Year selector (left column)
        - Semester selector (middle column)
        - Subject selector (right column)

        Each selector updates the application state via the controller or Streamlit session state.
        """
        year_column, semester_column, subject_column = st.columns(3)

        with year_column:
            self._render_year_selector()

        with semester_column:
            self._render_semester_selector()

        with subject_column:
            self._render_subject_selector()

    def _render_year_selector(self) -> None:
        """
        Render a dropdown to select the academic year.

        Updates the controller's current year based on selection.
        """
        selected_year = st.selectbox(
            "Select Year",
            options=self.controller.available_years,
            index=self.controller.available_years.index(self.controller.current_year),
            key="year_select",
        )
        self.controller.set_year(selected_year)

    def _render_semester_selector(self) -> None:
        """
        Render a dropdown to select the semester.

        This is only displayed if a year has been selected.
        On selection, updates the semester in the controller.
        Displays an error if the semester selection fails.
        """
        if self.controller.year:
            selected_semester = st.selectbox(
                "Select Semester", options=self.controller.available_semesters, index=0, key="semester_select"
            )
            success = self.controller.set_semester(selected_semester)
            if not success:
                st.error("Failed to set semester. Please try again.")

    def _render_subject_selector(self) -> None:
        """
        Render a dropdown to select a subject from the available subjects list.

        Updates the Streamlit session state with the selected subject.
        This control is only shown if subjects are available.
        """
        if self.controller.available_subjects:
            selected_subject = st.selectbox(
                "Select Subject", options=self.controller.available_subjects, key="subject_select"
            )
            st.session_state["selected_subject"] = selected_subject
