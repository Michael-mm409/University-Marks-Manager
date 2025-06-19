from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

from controller.entry_logic import add_assignment, delete_assignment
from controller.subject_logic import add_subject, delete_subject, set_total_mark
from model.data_persistence import DataPersistence
from model.models import Assignment, Examination, Subject
from model.semester import Semester

if TYPE_CHECKING:
    from main import App


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def render_main_page(app: "App"):
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
                    success, message = set_total_mark(subject, total_mark, data_persistence)
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
                weighted_mark = st.number_input(
                    "Weighted Mark",
                    min_value=0.0,
                    value=selected_data["weighted_mark"],
                    key=f"add_weighted_mark_{subject_code}_{selected_idx}",
                )
                mark_weight = st.number_input(
                    "Mark Weight",
                    min_value=0.0,
                    value=selected_data["mark_weight"],
                    key=f"add_mark_weight_{subject_code}_{selected_idx}",
                )
                if st.button("Add Assignment", key=f"add_assignment_btn_{subject_code}_{selected_idx}"):
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


def build_tables_per_subject(sem_obj, data_persistence):
    subjects = get_all_subjects(sem_obj, data_persistence)

    # Now sort all subject codes (current + synced)
    for subject_code in sorted(subjects.keys()):
        subject = subjects[subject_code]
        st.subheader(
            f"{subject.subject_name} ({subject_code})"
            f"{' - Synced' if getattr(subject, 'sync_subject', False) else ''} "
            f"in {sem_obj.name} {sem_obj.year}"
        )
        rows = []
        for entry in subject.assignments:
            rows.append(
                [
                    entry.subject_assessment,
                    entry.unweighted_mark,
                    entry.weighted_mark,
                    entry.mark_weight,
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


def get_all_subjects(sem_obj, data_persistence):
    """Retrieve all subjects for the given semester, including synced subjects from other semesters."""
    subjects = dict(sem_obj.subjects)  # Start with current semester's subjects

    # Add synced subjects from other semesters
    for sem_name, sem_data in data_persistence.data.items():
        if sem_name == sem_obj.name:
            continue
        for subj_code, subj in sem_data.items():
            is_synced = False
            if isinstance(subj, dict):
                is_synced = subj.get("sync_subject", False)
            elif hasattr(subj, "sync_subject"):
                is_synced = subj.sync_subject
            if is_synced and subj_code not in subjects:
                if isinstance(subj, dict):
                    assignments = [Assignment(**a) for a in subj["assignments"]] if "assignments" in subj else []
                    examinations = Examination(**subj.get("examinations", {})) if "examinations" in subj else None
                    subject = Subject(
                        subject_code=subj_code,
                        subject_name=subj.get("subject_name", "N/A"),
                        assignments=assignments,
                        total_mark=subj.get("total_mark", 0.0),
                        examinations=examinations or Examination(exam_mark=0, exam_weight=100),
                        sync_subject=True,
                    )
                else:
                    subject = subj
                subjects[subj_code] = subject

    return subjects


def get_summary(subject):
    """Calculate the summary values for a subject."""
    total_weighted_mark = sum(
        entry.weighted_mark for entry in subject.assignments if isinstance(entry.weighted_mark, (int, float))
    )
    total_weight = sum(
        entry.mark_weight for entry in subject.assignments if isinstance(entry.mark_weight, (int, float))
    )
    exam_mark = subject.examinations.exam_mark if subject.examinations else 0
    exam_weight = subject.examinations.exam_weight if subject.examinations else 100
    total_mark = subject.total_mark

    return total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark
