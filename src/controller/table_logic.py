import streamlit as st
import pandas as pd
from model.semester import Semester
from model.models import Assignment, Examination, Subject


def update_table(app, semester: Semester | str):
    """
    Displays the table for the specified semester using Streamlit,
    using the dataclasses from models.py for all data access.
    """
    # Ensure semester is a Semester object
    if isinstance(semester, str):
        sem_obj = app.semesters.get(semester)
        if sem_obj is None:
            st.warning(f"Semester '{semester}' not found.")
            return
    else:
        sem_obj = semester

    # 1. Gather all subjects (including synced ones)
    subject_map = {}

    # Add normal subjects
    for subject_code, subject in sem_obj.subjects.items():
        if isinstance(subject, Subject):
            subject_map.setdefault(subject_code, []).append((subject, False))  # False = not synced

    # Add synced subjects (from other semesters)
    for sync_semester in app.semesters.values():
        if sync_semester is sem_obj:
            continue
        for code, subj in sync_semester.subjects.items():
            if isinstance(subj, Subject) and getattr(subj, "sync_subject", False):
                subject_map.setdefault(code, []).append((subj, True))  # True = synced

    # 2. Sort subject codes
    sorted_subject_codes = sorted(subject_map.keys())

    # 3. Build rows for each subject, keeping separator after each
    all_rows = []
    for subject_code in sorted_subject_codes:
        for subject, is_synced in subject_map[subject_code]:
            subject_name = subject.subject_name
            total_mark = subject.total_mark
            # Assignment rows
            for entry in subject.assignments:
                if not isinstance(entry, Assignment):
                    continue
                all_rows.append(
                    [
                        subject_code,
                        subject_name,
                        entry.subject_assessment.strip("\n") if entry.subject_assessment else "N/A",
                        f"{entry.unweighted_mark:.2f}"
                        if isinstance(entry.unweighted_mark, (float, int))
                        else str(entry.unweighted_mark)
                        if entry.unweighted_mark is not None
                        else "",
                        f"{entry.weighted_mark:.2f}"
                        if isinstance(entry.weighted_mark, (float, int))
                        else str(entry.weighted_mark)
                        if entry.weighted_mark is not None
                        else "",
                        f"{entry.mark_weight:.2f}%"
                        if isinstance(entry.mark_weight, (float, int))
                        else str(entry.mark_weight) + "%"
                        if entry.mark_weight is not None
                        else "",
                        f"{total_mark:.2f}",
                        "Synced" if is_synced else "",
                    ]
                )
            # Summary row
            total_weighted_mark = sum(
                entry.weighted_mark for entry in subject.assignments
                if isinstance(entry, Assignment) and isinstance(entry.weighted_mark, (int, float))
            )
            total_weight = sum(
                entry.mark_weight for entry in subject.assignments
                if isinstance(entry, Assignment) and isinstance(entry.mark_weight, (int, float))
            )
            exam_mark = subject.examinations.exam_mark if isinstance(subject.examinations, Examination) else 0
            exam_weight = subject.examinations.exam_weight if isinstance(subject.examinations, Examination) else 100
            all_rows.append(
                [
                    f"Summary for {subject_code}",
                    f"Assessments: {len(subject.assignments)}",
                    f"Total Weighted: {total_weighted_mark:.2f}",
                    f"Total Weight: {total_weight:.0f}%",
                    f"Total Mark: {total_mark:.0f}",
                    f"Exam Mark: {exam_mark:.2f}",
                    f"Exam Weight: {exam_weight:.0f}%",
                    "Synced" if is_synced else "",
                ]
            )
            # Separator row (fixed length, or you can use "" for a blank row)
            all_rows.append(["-----"] * 8)

    # 4. Display as a table in Streamlit
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
            "Status",
        ],
    )
    st.table(df)
