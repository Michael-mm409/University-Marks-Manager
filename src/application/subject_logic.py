from PyQt6.QtWidgets import QDialog, QMessageBox

from ui.subject_dialog import AddSubjectDialog, confirm_remove_subject


def add_subject(self):
    """
    Adds a subject to the selected semester.

    This method retrieves the currently selected semester from the combo box
    and attempts to add a new subject to it. If the semester is not found,
    an error message is displayed. The method uses the AddSubjectDialog to
    gather subject details from the user. If the subject code is empty or
    an error occurs during the addition process, appropriate error messages
    are shown.

    Steps:
    1. Retrieve the selected semester from the combo box.
    2. Display the AddSubjectDialog for user input.
    3. Validate the subject code.
    4. Add the subject to the semester with synchronization enabled.
    5. Refresh the table to reflect the updated subjects.

    Raises:
        ValueError: If adding the subject fails due to invalid data or other issues.

    Dialogs:
        - QMessageBox: Displays error or warning messages.
        - AddSubjectDialog: Collects subject details from the user.
    """
    semester_name = self.semester_combo.currentText()
    semester = self.semesters.get(semester_name)
    if semester is None:
        QMessageBox.critical(self, "Error", f"Semester '{semester_name}' not found.")
        return

    # Show the AddSubjectDialog
    dialog = AddSubjectDialog(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        subject_code, subject_name, custom_semesters = dialog.get_subject_data()

        if not subject_code:
            QMessageBox.warning(self, "Error", "Subject code cannot be empty.")
            return

        try:
            # Add the subject with the "sync subject" flag set to True
            semester.add_subject(subject_code, subject_name, sync_subject=True)

            # Refresh the table to include synced subjects
            self.update_table(semester)
        except ValueError as error:
            QMessageBox.critical(self, "Error", f"Failed to add subject: {error}")


def delete_subject(self):
    """
    Deletes a selected subject from the currently selected semester.

    This method retrieves the selected semester and subject from the UI,
    confirms the deletion with the user, and removes the subject from the
    semester. It then saves the updated data and refreshes the table view.

    Raises:
        ValueError: If an error occurs while deleting the subject.

    Steps:
        1. Retrieve the currently selected semester from the combo box.
        2. Validate that the semester exists.
        3. Retrieve the selected subject code from the table.
        4. Confirm the deletion with the user.
        5. Remove the subject from the semester.
        6. Save the updated data to persistent storage.
        7. Refresh the table view to reflect changes.

    Error Handling:
        - Displays an error message if the semester is not found.
        - Displays a warning if no subject is selected.
        - Displays an error message if the deletion fails.

    UI Components:
        - `semester_combo`: Combo box for selecting the semester.
        - `table`: Table displaying subjects for the selected semester.

    Confirmation Dialog:
        - Uses `confirm_remove_subject` to confirm the deletion.

    """
    semester_name = self.semester_combo.currentText()
    semester = self.semesters.get(semester_name)
    if semester is None:
        QMessageBox.critical(self, "Error", f"Semester '{semester_name}' not found.")
        return

    # Get the selected subject code from the table
    selected_items = self.table.selectedItems()
    if not selected_items:
        QMessageBox.warning(self, "Error", "Please select a subject to delete.")
        return

    subject_code = selected_items[0].text()  # Assuming the first column contains the subject code

    # Confirm removal
    if not confirm_remove_subject(self, subject_code):
        return

    try:
        semester.delete_subject(subject_code)  # Remove the subject from the semester
        self.storage_handler.save_data(self.semesters)  # Save changes
        self.update_table(semester)  # Refresh the table
    except ValueError as error:
        QMessageBox.critical(self, "Error", f"Failed to delete subject: {error}")
