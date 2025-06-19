import streamlit as st
from datetime import datetime

from model.data_persistence import DataPersistence
from model.semester import Semester

import pandas as pd

# --- Streamlit UI ---

st.set_page_config(page_title="University Marks Manager", layout="wide")
st.title("University Marks Manager (Streamlit Edition)")

# --- Year Selection ---
years = [str(y) for y in range(datetime.now().year - 2, datetime.now().year + 3)]
year = st.selectbox("Select Year", years, index=years.index(str(datetime.now().year)))
data_persistence = DataPersistence(year)

# --- Semester Selection ---
semester_names = list(data_persistence.data.keys()) or ["Autumn", "Spring", "Annual"]
semester = st.selectbox("Select Semester", semester_names)
sem_obj = Semester(semester, year, data_persistence)

# --- Subject Selection ---
subject_codes = list(sem_obj.subjects.keys())
subject_code = st.selectbox("Select Subject", subject_codes) if subject_codes else None

# --- Display Table ---
def build_table(sem_obj):
    all_rows = []
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
    )
    st.dataframe(df, use_container_width=True)

st.subheader(f"Subjects and Assessments for {semester} {year}")
build_table(sem_obj)

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

# --- Delete Subject ---
with st.expander("Delete Subject"):
    del_code = st.selectbox("Select Subject to Delete", subject_codes, key="del_subject_code") if subject_codes else None
    if st.button("Delete Subject", key="del_subject_btn") and del_code:
        sem_obj.delete_subject(del_code)
        st.success(f"Deleted subject {del_code}. Please refresh the page to see changes.")

# --- Add Assignment ---
if subject_code:
    with st.expander(f"Add Assignment to {subject_code}"):
        assessment = st.text_input("Assessment Name", key="add_assessment")
        weighted_mark = st.number_input("Weighted Mark", min_value=0.0, key="add_weighted_mark")
        mark_weight = st.number_input("Mark Weight", min_value=0.0, key="add_mark_weight")
        if st.button("Add Assignment", key="add_assignment_btn"):
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

# --- Delete Assignment ---
if subject_code:
    subject = sem_obj.subjects[subject_code]
    assessments = [a.subject_assessment for a in subject.assignments]
    with st.expander(f"Delete Assignment from {subject_code}"):
        del_assessment = st.selectbox("Select Assessment to Delete", assessments, key="del_assessment") if assessments else None
        if st.button("Delete Assignment", key="del_assignment_btn") and del_assessment:
            sem_obj.delete_entry(subject_code, del_assessment)
            st.success(f"Deleted assessment '{del_assessment}' from {subject_code}. Please refresh the page to see changes.")

# --- Set Total Mark ---
if subject_code:
    with st.expander(f"Set Total Mark for {subject_code}"):
        total_mark = st.number_input("Total Mark", min_value=0.0, value=subject.total_mark, key="set_total_mark")
        if st.button("Set Total Mark", key="set_total_mark_btn"):
            subject.total_mark = total_mark
            data_persistence.save_data(data_persistence.data)
            st.success(f"Total Mark for '{subject_code}' set to {total_mark}.")

# --- Calculate Exam Mark ---
if subject_code:
    with st.expander(f"Calculate Exam Mark for {subject_code}"):
        if st.button("Calculate Exam Mark", key="calc_exam_mark_btn"):
            exam_mark = sem_obj.calculate_exam_mark(subject_code)
            if exam_mark is not None:
                st.info(f"Exam mark for {subject_code}: {exam_mark}")
            else:
                st.warning("Could not calculate exam mark.")

st.caption("Tip: Refresh the page after adding or deleting subjects/assignments to see updates.")