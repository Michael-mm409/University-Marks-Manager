from typing import TYPE_CHECKING, Dict, List, Optional, Union

import pandas as pd
import streamlit as st

from application.entry_logic import add_assignment, delete_assignment
from application.subject_logic import add_subject, delete_subject, set_total_mark
from application.table_logic import get_all_subjects, get_summary
from domain import DataPersistence, Semester
from domain.enums import GradeType
from domain.models import Assignment, Subject

# If you created the types file:
# from model.types import SubjectDict, AssignmentDict

if TYPE_CHECKING:
    from main import App


def safe_float(val) -> Optional[float]:
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


def render_main_page(app: "App") -> None:
    """
    Render the main page of the University Marks Manager application using Streamlit.
    This function sets up the layout and user interface for managing university subjects,
    assignments, and marks. It provides functionality for adding, deleting, and updating
    subjects and assignments, as well as calculating exam marks and displaying data in a
    tabular format.
    Args:
        app (App): The main application object containing the semester data, persistence
                   layer, and current subject/semester context.
    Streamlit Components:
        - Page Configuration: Sets the page title, layout, and icon.
        - Subject Management:
            - Add New Subject: Allows users to add a new subject with a code, name, and
              optional synchronization.
            - Delete Subject: Enables users to delete the currently selected subject.
            - Set Total Mark: Allows users to set the total mark for a selected subject.
        - Assignment Management:
            - Add Assignment: Provides functionality to add a new assignment to a subject.
            - Delete Assignment: Enables users to delete an assignment from a subject.
            - Calculate Exam Mark: Calculates and displays the exam mark for a subject.
        - Display Table: Displays a table of subjects and their assessments for the
          selected semester and year.
    Notes:
        - The function uses Streamlit's layout components (e.g., columns, expanders) to
          organize the UI.
        - Users are advised to refresh the page after adding or deleting subjects or
          assignments to see the updates in the displayed table.
    Dependencies:
        - Streamlit (st): Used for building the user interface.
        - Semester: Represents the semester object containing subjects and assignments.
        - DataPersistence: Handles data persistence for subjects and assignments.
        - Helper functions (e.g., add_subject, delete_subject, set_total_mark, add_assignment,
          delete_assignment, build_tables_per_subject) are used for performing specific
          operations.
    """
    st.set_page_config(page_title="University Marks Manager", layout="wide", page_icon="assets/app_icon.ico")
    st.title("University Marks Manager (Streamlit Edition)")

    sem_obj: Semester = app.sem_obj
    data_persistence: DataPersistence = app.data_persistence
    subject_code: str | None = app.subject_code
    year: str = app.year
    semester: str | None = app.semester

    col1, col2, col3 = st.columns(3)

    # --- Subject Name Input ---
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander("Add New Subject"):
            new_code = st.text_input("Subject Code", key="add_subject_code")
            new_name = st.text_input("Subject Name", key="add_subject_name")
            sync_subject = st.checkbox("Sync Subject", key="add_sync_subject")
            if st.button("Add Subject"):
                success, message = add_subject(sem_obj, new_code, new_name, sync_subject)
                if success:
                    st.success(message)
                else:
                    st.warning(message)
    with col2:
        with st.expander("Delete Subject"):
            if st.button("Delete Subject", key="delete_subject_btn"):
                success, message = delete_subject(sem_obj, subject_code)
                if success:
                    st.success(message)
                else:
                    st.warning(message)

    with col3:
        subject = sem_obj.subjects.get(subject_code) if subject_code else None
        if subject_code:
            with st.expander(f"Set Total Mark for {subject_code}"):
                total_mark = st.number_input(
                    "Total Mark", min_value=0.0, value=subject.total_mark if subject else 0.0, key="set_total_mark"
                )
                if st.button("Set Total Mark", key="set_total_mark_btn"):
                    if subject is not None:
                        success, message = set_total_mark(subject, total_mark, data_persistence)
                    else:
                        st.warning("No subject selected. Please select a valid subject.")
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)

    # --- Assignment Management ---
    col1, col2, col3 = st.columns(3)
    with col1:
        if subject_code:
            with st.expander(f"Add Assignment to {subject_code}"):
                select_key = f"select_row_{subject_code}"
                selected_idx = st.session_state.get(select_key, 0)
                subject = sem_obj.subjects.get(subject_code)
                assignments = subject.assignments if subject else []
                if assignments and 0 <= selected_idx < len(assignments):
                    selected_assignment = assignments[selected_idx]
                    selected_data = {
                        "assessment": selected_assignment.subject_assessment,
                        "weighted_mark": safe_float(selected_assignment.weighted_mark),
                        "mark_weight": safe_float(selected_assignment.mark_weight),
                    }
                else:
                    selected_data = {"assessment": "", "weighted_mark": 0.0, "mark_weight": 0.0}

                assessment = st.text_input(
                    "Assessment Name",
                    value=selected_data["assessment"],
                    key=f"add_assessment_{subject_code}_{selected_idx}",
                )

                # Replace the number_input with text_input to allow S/U
                weighted_mark_input = st.text_input(
                    "Weighted Mark",
                    value=safe_display_value(selected_data["weighted_mark"]),
                    placeholder=f"Enter number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}'",
                    help=f"Enter a numeric value for graded assignments, or '{GradeType.SATISFACTORY.value}' for Satisfactory, '{GradeType.UNSATISFACTORY.value}' for Unsatisfactory",
                    key=f"add_weighted_mark_{subject_code}_{selected_idx}",
                )

                # Conditionally show mark weight input based on grade type
                if weighted_mark_input.upper() in [GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value]:
                    st.info(f"Mark weight is not applicable for {weighted_mark_input.upper()} grades")
                    mark_weight = None
                else:
                    mark_weight = st.number_input(
                        "Mark Weight",
                        min_value=0.0,
                        value=selected_data["mark_weight"] if selected_data["mark_weight"] is not None else 0.0,
                        key=f"add_mark_weight_{subject_code}_{selected_idx}",
                    )

                if st.button("Add Assignment", key=f"add_assignment_btn_{subject_code}_{selected_idx}"):
                    # Convert weighted_mark_input to appropriate type using enums
                    if weighted_mark_input.upper() == GradeType.SATISFACTORY.value:
                        weighted_mark = GradeType.SATISFACTORY.value
                    elif weighted_mark_input.upper() == GradeType.UNSATISFACTORY.value:
                        weighted_mark = GradeType.UNSATISFACTORY.value
                    else:
                        try:
                            weighted_mark = float(weighted_mark_input)
                        except ValueError:
                            st.error(
                                f"Please enter a valid number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}' for weighted mark"
                            )
                            st.stop()

                    success, message = add_assignment(sem_obj, subject_code, assessment, weighted_mark, mark_weight)
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)

    with col2:
        if subject_code:
            assessments = [a.subject_assessment for a in subject.assignments] if subject else []
            with st.expander(f"Delete Assignment from {subject_code}"):
                del_assessment = (
                    st.selectbox("Select Assessment to Delete", assessments, key="del_assessment")
                    if assessments
                    else None
                )
                if st.button("Delete Assignment", key="del_assignment_btn") and del_assessment:
                    success, message = delete_assignment(sem_obj, subject_code, del_assessment)
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)

    with col3:
        if subject_code:
            with st.expander(f"Calculate Exam Mark for {subject_code}"):
                if st.button("Calculate Exam Mark", key="calc_exam_mark_btn"):
                    exam_mark = sem_obj.calculate_exam_mark(subject_code)
                    if exam_mark is not None:
                        st.info(f"Exam mark for {subject_code}: {exam_mark}")
                    else:
                        st.warning("Could not calculate exam mark.")

    # --- Display Table ---
    st.header(f"Subjects and Assessments for {semester} {year}")
    build_tables_per_subject(sem_obj, data_persistence)
    st.caption("Tip: Refresh the page after adding or deleting subjects/assignments to see updates.")


def build_tables_per_subject(sem_obj: Semester, data_persistence: DataPersistence) -> None:
    """
    Builds and displays tables for each subject in a given semester object.
    This function retrieves all subjects associated with the given semester object,
    sorts them by their subject codes, and displays their assignment details in
    tabular format using Streamlit. It also allows users to select specific assignments
    via radio buttons and stores the selected assignment details in the Streamlit
    session state.
    Args:
        sem_obj (Semester): The semester object containing information about the semester
                          (e.g., name, year).
        data_persistence (DataPersistence): The data persistence layer used to retrieve subject
                                   and assignment data.
    Functionality:
        - Retrieves all subjects for the given semester.
        - Displays assignment details for each subject in a table.
        - Allows users to select an assignment using radio buttons.
        - Stores the selected assignment details in Streamlit session state.
        - Displays a summary of total weighted marks, total weight, exam marks, and
          total marks for each subject.
    Session State Keys:
        - `select_row_<subject_code>`: Stores the index of the selected assignment row
          for each subject.
        - `selected_assignment_<subject_code>`: Stores details of the selected assignment
          for each subject, including assessment name, weighted mark, and mark weight.
    Notes:
        - If no assignments are available for a subject, the radio buttons and table
          are disabled.
        - The summary row is displayed as a markdown section below each subject's table.
    Dependencies:
        - Requires the `get_all_subjects`, `safe_float`, and `get_summary` helper functions.
        - Uses the `pandas` library for creating and manipulating dataframes.
        - Relies on the `streamlit` library for UI rendering.
    """
    subjects: Dict[str, Subject] = get_all_subjects(sem_obj, data_persistence)

    # Now sort all subject codes (current + synced)
    for subject_code in sorted(subjects.keys()):
        subject: Subject = subjects[subject_code]
        st.subheader(
            f"{subject.subject_name} ({subject_code})"
            f"{' - Synced' if getattr(subject, 'sync_subject', False) else ''} "
            f"in {sem_obj.name} {sem_obj.year}"
        )

        rows: List[List[Union[str, float, None]]] = []
        assignment: Assignment
        for assignment in subject.assignments:
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

        selected_idx = (
            st.radio(
                f"**Select an assignment for {subject_code}**",
                options=range(len(df)),
                format_func=lambda i: df.iloc[i]["Assessment"],
                key=select_key,
                index=st.session_state[select_key] if len(df) > 0 else None,
                horizontal=True,  # if len(df) <= 5 else False,
                disabled=(len(df) == 0),
            )
            if len(df) > 0
            else None
        )

        # Update session state if changed
        if selected_idx is not None and st.session_state[select_key] != selected_idx:
            st.session_state[select_key] = selected_idx

        st.dataframe(df.reset_index(drop=True), use_container_width=True, key=f"summary_editor_{subject_code}")

        # --- Store the selected assignment in session state ---
        if selected_idx is not None and len(df) > 0:
            selected_assignment = df.iloc[selected_idx]
            st.session_state[f"selected_assignment_{subject_code}"] = {
                "assessment": selected_assignment["Assessment"],
                "weighted_mark": safe_float(selected_assignment["Weighted Mark"]),
                "mark_weight": safe_float(selected_assignment["Mark Weight"]),
            }
        else:
            st.session_state[f"selected_assignment_{subject_code}"] = None

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
