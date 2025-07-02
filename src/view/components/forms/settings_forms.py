# src/view/components/forms/settings_forms.py
"""Settings and configuration form components."""

import streamlit as st

from controller import set_total_mark
from controller.app_controller import AppController


class SettingsForms:
    """Handles settings-related form components."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render_total_mark_form(self) -> None:
        """Render set total mark form."""
        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            st.info("Select a subject first")
            return

        if not self.controller.semester_obj or not self.controller.data_persistence:
            st.error("Controller not properly initialized.")
            return

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject:
            st.warning("Subject not found.")
            return

        with st.form(f"set_total_mark_compact_{subject_code}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                new_total_mark = st.number_input(
                    f"Total Mark for {subject_code}",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(subject.total_mark),
                    step=0.01,
                    help=f"Current: {subject.total_mark}",
                )

            with col2:
                if st.form_submit_button("Update", type="secondary"):
                    success, message = set_total_mark(subject, new_total_mark, self.controller.data_persistence)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    def render_semester_settings_form(self) -> None:
        """Render semester-wide settings form."""
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.markdown("#### Semester Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Current Year:** {self.controller.semester_obj.year}")
            st.info(f"**Current Semester:** {self.controller.semester_obj.name}")

        with col2:
            total_subjects = len(self.controller.semester_obj.subjects)
            st.metric("Total Subjects", total_subjects)

    def render_data_management_form(self) -> None:
        """Render data export/import form."""
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.markdown("#### Data Management")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export Data", type="secondary"):
                # Future implementation for data export
                st.info("Export functionality coming soon!")

        with col2:
            if st.button("Backup Data", type="secondary"):
                # Future implementation for data backup
                st.info("Backup functionality coming soon!")
