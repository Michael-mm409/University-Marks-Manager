from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QDialog, QMessageBox

from view.ui import AddSubjectDialog, DeleteSubjectDialog, confirm_remove_subject

if TYPE_CHECKING:
    from view.main_window import Application


def add_subject(self: "Application"):
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
    semester = self.get_semester(semester_name)
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
            # Add the subject with the "sync subject" flag set to False
            semester.add_subject(subject_code, subject_name, sync_subject=False)

            # Refresh the table to include synced subjects
            self.update_table(semester)
        except ValueError as error:
            QMessageBox.critical(self, "Error", f"Failed to add subject: {error}")


def delete_subject(self: "Application"):
    """
    Deletes one or more subjects from the currently selected semester.

    This method interacts with the user interface to determine the semester and subjects
    to delete. It displays dialogs for subject selection and confirmation, and handles
    errors that may occur during the deletion process.

    Steps:
    1. Retrieve the currently selected semester from the UI.
    2. Check if the semester exists and contains subjects.
    3. Display a dialog for the user to select subjects to delete.
    4. Confirm deletion for each selected subject.
    5. Update the semester data and save changes.

    Args:
        self (Application): The main application instance.

    Raises:
        ValueError: If an error occurs during subject deletion.

    User Interaction:
        - Displays error messages if the semester is not found or contains no subjects.
        - Opens a dialog for subject selection.
        - Prompts for confirmation before deleting each subject.

    Updates:
        - Saves updated semester data to persistent storage.
        - Refreshes the subject table in the UI.
    """

    semester_name = self.semester_combo.currentText()
    semester = self.get_semester(semester_name)
    if semester is None:
        QMessageBox.critical(self, "Error", f"Semester '{semester_name}' not found.")
        return

    # Get all subject codes in the current semester
    subject_codes = list(semester.subjects.keys())
    if not subject_codes:
        QMessageBox.warning(self, "Error", "There are no subjects to delete in this semester.")
        return

    # Optionally, get the currently selected subject in the table
    selected_items = self.table.selectedItems()
    default_subject = selected_items[0].text() if selected_items else None

    # Show the DeleteSubjectDialog
    dialog = DeleteSubjectDialog(subject_codes, default_subject, self)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return
    selected_subjects = dialog.selected_subjects()
    if not selected_subjects:
        QMessageBox.warning(self, "Error", "No subjects selected for deletion.")
        return

    # Confirm removal for each subject
    for subject_code in selected_subjects:
        if not confirm_remove_subject(self, subject_code):
            continue
        try:
            semester.delete_subject(subject_code)
        except ValueError as error:
            QMessageBox.critical(self, "Error", f"Failed to delete subject: {error}")

    self.storage_handler.save_data(self.semesters)
    self.update_table(semester)
