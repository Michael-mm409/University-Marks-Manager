from datetime import datetime

import pandas as pd
import streamlit as st

from model.data_persistence import DataPersistence
from model.models import Assignment, Examination, Subject
from model.semester import Semester


def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


# --- Streamlit UI ---

st.set_page_config(page_title="University Marks Manager", layout="wide", page_icon="assets/app_icon.ico")
st.title("University Marks Manager (Streamlit Edition)")
col1, col2, col3 = st.columns(3)

# --- Year Selection ---
years = [str(y) for y in range(datetime.now().year - 2, datetime.now().year + 3)]
with col1:
    year = st.selectbox("Select Year", years, index=years.index(str(datetime.now().year)))

data_persistence = DataPersistence(year)

# --- Semester Selection ---
semester_names = list(data_persistence.data.keys()) or ["Autumn", "Spring", "Annual"]
with col2:
    semester = st.selectbox("Select Semester", semester_names, index=0)
sem_obj = Semester(semester or "Autumn", year, data_persistence)

# --- Subject Selection ---
subject_codes = list(sem_obj.subjects.keys())

# Add synced subjects from other semesters
for sem_name, sem_data in data_persistence.data.items():
    if sem_name == semester:
        continue  # Skip the current semester
    for subject_code, subject in sem_data.items():
        if isinstance(subject, dict) and subject.get("sync_subject", False):
            if subject_code not in subject_codes:
                subject_codes.append(subject_code)

subject_codes = sorted(subject_codes)  # <-- Sort subject codes here

with col3:
    subject_code = st.selectbox("Select Subject", subject_codes) if subject_codes else None

# --- Subject Name Input ---
col1, col2, col3 = st.columns(3)

with col1:
    # --- Add Subject ---
    with st.expander("Add New Subject"):
        new_code = st.text_input("Subject Code", key="add_subject_code")
        new_name = st.text_input("Subject Name", key="add_subject_name")
        sync_subject = st.checkbox("Sync Subject", key="add_sync_subject")
        if st.button("Add Subject"):
            if not new_code or not new_name:
                st.warning("Subject code and name cannot be empty.")
            elif new_code in sem_obj.subjects:
                st.warning("Subject code already exists.")
            else:
                sem_obj.add_subject(new_code, new_name, sync_subject=sync_subject)
                st.success(f"Added subject {new_code}. Please refresh the page to see it.")

with col2:
    # --- Delete Subject ---
    with st.expander("Delete Subject"):
        del_code = (
            st.selectbox("Select Subject to Delete", subject_codes, key="del_subject_code") if subject_codes else None
        )
        if st.button("Delete Subject", key="del_subject_btn") and del_code:
            sem_obj.delete_subject(del_code)
            st.success(f"Deleted subject {del_code}. Please refresh the page to see changes.")

with col3:
    subject = sem_obj.subjects.get(subject_code) if subject_code else None
    # --- Set Total Mark ---
    if subject_code:
        with st.expander(f"Set Total Mark for {subject_code}"):
            total_mark = st.number_input(
                "Total Mark", min_value=0.0, value=subject.total_mark if subject else 0.0, key="set_total_mark"
            )
            if st.button("Set Total Mark", key="set_total_mark_btn"):
                if subject is not None:
                    subject.total_mark = total_mark
                else:
                    st.warning(f"Subject '{subject_code}' not found.")
                data_persistence.save_data(data_persistence.data)
                st.success(f"Total Mark for '{subject_code}' set to {total_mark}.")

col1, col2, col3 = st.columns(3)
with col1:
    # --- Add Assignment ---
    if subject_code:
        with st.expander(f"Add Assignment to {subject_code}"):
            # Get the selected assignment index for this subject
            select_key = f"select_row_{subject_code}"
            selected_idx = st.session_state.get(select_key, 0)
            # Get the assignments for this subject
            subject = sem_obj.subjects.get(subject_code)
            assignments = subject.assignments if subject else []
            # Get the selected assignment data
            if assignments and 0 <= selected_idx < len(assignments):
                selected_assignment = assignments[selected_idx]
                selected_data = {
                    "assessment": selected_assignment.subject_assessment,
                    "weighted_mark": safe_float(selected_assignment.weighted_mark),
                    "mark_weight": safe_float(selected_assignment.mark_weight),
                }
            else:
                selected_data = {"assessment": "", "weighted_mark": 0.0, "mark_weight": 0.0}

            # Use keys that depend on the selected assignment to force Streamlit to update values
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
                if not assessment:
                    st.warning("Assessment name cannot be empty.")
                else:
                    sem_obj.add_entry(
                        subject_code=subject_code,
                        subject_assessment=assessment,
                        weighted_mark=weighted_mark,
                        unweighted_mark=round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0,
                        mark_weight=mark_weight,
                        grade_type="numeric",
                    )
                    st.success(f"Added assignment '{assessment}' to {subject_code}. Please refresh the page to see it.")

with col2:
    # --- Delete Assignment ---
    if subject_code:
        assessments = [a.subject_assessment for a in subject.assignments] if subject else []
        with st.expander(f"Delete Assignment from {subject_code}"):
            del_assessment = (
                st.selectbox("Select Assessment to Delete", assessments, key="del_assessment") if assessments else None
            )
            if st.button("Delete Assignment", key="del_assignment_btn") and del_assessment:
                sem_obj.delete_entry(subject_code, del_assessment)
                st.success(
                    f"Deleted assessment '{del_assessment}' from {subject_code}. Please refresh the page to see changes."
                )

# --- Calculate Exam Mark ---
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
def build_table(sem_obj):
    all_rows = []
    # Add subjects from current semester
    for subject_code, subject in sem_obj.subjects.items():
        subject_name = subject.subject_name
        total_mark = subject.total_mark
        for entry in subject.assignments:
            all_rows.append(
                [
                    subject_code,
                    subject_name,
                    entry.subject_assessment,
                    entry.unweighted_mark,
                    entry.weighted_mark,
                    entry.mark_weight,
                    total_mark,
                ]
            )
        # Summary row
        total_weighted_mark = sum(
            entry.weighted_mark for entry in subject.assignments if isinstance(entry.weighted_mark, (int, float))
        )
        total_weight = sum(
            entry.mark_weight for entry in subject.assignments if isinstance(entry.mark_weight, (int, float))
        )
        exam_mark = subject.examinations.exam_mark if subject.examinations else 0
        exam_weight = subject.examinations.exam_weight if subject.examinations else 100
        all_rows.append(
            [
                f"Summary for {subject_code}",
                f"Assessments: {len(subject.assignments)}",
                f"Total Weighted: {total_weighted_mark:.2f}",
                f"Total Weight: {total_weight:.0f}%",
                f"Exam Mark: {exam_mark:.2f}",
                f"Exam Weight: {exam_weight:.0f}%",
                f"Total Mark: {total_mark:.0f}",
            ]
        )
        # Separator row
        all_rows.append(["-----"] * 7)
    # Add synced subjects from other semesters
    for sem_name, sem_data in data_persistence.data.items():
        if sem_name == sem_obj.name:
            continue
        for subj_code, subj in sem_data.items():
            is_synced = False
            if isinstance(subject, dict):
                is_synced = subj.get("sync_subject", False)
            elif hasattr(subj, "sync_subject"):
                is_synced = subj.sync_subject

            if is_synced and subj_code not in sem_obj.subjects:
                # subj is a Subject object
                assignments = subj.assignments if hasattr(subj, "assignments") else []
                examinations = subj.examinations if hasattr(subj, "examinations") else None
                subject = Subject(
                    subject_code=subj_code,
                    subject_name=subj.subject_name if hasattr(subj, "subject_name") else "N/A",
                    assignments=assignments,
                    total_mark=subj.total_mark if hasattr(subj, "total_mark") else 0.0,
                    examinations=examinations or Examination(exam_mark=0, exam_weight=100),
                    sync_subject=True,
                )
                subject_name = subject.subject_name
                total_mark = subject.total_mark
                for entry in subject.assignments:
                    all_rows.append(
                        [
                            subj_code,
                            subject_name,
                            entry.subject_assessment,
                            entry.unweighted_mark,
                            entry.weighted_mark,
                            entry.mark_weight,
                            total_mark,
                        ]
                    )
                # Summary row
                total_weighted_mark = sum(
                    entry.weighted_mark
                    for entry in subject.assignments
                    if isinstance(entry.weighted_mark, (int, float))
                )
                total_weight = sum(
                    entry.mark_weight for entry in subject.assignments if isinstance(entry.mark_weight, (int, float))
                )
                exam_mark = subject.examinations.exam_mark if subject.examinations else 0
                exam_weight = subject.examinations.exam_weight if subject.examinations else 100
                all_rows.append(
                    [
                        f"Summary for {subj_code}",
                        f"Assessments: {len(subject.assignments)}",
                        f"Total Weighted: {total_weighted_mark:.2f}",
                        f"Total Weight: {total_weight:.0f}%",
                        f"Total Mark: {total_mark:.0f}",
                        f"Exam Mark: {exam_mark:.2f}",
                        f"Exam Weight: {exam_weight:.0f}%",
                    ]
                )
                # Separator row
                all_rows.append(["-----"] * 7)
    df = pd.DataFrame(
        all_rows,
        columns=[
            "Subject Code",
            "Subject Name",
            "Assessment",
            "Unweighted Mark",
            "Weighted Mark",
            "Mark Weight",
            "Total Mark",
        ],
    ).astype(str)  # <-- Convert all columns to string
    st.dataframe(df.reset_index(drop=True), use_container_width=True)


def build_tables_per_subject(sem_obj, data_persistence):
    # Gather all subjects (including synced)
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
                    assignments = [Assignment(**a) for a in subj.get("assignments", [])]
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
                f"Select an assignment for {subject_code}",
                options=range(len(df)),
                format_func=lambda i: df.iloc[i]["Assessment"],
                key=select_key,
                index=st.session_state[select_key] if len(df) > 0 else None,
                horizontal=True if len(df) <= 5 else False,
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
        total_weighted_mark = sum(
            entry.weighted_mark for entry in subject.assignments if isinstance(entry.weighted_mark, (int, float))
        )
        total_weight = sum(
            entry.mark_weight for entry in subject.assignments if isinstance(entry.mark_weight, (int, float))
        )
        exam_mark = subject.examinations.exam_mark if subject.examinations else 0
        exam_weight = subject.examinations.exam_weight if subject.examinations else 100
        total_mark = subject.total_mark

        st.markdown(
            f"**Summary:**  "
            f"Total Weighted: `{total_weighted_mark:.2f}` &nbsp; | &nbsp; "
            f"Total Weight: `{total_weight:.0f}%` &nbsp; | &nbsp; "
            f"Exam Mark: `{exam_mark:.2f}` &nbsp; | &nbsp; "
            f"Exam Weight: `{exam_weight:.0f}%` &nbsp; | &nbsp; "
            f"Total Mark: `{total_mark:.0f}`"
        )
        st.markdown("---")


st.header(f"Subjects and Assessments for {semester} {year}")
build_tables_per_subject(sem_obj, data_persistence)

st.caption("Tip: Refresh the page after adding or deleting subjects/assignments to see updates.")
