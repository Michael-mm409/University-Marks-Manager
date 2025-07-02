# src/view/components/forms/assignment_forms.py
"""Assignment management form components."""

import streamlit as st

from controller import add_assignment, delete_assignment, modify_assignment
from controller.app_controller import AppController
from model.enums import GradeType


class AssignmentForms:
    """Handles assignment-related form components."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render_add_form(self) -> None:
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

            weighted_mark_input = st.text_input(
                "Weighted Mark",
                placeholder=f"Enter number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}'",
                help=f"Enter a numeric value for graded assignments, or '{GradeType.SATISFACTORY.value}' for Satisfactory, '{GradeType.UNSATISFACTORY.value}' for Unsatisfactory",
            )

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

    def render_modify_form(self) -> None:
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

    def render_delete_form(self) -> None:
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
