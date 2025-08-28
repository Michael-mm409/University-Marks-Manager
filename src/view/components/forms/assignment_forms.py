"""
Assignment management form components.

This module defines the `AssignmentForms` class, which renders forms in the Streamlit UI
to support the addition, modification, and deletion of assignments tied to a subject
within a semester. The forms validate user input, call controller methods, and provide
feedback messages based on operation success or failure.

Forms include:
    - Add Assignment Form
    - Modify Assignment Form
    - Delete Assignment Form

Dependencies:
    - streamlit
    - controller (add_assignment, modify_assignment, delete_assignment)
    - AppController
    - GradeType (enum representing SATISFACTORY/UNSATISFACTORY grades)
"""

import streamlit as st

from controller import AppController, ExamController, add_assignment, delete_assignment, modify_assignment
from model import GradeType


class AssignmentForms:
    """
    Handles Streamlit form rendering for managing assignments.

    Attributes:
        controller (AppController): Instance of the application controller used
            to access the current semester and perform assignment operations.
    """

    def __init__(self, controller: AppController):
        """
        Initialize the AssignmentForms component with an AppController.

        Args:
            controller (AppController): Controller instance for accessing app state.
        """

        self.controller = controller

    def render_add_form(self) -> None:
        """
        Render the form for adding a new assignment to the selected subject.

        Displays input fields for:
            - Assessment name
            - Weighted mark (numeric or S/U)
            - Mark weight (if applicable)

        On submission, validates the input and calls `add_assignment()` from the controller.
        Displays success, error, or warning messages based on operation outcome.
        """

        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            st.info("Select a subject first")
            return

        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        fb_key = f"assignment_add_feedback_{subject_code}"
        if fb := st.session_state.get(fb_key):
            st.success(fb)
            if st.button("Dismiss", key=f"dismiss_{fb_key}", type="secondary"):
                st.session_state.pop(fb_key, None)
                st.rerun()

        with st.form(f"add_assignment_form_{subject_code}"):
            assessment = st.text_input("Assessment Name")

            weighted_mark_input = st.text_input(
                "Weighted Mark",
                placeholder=f"Enter number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}'",
                help=f"Enter a numeric value for graded assignments, or "
                f"'{GradeType.SATISFACTORY.value}' for Satisfactory, "
                f"'{GradeType.UNSATISFACTORY.value}' for Unsatisfactory",
            )

            mark_weight = None
            if weighted_mark_input.upper() not in [GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value]:
                mark_weight = st.number_input("Mark Weight", min_value=0.0, max_value=100.0)
            else:
                st.info(f"Mark weight is not applicable for {weighted_mark_input.upper()} grades")

            if st.form_submit_button("Add Assignment"):
                if not assessment:
                    st.error("Assessment name is required")
                    return
                # If weighted_mark_input is empty, treat as zero
                if not weighted_mark_input:
                    weighted_mark_input = 0

                success, message = add_assignment(
                    self.controller.semester_obj, subject_code, assessment, weighted_mark_input, mark_weight
                )
                if success:
                    # Use ExamController to update exam weight after adding assignment
                    try:
                        exam_controller = ExamController(self.controller)
                        exam_controller.auto_calculate_exam(subject_code)
                    except Exception:
                        pass
                    st.session_state[fb_key] = message
                    st.rerun()
                else:
                    st.warning(message)

    def render_modify_form(self) -> None:
        """
        Render the form for modifying an existing assignment.

        Allows the user to:
            - Select an assignment
            - Change its name, mark, or weight

        Handles both numeric and non-numeric (S/U) grading.
        On form submission, it calls `modify_assignment()` and displays feedback.
        """

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

        # Select assignment to modify OUTSIDE the form so it updates dynamically
        selected_assessment = st.selectbox(
            "Select Assignment to Modify", assessments, key=f"modify_select_{subject_code}"
        )

        # Get current assignment data
        current_assignment = None
        for assignment in subject.assignments:
            if assignment.subject_assessment == selected_assessment:
                current_assignment = assignment
                break

        if current_assignment:
            mod_fb_key = f"assignment_modify_feedback_{subject_code}"
            if mfb := st.session_state.get(mod_fb_key):
                st.success(mfb)
                if st.button("Dismiss", key=f"dismiss_{mod_fb_key}", type="secondary"):
                    st.session_state.pop(mod_fb_key, None)
                    st.rerun()
            # Show current values clearly
            st.markdown(f"**Currently Modifying: {selected_assessment}**")

            # Compact info box for current assignment
            st.info(
                f"**Currently Modifying:** `{selected_assessment}`  \n"
                f"**Name:** `{current_assignment.subject_assessment}` &nbsp; | &nbsp; "
                f"**Mark:** `{current_assignment.weighted_mark}` &nbsp; | &nbsp; "
                f"**Weight:** `{current_assignment.mark_weight}`"
            )

            with st.form(f"modify_assignment_form_{subject_code}_{selected_assessment}"):
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
                        placeholder=f"Enter number, '{GradeType.SATISFACTORY.value}', "
                        f"or '{GradeType.UNSATISFACTORY.value}'",
                        help=f"Enter a numeric value for graded assignments, or "
                        f"'{GradeType.SATISFACTORY.value}' for Satisfactory, "
                        f"'{GradeType.UNSATISFACTORY.value}' for Unsatisfactory",
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
                    st.markdown("**Changes Preview:**")
                    changes_made = False
                    if new_assessment_name != current_assignment.subject_assessment:
                        st.write(f"• Name: {current_assignment.subject_assessment} → {new_assessment_name}")
                        changes_made = True
                    if str(new_weighted_mark) != str(current_assignment.weighted_mark):
                        st.write(f"• Mark: {current_assignment.weighted_mark} → {new_weighted_mark}")
                        changes_made = True
                    if new_mark_weight != current_assignment.mark_weight:
                        st.write(f"• Weight: {current_assignment.mark_weight} → {new_mark_weight}")
                        changes_made = True

                    if not changes_made:
                        st.write("No changes detected")

                if st.form_submit_button("Modify Assignment", type="primary"):
                    if not new_assessment_name:
                        st.error("Assessment name is required")
                        return
                    # If new_weighted_mark is empty, treat as zero
                    if not new_weighted_mark:
                        new_weighted_mark = 0

                    success, message = modify_assignment(
                        self.controller.semester_obj,
                        subject_code,
                        selected_assessment,  # Use the original assessment name as the identifier
                        new_assessment_name,
                        new_weighted_mark,
                        new_mark_weight,
                    )
                    if success:
                        # Use ExamController to update exam weight after modifying assignment
                        try:
                            exam_controller = ExamController(self.controller)
                            exam_controller.auto_calculate_exam(subject_code)
                        except Exception as exception:
                            st.error(f"Error updating exam: {str(exception)}")
                            return
                        st.session_state[mod_fb_key] = message
                        st.rerun()
                    else:
                        st.warning(message)
        else:
            st.error("Could not find the selected assignment. Please try again.")

    def render_delete_form(self) -> None:
        """
        Render the form for deleting an existing assignment.

        Prompts the user to select an assignment from the current subject and delete it.

        On confirmation, it calls `delete_assignment()` and shows a success or warning message.
        """
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

        del_fb_key = f"assignment_delete_feedback_{subject_code}"
        if dfb := st.session_state.get(del_fb_key):
            st.success(dfb)
            if st.button("Dismiss", key=f"dismiss_{del_fb_key}", type="secondary"):
                st.session_state.pop(del_fb_key, None)
                st.rerun()

        with st.form(f"delete_assignment_form_{subject_code}"):
            del_assessment = st.selectbox("Select Assessment to Delete", assessments)

            if st.form_submit_button("Delete Assignment", type="secondary"):
                success, message = delete_assignment(self.controller.semester_obj, subject_code, del_assessment)
                if success:
                    # Use ExamController to update exam weight after deleting assignment
                    try:
                        exam_controller = ExamController(self.controller)
                        exam_controller.auto_calculate_exam(subject_code)
                    except Exception:
                        pass
                    st.session_state[del_fb_key] = message
                    st.rerun()
                else:
                    st.warning(message)
