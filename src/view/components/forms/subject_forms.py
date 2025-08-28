"""
Subject management form components.

This module defines the `SubjectForms` class, which provides Streamlit-based UI forms
to support adding and deleting subjects within a semester context.

Forms include:
    - Add Subject Form
    - Delete Subject Form

These forms interact with controller functions (`add_subject`, `delete_subject`) and
provide feedback based on user actions.

Dependencies:
    - streamlit
    - controller (add_subject, delete_subject)
    - AppController
"""

import streamlit as st

from controller import add_subject, delete_subject
from controller.app_controller import AppController


class SubjectForms:
    """
    Handles Streamlit form rendering for managing subjects.

    Args:
        controller (AppController): The application controller used to access semester
            state and subject management logic.
    """

    def __init__(self, controller: AppController):
        """
        Initialize the SubjectForms component.

        Args:
            controller (AppController): Controller instance for accessing app state.
        """
        self.controller = controller

    def render_add_form(self) -> None:
        """
        Render the form to add a new subject.

        Displays input fields for:
            - Subject code
            - Subject name
            - Sync subject checkbox (optional flag for external sync)

        On submission:
            - Validates the input
            - Calls `add_subject()` from the controller
            - Displays feedback messages (success, warning, error)
            - Triggers rerun if successful
        """
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        # Persistent feedback display
        feedback_key = "subject_add_feedback"
        if fb := st.session_state.get(feedback_key):
            st.success(fb)  # Could differentiate types later
            if st.button("Dismiss", key=f"dismiss_{feedback_key}", type="secondary"):
                st.session_state.pop(feedback_key, None)
                st.rerun()

        with st.form("add_subject_form"):
            subject_code = st.text_input("Subject Code")
            subject_name = st.text_input("Subject Name")
            sync_subject = st.checkbox("Sync Subject")
            attempt_flag = "_subject_add_attempted"
            # Show validation error only after attempted submit; auto-hide when corrected
            if st.session_state.get(attempt_flag) and (not subject_code or not subject_name):
                st.error("Please fill in all fields")
            elif st.session_state.get(attempt_flag) and subject_code and subject_name:
                st.session_state.pop(attempt_flag, None)

            if st.form_submit_button("Add Subject"):
                if not subject_code or not subject_name:
                    st.session_state[attempt_flag] = True
                    st.error("Please fill in all fields")
                else:
                    success, message = add_subject(
                        self.controller.semester_obj, subject_code, subject_name, sync_subject
                    )
                    if success:
                        st.session_state[feedback_key] = message
                        st.session_state.pop(attempt_flag, None)
                        st.rerun()
                    else:
                        st.warning(message)

    def render_delete_form(self) -> None:
        """
        Render the form to delete an existing subject.

        Displays a dropdown of available subjects and allows the user to delete a selected one.

        On submission:
            - Calls `delete_subject()` from the controller
            - Displays success or warning message
            - Triggers rerun if successful
        """
        subjects = self.controller.available_subjects
        if not subjects:
            st.info("No subjects to delete.")
            return

        feedback_key = "subject_delete_feedback"
        if fb := st.session_state.get(feedback_key):
            st.success(fb)
            if st.button("Dismiss", key=f"dismiss_{feedback_key}", type="secondary"):
                st.session_state.pop(feedback_key, None)
                st.rerun()

        with st.form("delete_subject_form"):
            subject_to_delete = st.selectbox("Select Subject to Delete", subjects)
            if st.form_submit_button("Delete Subject", type="secondary"):
                if self.controller.semester_obj:
                    success, message = delete_subject(self.controller.semester_obj, subject_to_delete)
                    if success:
                        st.session_state[feedback_key] = message
                        st.rerun()
                    else:
                        st.warning(message)
