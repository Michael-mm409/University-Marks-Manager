# src/view/components/forms/subject_forms.py
"""Subject management form components."""

import streamlit as st

from controller import add_subject, delete_subject
from controller.app_controller import AppController


class SubjectForms:
    """Handles subject-related form components."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render_add_form(self) -> None:
        """Render add subject form."""
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        with st.form("add_subject_form"):
            subject_code = st.text_input("Subject Code")
            subject_name = st.text_input("Subject Name")
            sync_subject = st.checkbox("Sync Subject")

            if st.form_submit_button("Add Subject"):
                if subject_code and subject_name:
                    success, message = add_subject(
                        self.controller.semester_obj, subject_code, subject_name, sync_subject
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.warning(message)
                else:
                    st.error("Please fill in all fields")

    def render_delete_form(self) -> None:
        """Render delete subject form."""
        subjects = self.controller.available_subjects
        if not subjects:
            st.info("No subjects to delete.")
            return

        with st.form("delete_subject_form"):
            subject_to_delete = st.selectbox("Select Subject to Delete", subjects)

            if st.form_submit_button("Delete Subject", type="secondary"):
                if self.controller.semester_obj:
                    success, message = delete_subject(self.controller.semester_obj, subject_to_delete)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.warning(message)
