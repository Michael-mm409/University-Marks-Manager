from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

from model import Assignment, Examination, Semester, Subject

if TYPE_CHECKING:
    from view import Application


def update_table(app: "Application", semester: Semester | str):
    """
    Updates the table widget with data from the specified semester, including subjects and their assignments.

    Args:
        semester (Semester | str): The semester to display data for. Can be a Semester object or a string
                        representing the semester name.

    Behavior:
        - Clears the table before populating it with new data.
        - If `semester` is a string, attempts to retrieve the corresponding Semester object.
        - Gathers all subjects from the specified semester, including synced subjects from other semesters.
        - Sorts subjects by their codes.
        - Builds rows for each subject, including assignment details, summary rows, and separators.
        - Inserts rows into the table and adjusts column sizes to fit content.

    Row Structure:
        - Assignment rows: Display details for each assignment, including assessment name, marks, weights, and
            whether the subject is synced.
        - Summary rows: Provide a summary of the subject, including total marks, weights, exam marks, and exam weights.
        - Separator rows: Separate subjects visually with a row of equal signs.

    Notes:
        - If the semester is not found, a message is printed and the table is not updated.
    """
    app.table.setRowCount(0)

    # Ensure semester is a Semester object
    if isinstance(semester, str):
        sem_obj = app.semesters.get(semester)
        if sem_obj is None:
            QMessageBox.warning(None, "Warning", f"Semester '{semester}' not found.")
            return
    else:
        sem_obj = semester

    # 1. Gather all subjects (including synced ones)
    subject_map = {}

    # Add normal subjects
    for subject_code, subject in sem_obj.subjects.items():
        subject_map.setdefault(subject_code, []).append((subject, False))  # False = not synced

    # Add synced subjects (from other semesters)
    for sync_semester in app.semesters.values():
        if sync_semester is sem_obj:
            continue
        for code, subj in sync_semester.subjects.items():
            if getattr(subj, "sync_subject", False):
                subject_map.setdefault(code, []).append((subj, True))  # True = synced

    # 2. Sort subject codes
    sorted_subject_codes = sorted(subject_map.keys())

    # 3. Build rows for each subject, keeping separator after each
    all_rows = []
    for subject_code in sorted_subject_codes:
        for subject, is_synced in subject_map[subject_code]:
            subject_name = subject.subject_name
            total_mark = subject.total_mark if hasattr(subject, "total_mark") else 0
            # Assignment rows
            for entry in subject.assignments:
                all_rows.append(
                    [
                        subject_code,
                        subject_name,
                        entry.subject_assessment.strip("\n") if entry.subject_assessment else "N/A",
                        f"{entry.unweighted_mark:.2f}",
                        f"{entry.weighted_mark:.2f}",
                        f"{entry.mark_weight:.2f}%",
                        f"{total_mark:.2f}",
                        "Synced" if is_synced else "",
                    ]
                )
            # Summary row
            total_weighted_mark = sum(entry.weighted_mark for entry in subject.assignments)
            total_weight = sum(entry.mark_weight for entry in subject.assignments)
            exam_mark = subject.examinations.exam_mark if hasattr(subject, "examinations") else 0
            exam_weight = subject.examinations.exam_weight if hasattr(subject, "examinations") else 100
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
            # Separator row
            all_rows.append(["=" * 25 for _ in range(8)])

    # 4. Insert rows into the table
    app.table.setRowCount(0)
    for row_data in all_rows:
        app.table.insertRow(app.table.rowCount())
        for col_index, cell_data in enumerate(row_data):
            table_item = QTableWidgetItem(cell_data)
            table_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            app.table.setItem(app.table.rowCount() - 1, col_index, table_item)

    # Resize columns to fit content
    app.table.resizeColumnsToContents()


@staticmethod
def sync_table_entries(current_semester: Semester, synced_semester: Semester):
    """
    Synchronizes subjects and assignments between two Semester objects.
    Updates `current_semester` with new subjects or assignments from `synced_semester`.
    Existing subjects and assignments are updated with corresponding data.

    Args:
        current_semester (Semester): Semester to be updated.
        synced_semester (Semester): Semester containing data to sync.

    Behavior:
        - Adds new subjects from `synced_semester` to `current_semester`.
        - Updates existing subjects and assignments with data from `synced_semester`.
        - Performs updates in memory without saving to persistent storage.

    Note:
        Assumes `synced_semester.subjects` is a dictionary with subject codes as keys.
    """

    for subject_code, subject_data in synced_semester.subjects.items():
        if subject_code not in current_semester.subjects:
            # Add the subject to the current semester in memory (not saved to JSON)
            current_semester.subjects[subject_code] = Subject(
                subject_code=subject_code,
                subject_name=subject_data[0]["Subject Name"]
                if isinstance(subject_data, list) and subject_data
                else subject_data.subject_name,
                assignments=[
                    Assignment(
                        subject_assessment=assignment.subject_assessment if isinstance(assignment, Assignment) else "",
                        unweighted_mark=assignment.unweighted_mark if isinstance(assignment, Assignment) else 0.0,
                        weighted_mark=assignment.weighted_mark if isinstance(assignment, Assignment) else 0.0,
                        mark_weight=assignment.mark_weight if isinstance(assignment, Assignment) else 0.0,
                    )
                    for assignment in subject_data.assignments
                    if isinstance(assignment, dict)
                ]
                if isinstance(subject_data, Subject)
                else [],
                total_mark=subject_data.total_mark,
                examinations=subject_data.examinations
                if isinstance(subject_data.examinations, Examination)
                else Examination(),
            )
        else:
            # Update the current semester's data with the synced semester's data
            current_subject_data = current_semester.subjects[subject_code]
            for assignment in subject_data.assignments:
                # Check if the assignment already exists in the current semester
                existing_assignment = next(
                    (
                        assessment
                        for assessment in current_subject_data.assignments
                        if assessment.subject_assessment == assignment.subject_assessment
                    ),
                    None,
                )
                if existing_assignment:
                    # Update the existing assignment
                    existing_assignment.subject_assessment = assignment.subject_assessment
                    existing_assignment.unweighted_mark = assignment.unweighted_mark
                    existing_assignment.weighted_mark = assignment.weighted_mark
                    existing_assignment.mark_weight = assignment.mark_weight
                else:
                    # Add the new assignment
                    current_subject_data.assignments.append(assignment)
