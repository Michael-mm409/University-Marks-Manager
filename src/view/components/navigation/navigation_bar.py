"""Navigation bar component."""

import streamlit as st

from controller.app_controller import AppController


class NavigationBar:
    """Handles navigation controls."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self) -> None:
        """Render navigation controls."""
        col1, col2, col3 = st.columns(3)

        with col1:
            self._render_year_selector()

        with col2:
            self._render_semester_selector()

        with col3:
            self._render_subject_selector()

    def _render_year_selector(self) -> None:
        """Render year selection dropdown."""
        selected_year = st.selectbox(
            "Select Year",
            options=self.controller.available_years,
            index=self.controller.available_years.index(self.controller.current_year),
            key="year_select",
        )
        self.controller.set_year(selected_year)

    def _render_semester_selector(self) -> None:
        """Render semester selection dropdown."""
        if self.controller.year:
            selected_semester = st.selectbox(
                "Select Semester", options=self.controller.available_semesters, index=0, key="semester_select"
            )
            success = self.controller.set_semester(selected_semester)
            if not success:
                st.error("Failed to set semester. Please try again.")

    def _render_subject_selector(self) -> None:
        """Render subject selection dropdown."""
        if self.controller.available_subjects:
            selected_subject = st.selectbox(
                "Select Subject", options=self.controller.available_subjects, key="subject_select"
            )
            st.session_state["selected_subject"] = selected_subject
