from typing import List, Optional, Union

import pandas as pd
import streamlit as st

from controller import add_assignment, add_subject, delete_assignment, delete_subject, get_all_subjects, get_summary
from controller.app_controller import AppController
from model import Subject  # Add missing imports
from model.enums import GradeType


def safe_float(val) -> Optional[float]:  # Add missing return type
    """
    Safely converts a value to a float, or returns None for 'S'/'U' (non-marked assignments).

    Args:
        val: The value to be converted to a float. Can be of any type.

    Returns:
        float or None: The converted float value, or None if the value is 'S' or 'U'.
    """
    if isinstance(val, str) and val.strip().upper() in {GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value}:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_display_value(val) -> str:
    """
    Safely converts a value to a string for display, handling S/U grades properly.

    Args:
        val: The value to be converted for display

    Returns:
        str: The display string
    """
    if isinstance(val, str) and val.upper() in {GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value}:
        return val.upper()
    try:
        return str(float(val))
    except (ValueError, TypeError):
        return ""


class StreamlitView:
    """
    Main Streamlit view class following MVC pattern.
    Handles all UI rendering and user interactions.
    """

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self) -> None:
        """Render the main application interface."""
        st.title("University Marks Manager")

        # Render navigation
        self._render_navigation()

        # Check if ready to render main content
        if not self.controller.is_ready():
            st.info("Please select year and semester to continue.")
            return

        # Render main content
        self._render_main_content()

    def _render_navigation(self) -> None:
        """Render navigation controls."""
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_year = st.selectbox(
                "Select Year",
                options=self.controller.available_years,
                index=self.controller.available_years.index(self.controller.current_year),
                key="year_select",
            )
            self.controller.set_year(selected_year)

        with col2:
            if self.controller.year:
                selected_semester = st.selectbox(
                    "Select Semester", options=self.controller.available_semesters, index=0, key="semester_select"
                )
                success = self.controller.set_semester(selected_semester)
                if not success:
                    st.error("Failed to set semester. Please try again.")

        with col3:
            if self.controller.available_subjects:
                selected_subject = st.selectbox(
                    "Select Subject", options=self.controller.available_subjects, key="subject_select"
                )
                # Store selected subject in session state for components
                st.session_state["selected_subject"] = selected_subject

    def _render_main_content(self) -> None:
        """Render main application content."""
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["&#x1F4CA; Overview", "&#x2795; Manage", "&#x1F4C8; Analytics"])

        with tab1:
            self._render_overview_tab()

        with tab2:
            self._render_manage_tab()

        with tab3:
            self._render_analytics_tab()

    def _render_overview_tab(self) -> None:
        """Render overview tab with subject tables."""
        # Validate controller state
        if not self.controller.semester_obj or not self.controller.data_persistence:
            st.error("Controller not properly initialized.")
            return

        subjects = get_all_subjects(self.controller.semester_obj, self.controller.data_persistence)

        # Now sort all subject codes (current + synced)
        for subject_code in sorted(subjects.keys()):
            subject: Subject = subjects[subject_code]
            st.subheader(
                f"{subject.subject_name} ({subject_code})"
                f"{' - Synced' if getattr(subject, 'sync_subject', False) else ''} "
                f"in {self.controller.semester_obj.name} {self.controller.semester_obj.year}"
            )

            # Fix: Correct indentation and type annotation
            rows: List[List[Union[str, float, None]]] = []
            for assignment in subject.assignments:  # Fix: Proper indentation and variable declaration
                rows.append(
                    [
                        assignment.subject_assessment,
                        assignment.unweighted_mark,
                        assignment.weighted_mark,
                        assignment.mark_weight,
                    ]
                )

            df = pd.DataFrame(
                rows,
                columns=[
                    "Assessment",
                    "Unweighted Mark",
                    "Weighted Mark",
                    "Mark Weight",
                ],
            ).astype(str)

            # --- Add radio buttons for row selection ---
            select_key = f"select_row_{subject_code}"
            if select_key not in st.session_state:
                st.session_state[select_key] = 0  # Default to first row

            st.dataframe(df.reset_index(drop=True), use_container_width=True, key=f"summary_editor_{subject_code}")

            # Summary row (as a separate table or markdown)
            total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark = get_summary(subject)
            st.markdown(
                f"**Summary:**  "
                f"Total Weighted: `{total_weighted_mark:.2f}` &nbsp; | &nbsp; "
                f"Total Weight: `{total_weight:.0f}%` &nbsp; | &nbsp; "
                f"Exam Mark: `{exam_mark:.2f}` &nbsp; | &nbsp; "
                f"Exam Weight: `{exam_weight:.0f}%` &nbsp; | &nbsp; "
                f"Total Mark: `{total_mark:.0f}`"
            )
            st.markdown("---")

    def _render_manage_tab(self) -> None:
        """Render management tab with organized container layout."""

        # Subject Management Section
        with st.container():
            st.markdown("### &#x1F4DA; Subject Management")
            col1, col2 = st.columns(2, gap="medium")

            with col1:
                with st.expander("&#x2795; Add Subject", expanded=True):
                    self._render_add_subject_form()

            with col2:
                with st.expander("&#x1F5D1;&#xFE0F; Delete Subject", expanded=True):
                    self._render_delete_subject_form()

        st.divider()  # Visual separator

        # Assignment Management Section
        with st.container():
            st.markdown("### &#x270E; Assignment Management")
            col1, col2, col3 = st.columns(3, gap="medium")

            with col1:
                with st.expander("&#x2795; Add Assignment", expanded=True):
                    self._render_add_assignment_form()

            with col2:
                with st.expander("&#x1F4DD; Modify or Delete Assignments", expanded=True):
                    self._render_modify_assignment_form()

            with col3:
                with st.expander("&#x1F5D1;&#xFE0F; Delete Assignment", expanded=True):
                    self._render_delete_assignment_form()

        st.divider()

        # Settings Section
        with st.container():
            st.markdown("### &#x2699; Settings")
            with st.expander("&#x1F3AF; Set Total Marks", expanded=True):
                self._render_set_total_mark_form()

    def _render_analytics_tab(self) -> None:
        """Render analytics tab with calculations."""
        selected_subject = st.session_state.get("selected_subject")
        if selected_subject:
            self._render_exam_calculator(selected_subject)
            self._render_grade_summary(selected_subject)

    def _render_add_subject_form(self) -> None:
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

    def _render_delete_subject_form(self) -> None:
        """Render delete subject form."""
        subjects = self.controller.available_subjects
        if subjects:
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

    def _render_add_assignment_form(self) -> None:
        """Render add assignment form."""
        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            st.info("Select a subject first")
            return

        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        with st.form(f"add_assignment_form_{subject_code}"):
            assessment = st.text_input("Assessment Name")

            # Use text input to allow S/U grades
            weighted_mark_input = st.text_input(
                "Weighted Mark",
                placeholder=f"Enter number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}'",
                help=f"Enter a numeric value for graded assignments, or '{GradeType.SATISFACTORY.value}' for Satisfactory, '{GradeType.UNSATISFACTORY.value}' for Unsatisfactory",
            )

            # Conditionally show mark weight input
            mark_weight = None
            if weighted_mark_input.upper() not in [GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value]:
                mark_weight = st.number_input("Mark Weight", min_value=0.0, max_value=100.0)
            else:
                st.info(f"Mark weight is not applicable for {weighted_mark_input.upper()} grades")

            if st.form_submit_button("Add Assignment"):
                if not assessment or not weighted_mark_input:
                    st.error("Assessment name and weighted mark are required")
                    return

                success, message = add_assignment(
                    self.controller.semester_obj, subject_code, assessment, weighted_mark_input, mark_weight
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.warning(message)

    def _render_delete_assignment_form(self) -> None:
        """Render delete assignment form."""
        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            st.info("Select a subject first")
            return

        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject or not subject.assignments:
            st.info("No assignments to delete.")
            return

        assessments = [a.subject_assessment for a in subject.assignments]

        with st.form(f"delete_assignment_form_{subject_code}"):
            del_assessment = st.selectbox("Select Assessment to Delete", assessments)

            if st.form_submit_button("Delete Assignment", type="secondary"):
                success, message = delete_assignment(self.controller.semester_obj, subject_code, del_assessment)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.warning(message)

    def _render_modify_assignment_form(self) -> None:
        """Render modify assignment form."""
        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            st.info("Select a subject first")
            return

        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject or not subject.assignments:
            st.info("No assignments to modify.")
            return

        assessments = [a.subject_assessment for a in subject.assignments]

        with st.form(f"modify_assignment_form_{subject_code}"):
            # Select assignment to modify
            selected_assessment = st.selectbox("Select Assignment to Modify", assessments)

            # Get current assignment data
            current_assignment = None
            for assignment in subject.assignments:
                if assignment.subject_assessment == selected_assessment:
                    current_assignment = assignment
                    break

            if current_assignment:
                # Show current values and allow modification
                st.markdown(f"**Modifying: {selected_assessment}**")

                col1, col2 = st.columns(2)

                with col1:
                    new_assessment_name = st.text_input(
                        "New Assessment Name",
                        value=current_assignment.subject_assessment,
                        help="Change the assessment name",
                    )

                    # Handle S/U vs numeric grades
                    current_mark = current_assignment.weighted_mark
                    if isinstance(current_mark, str):
                        default_mark = current_mark
                    else:
                        default_mark = str(current_mark)

                    new_weighted_mark = st.text_input(
                        "New Weighted Mark",
                        value=default_mark,
                        placeholder=f"Enter number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}'",
                        help=f"Enter a numeric value for graded assignments, or '{GradeType.SATISFACTORY.value}' for Satisfactory, '{GradeType.UNSATISFACTORY.value}' for Unsatisfactory",
                    )

                with col2:
                    # Conditionally show mark weight input
                    current_weight = current_assignment.mark_weight or 0.0
                    new_mark_weight = None

                    if new_weighted_mark.upper() not in [GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value]:
                        new_mark_weight = st.number_input(
                            "New Mark Weight",
                            min_value=0.0,
                            max_value=100.0,
                            value=current_weight,
                            help="Weight of this assignment",
                        )
                    else:
                        st.info(f"Mark weight is not applicable for {new_weighted_mark.upper()} grades")

                    # Show what's changing
                    st.markdown("**Changes:**")
                    if new_assessment_name != current_assignment.subject_assessment:
                        st.write(f"• Name: {current_assignment.subject_assessment} → {new_assessment_name}")
                    if str(new_weighted_mark) != str(current_assignment.weighted_mark):
                        st.write(f"• Mark: {current_assignment.weighted_mark} → {new_weighted_mark}")
                    if new_mark_weight != current_assignment.mark_weight:
                        st.write(f"• Weight: {current_assignment.mark_weight} → {new_mark_weight}")

                if st.form_submit_button("Modify Assignment", type="primary"):
                    if not new_assessment_name or not new_weighted_mark:
                        st.error("Assessment name and weighted mark are required")
                        return

                    from controller import modify_assignment

                    success, message = modify_assignment(
                        self.controller.semester_obj,
                        subject_code,
                        selected_assessment,
                        new_assessment_name,
                        new_weighted_mark,
                        new_mark_weight,
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.warning(message)

    def _render_exam_calculator(self, subject_code: str) -> None:
        """Simple exam mark calculator that calculates from total mark."""
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.subheader(f"Exam Calculator for {subject_code}")

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject:
            st.error("Subject not found.")
            return

        # Show current summary
        assignment_total = sum(
            a.weighted_mark for a in subject.assignments if isinstance(a.weighted_mark, (float, int))
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Mark", f"{subject.total_mark:.1f}")
        with col2:
            st.metric("Assignment Total", f"{assignment_total:.1f}")
        with col3:
            # Simple calculation for display
            calculated_exam = subject.total_mark - assignment_total
            st.metric("Calculated Exam", f"{calculated_exam:.1f}")

        # Show the simple formula
        st.info(
            f"**Formula:** Exam Mark = Total Mark - Assignment Total = {subject.total_mark} - {assignment_total} = {calculated_exam:.1f}"
        )

        # Calculate and save button
        if st.button("Calculate & Save Exam Mark", type="primary"):
            calculated_mark = self.controller.semester_obj.calculate_exam_mark(subject_code)
            if calculated_mark is not None:
                st.success(f"Exam mark saved: {calculated_mark:.2f}")
                st.rerun()
            else:
                st.error("Cannot calculate exam mark.")

    def _render_grade_summary(self, subject_code: str) -> None:
        """Render grade summary for subject."""
        if not self.controller.semester_obj:
            return

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject:
            return

        st.subheader(f"Grade Summary for {subject_code}")

        # Count different grade types
        numeric_assignments = len([a for a in subject.assignments if a.grade_type == GradeType.NUMERIC])
        satisfactory_assignments = len([a for a in subject.assignments if a.grade_type == GradeType.SATISFACTORY])
        unsatisfactory_assignments = len([a for a in subject.assignments if a.grade_type == GradeType.UNSATISFACTORY])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Numeric Assignments", numeric_assignments)
        with col2:
            st.metric("Satisfactory Assignments", satisfactory_assignments)
        with col3:
            st.metric("Unsatisfactory Assignments", unsatisfactory_assignments)

    def _render_set_total_mark_form(self) -> None:
        """Render set total mark form."""
        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            return

        if not self.controller.semester_obj or not self.controller.data_persistence:
            st.error("Controller not properly initialized.")
            return

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject:
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
                    from controller import set_total_mark

                    success, message = set_total_mark(subject, new_total_mark, self.controller.data_persistence)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
