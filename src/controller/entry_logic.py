import streamlit as st
from typing import Literal, Optional, Union

from .table_logic import sync_table_entries


def add_entry(self):
    """
    Adds or updates an entry for a subject in the selected semester using Streamlit widgets.

    This method validates user input, checks for the existence of the subject in the current
    or other semesters, and ensures that entries are added or updated in the correct semester.
    If the subject belongs to a different semester, a warning is displayed to the user.

    Raises a critical error message if the entry addition or update fails.

    Steps:
    1. Validate the selected semester and input fields.
    2. Check if the subject exists in the current or other semesters.
    3. Add or update the entry in the correct semester.
    4. Sync changes and refresh the table for the current semester.

    Returns:
        None

    Raises:
        ValueError: If the entry addition or update fails.

    Displays:
        QMessageBox.warning: If the semester or subject is invalid.
        QMessageBox.information: On successful addition or update of the entry.
        QMessageBox.critical: If an error occurs during the process.
    """
    semester_name = st.selectbox("Select Semester", list(self.semesters.keys()))
    semester = self.semesters.get(semester_name)

    if not semester:
        st.warning(f"Semester '{semester_name}' not found.")
        return

    subject_code = st.text_input("Subject Code")
    assessment = st.text_input("Assessment Name")
    weighted_mark_text = st.text_input("Weighted Mark (number or S/U)").upper()
    mark_weight_text = st.text_input("Mark Weight")

    # Default values
    weighted_mark: Union[float, str]
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: Literal["numeric", "S", "U"] = "numeric"

    if weighted_mark_text in ("S", "U"):
        weighted_mark = weighted_mark_text
        grade_type = weighted_mark_text
        unweighted_mark = None
        mark_weight = None
    else:
        try:
            weighted_mark = float(weighted_mark_text)
            mark_weight = float(mark_weight_text)
            unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0
            grade_type = "numeric"
        except ValueError:
            st.warning("Weighted mark and mark weight must be numbers, or S/U for mark.")
            return

    # Check if the subject exists in the current semester or others
    target_semester = semester
    for _, other_semester in self.semesters.items():
        if subject_code in other_semester.subjects:
            target_semester = other_semester
            break

    if target_semester != semester:
        st.warning(
            f"Subject '{subject_code}' belongs to the '{target_semester.name}' semester. "
            "Please switch to that semester to modify or add entries for this subject."
        )
        return

    if st.button("Add/Update Entry"):
        try:
            target_semester.add_entry(
                subject_code=subject_code,
                subject_assessment=assessment,
                weighted_mark=weighted_mark,
                unweighted_mark=unweighted_mark,
                mark_weight=mark_weight,
                grade_type=grade_type,
            )
            sync_table_entries(current_semester=semester, synced_semester=target_semester)
            self.update_table(semester)
            st.success("Entry added or updated successfully.")
        except ValueError as error:
            st.error(f"Failed to add or update entry: {error}")


def calculate_exam_mark(self):
    """
    Calculates the exam mark for a specific subject in the selected semester using Streamlit.

    This method retrieves the semester name from the combo box and the subject code
    from the text entry field. It validates the input and calculates the exam mark
    for the specified subject using the corresponding semester's data. If the subject
    code is not provided or the subject is not found, an error message is displayed.

    Returns:
        None: Updates the table with the semester data and displays error messages
        if necessary.
    """
    semester_name = st.selectbox("Select Semester", list(self.semesters.keys()))
    subject_code = st.text_input("Subject Code for Exam Mark Calculation")

    if st.button("Calculate Exam Mark"):
        if not subject_code:
            st.error("Please enter a Subject Code.")
            return

        exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)
        self.update_table(self.semesters[semester_name])

        if exam_mark is None:
            st.error(f"Subject {subject_code} not found.")
        else:
            st.success(f"Exam mark for {subject_code}: {exam_mark}")


def delete_entry(self):
    """
    Deletes selected entries from the current semester using Streamlit.

    This method allows the user to delete one or more selected entries from the
    table corresponding to the current semester. It performs the following steps:
    - Validates the selected semester and rows.
    - Deletes the entry from the semester's data structure.
    - Removes the corresponding row(s) from the table.
    - Synchronizes the table entries with other semesters if applicable.
    - Refreshes the table to reflect the changes.

    Raises appropriate error messages if the semester or selected rows are invalid,
    or if the deletion operation fails.

    Steps:
    1. Retrieve the selected semester from the combo box.
    2. Validate the selected rows in the table.
    3. For each selected row:
       - Retrieve the subject code and assessment details.
       - Delete the entry from the semester's data structure.
       - Remove the row from the table.
       - Synchronize entries with other semesters if necessary.
    4. Refresh the table for the current semester.

    Error Handling:
    - Displays a warning if the semester is not found.
    - Displays a warning if no rows are selected.
    - Displays a critical error message if the deletion operation fails.

    Note:
    - This method assumes that the `semester_combo` and `table` widgets are properly initialized.
    - The `semesters` dictionary should contain valid semester objects with a `delete_entry` method.

    """
    semester_name = st.selectbox("Select Semester", list(self.semesters.keys()))
    semester = self.semesters.get(semester_name)
    if not semester:
        st.warning(f"Semester '{semester_name}' not found.")
        return

    subject_codes = list(semester.subjects.keys())
    subject_code = st.selectbox("Select Subject to Delete Entry From", subject_codes)
    subject = semester.subjects.get(subject_code)
    if not subject:
        st.warning("Subject not found.")
        return

    assessments = [a.subject_assessment for a in subject.assignments]
    assessment = st.selectbox("Select Assessment to Delete", assessments)

    if st.button("Delete Entry"):
        try:
            semester.delete_entry(subject_code, assessment)
            # Sync the table for the current semester with the synced semester
            for _, synced_semester in self.semesters.items():
                if synced_semester != semester and subject_code in synced_semester.subjects:
                    sync_table_entries(semester, synced_semester)
            self.update_table(semester)
            st.success(f"Deleted assessment '{assessment}' from subject '{subject_code}'.")
        except ValueError as error:
            st.error(f"Failed to delete entry: {error}")


def manage_total_mark(self):
    """
    Manage the Total Mark for a specified subject in the selected semester using Streamlit.

    This method allows the user to set or clear the Total Mark for a subject.
    It validates the input fields, checks if the subject exists in the current
    or other semesters, and updates the data structure accordingly.

    Steps:
    1. Retrieve the selected semester and subject code from the UI.
    2. Validate the existence of the semester and subject.
    3. Prompt the user to either set or clear the Total Mark.
    4. Update the Total Mark in the data structure and save changes.
    5. Refresh the table to reflect the updated data.

    Error Handling:
    - Displays warnings or critical error messages if the semester or subject
        is not found, or if the data structure is invalid.
    - Ensures proper handling of user cancellation during input.

    UI Components:
    - `semester_combo`: Dropdown for selecting the semester.
    - `subject_code_entry`: Text field for entering the subject code.
    - `QMessageBox`: Used for displaying error, warning, and success messages.
    - `QInputDialog`: Used for prompting the user to input the Total Mark.

    Data Structure:
    - `semesters`: Dictionary containing semester objects.
    - `subjects`: Dictionary or list within a semester object representing subjects.

    Persistence:
    - Saves changes to the data structure using `self.storage_handler.save_data`.
    - Updates the UI table using `self.update_table`.

    Returns:
    None
    """
    semester_name = st.selectbox("Select Semester", list(self.semesters.keys()))
    semester = self.semesters.get(semester_name)

    if not semester:
        st.warning(f"Semester '{semester_name}' not found.")
        return

    subject_codes = list(semester.subjects.keys())
    subject_code = st.selectbox("Select Subject to Set Total Mark", subject_codes)

    if not subject_code:
        st.warning("Please select a Subject Code.")
        return

    total_mark = st.number_input(f"Enter Total Mark for {subject_code}:", min_value=0.0, format="%.2f")

    if st.button("Set Total Mark"):
        try:
            subject_item = semester.subjects[subject_code]
            subject_item.total_mark = total_mark
            self.storage_handler.save_data(self.semesters)
            self.update_table(semester)
            st.success(f"Total Mark for '{subject_code}' set to {total_mark} in semester '{semester.name}'.")
        except KeyError:
            st.error(f"Subject '{subject_code}' not found in the data structure.")
