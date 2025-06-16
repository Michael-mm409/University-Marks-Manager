from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from PyQt6.QtWidgets import QInputDialog, QMessageBox

from .table_logic import sync_table_entries

if TYPE_CHECKING:
    from view.main_window import Application


@staticmethod
def __validate_float(value: Any, error_message: str) -> float:
    """
    Validate the input value and return it as a float.

    Args:
        value (Any): The input value to validate. Can be of any type.
        error_message (str): The error message to display if the value cannot be converted to a float.

    Returns:
        float: The validated float value. Returns 0.0 if the input is None or an empty string.
                Returns -1 if the input cannot be converted to a float and displays an error message.
    """
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except ValueError:
        QMessageBox.critical(None, "Error", error_message)
        return -1


def add_entry(self: "Application") -> None:
    """
    Adds or updates an entry for a subject in the selected semester.

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
    semester_name = self.semester_combo.currentText()
    semester = self.semesters.get(semester_name)

    if not semester:
        QMessageBox.warning(self, "Error", f"Semester '{semester_name}' not found.")
        return

    subject_code = self.subject_code_entry.text().strip()
    assessment = self.assessment_entry.text().strip()
    weighted_mark_text = self.weighted_mark_entry.text().strip().upper()
    mark_weight_text = self.mark_weight_entry.text().strip()

    # Default values
    weighted_mark: Union[float, str]
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: Literal["numeric", "S", "U"] = "numeric"

    if weighted_mark_text in ("S", "U"):
        weighted_mark = weighted_mark_text
        grade_type = weighted_mark_text  # "S" or "U"
        # For S/U, unweighted_mark and mark_weight are not needed
        unweighted_mark = None
        mark_weight = None
    else:
        try:
            weighted_mark = float(weighted_mark_text)
            mark_weight = float(mark_weight_text)
            unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0
            grade_type = "numeric"
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input", "Weighted mark and mark weight must be numbers, or S/U for mark."
            )
            return

    # Check if the subject exists in the current semester
    target_semester = semester
    for _, other_semester in self.semesters.items():
        if subject_code in other_semester.subjects:
            target_semester = other_semester
            break

    if target_semester != semester:
        QMessageBox.warning(
            self,
            "Warning",
            f"Subject '{subject_code}' belongs to the '{target_semester.name}' semester. "
            "Please switch to that semester to modify or add entries for this subject.",
        )
        return

    try:
        # Add or update the entry in the target semester
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
    except ValueError as error:
        QMessageBox.critical(self, "Error", f"Failed to add or update entry: {error}")


def calculate_exam_mark(self: "Application") -> None:
    """
    Calculates the exam mark for a specific subject in the selected semester.

    This method retrieves the semester name from the combo box and the subject code
    from the text entry field. It validates the input and calculates the exam mark
    for the specified subject using the corresponding semester's data. If the subject
    code is not provided or the subject is not found, an error message is displayed.

    Returns:
        None: Updates the table with the semester data and displays error messages
        if necessary.
    """
    semester_name = self.semester_combo.currentText()
    subject_code = self.subject_code_entry.text()

    if not subject_code:
        QMessageBox.critical(self, "Error", "Please enter a Subject Code.")
        return

    exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)
    self.update_table(self.semesters[semester_name])

    if exam_mark is None:
        QMessageBox.critical(self, "Error", f"Subject {subject_code} not found.")


def delete_entry(self: "Application") -> None:
    """
    Deletes selected entries from the current semester and updates the table.

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
    semester_name = self.semester_combo.currentText()
    semester = self.semesters.get(semester_name)
    if not semester:
        QMessageBox.warning(self, "Error", f"Semester '{semester_name}' not found.")
        return

    sel_model = self.table.selectionModel()
    if sel_model is None:
        return
    selected_rows = sel_model.selectedRows()
    if not selected_rows:
        QMessageBox.warning(self, "Error", "Please select an entry to delete.")
        return

    for index in sorted(selected_rows, reverse=True):
        row = index.row()
        subject_code_item = self.table.item(row, 0)
        assessment_item = self.table.item(row, 2)

        if subject_code_item and assessment_item:
            subject_code = subject_code_item.text()
            assessment = assessment_item.text()
            try:
                # Delete the entry from the current semester
                semester.delete_entry(subject_code, assessment)

                # Remove the row from the table
                self.table.removeRow(row)

                # Sync the table for the current semester with the synced semester
                for _, synced_semester in self.semesters.items():
                    if synced_semester != semester and subject_code in synced_semester.subjects:
                        sync_table_entries(semester, synced_semester)

            except ValueError as error:
                QMessageBox.critical(self, "Error", f"Failed to delete entry: {error}")
        else:
            QMessageBox.warning(self, "Error", "Failed to retrieve subject code or assessment.")

    # Refresh the table for the current semester
    self.update_table(semester)


def manage_total_mark(self: "Application") -> None:
    """
    Manage the Total Mark for a specified subject in the selected semester.

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
    semester_name = self.semester_combo.currentText()
    semester = self.semesters.get(semester_name)

    if not semester:
        QMessageBox.warning(self, "Error", f"Semester '{semester_name}' not found.")
        return

    # Get the subject code from the entry field
    subject_code = self.subject_code_entry.text().strip()

    if not subject_code:
        QMessageBox.warning(self, "Error", "Please enter a Subject Code in the entry field.")
        return

    # Check if the subject exists in the current semester
    target_semester = semester
    if subject_code not in semester.subjects:
        # Search for the subject in other semesters
        for _, other_semester in self.semesters.items():
            if subject_code in other_semester.subjects:
                target_semester = other_semester
                break

        if target_semester == semester:
            QMessageBox.critical(self, "Error", f"Subject '{subject_code}' not found in any semester.")
            return

    total_mark, ok = QInputDialog.getDouble(self, "Set Total Mark", f"Enter Total Mark for {subject_code}:", decimals=2)

    if ok:
        try:
            subject_item = target_semester.subjects[subject_code]
            if isinstance(subject_item, dict):
                subject_item["Total Mark"] = total_mark
                self.storage_handler.save_data(self.semesters)
                self.update_table(semester)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Total Mark for '{subject_code}' set to {total_mark} in semester '{target_semester.name}'.",
                )
            else:
                QMessageBox.critical(self, "Error", f"Invalid data structure for subject '{subject_code}'.")
        except KeyError:
            QMessageBox.critical(self, "Error", f"Subject '{subject_code}' not found in the data structure.")
    # If user cancels (ok is False), do nothing
