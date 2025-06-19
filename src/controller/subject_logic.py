from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view.main_window import Application


import streamlit as st


def add_subject(self: "Application"):
    """
    Adds a subject to the selected semester using Streamlit widgets.

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
    semester_name = st.selectbox("Select Semester", list(self.semesters.keys()))
    semester = self.get_semester(semester_name)
    if semester is None:
        st.error(f"Semester '{semester_name}' not found.")
        return

    with st.form("Add Subject"):
        subject_code = st.text_input("Subject Code")
        subject_name = st.text_input("Subject Name")
        sync_subject = st.checkbox("Sync Subject", value=False)
        submitted = st.form_submit_button("Add Subject")
        if submitted:
            if not subject_code:
                st.warning("Subject code cannot be empty.")
                return
            try:
                semester.add_subject(subject_code, subject_name, sync_subject=sync_subject)
                self.update_table(semester)
                st.success(f"Added subject '{subject_code}'.")
            except ValueError as error:
                st.error(f"Failed to add subject: {error}")


def delete_subject(self: "Application"):
    """
    Deletes one or more subjects from the currently selected semester using Streamlit widgets.

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

    semester_name = st.selectbox("Select Semester", list(self.semesters.keys()))
    semester = self.get_semester(semester_name)
    if semester is None:
        st.error(f"Semester '{semester_name}' not found.")
        return

    subject_codes = list(semester.subjects.keys())
    if not subject_codes:
        st.warning("There are no subjects to delete in this semester.")
        return

    selected_subjects = st.multiselect("Select Subjects to Delete", subject_codes)

    if st.button("Delete Selected Subjects"):
        for subject_code in selected_subjects:
            try:
                semester.delete_subject(subject_code)
            except ValueError as error:
                st.error(f"Failed to delete subject: {error}")
        self.storage_handler.save_data(self.semesters)
        self.update_table(semester)
        st.success("Selected subjects deleted.")
