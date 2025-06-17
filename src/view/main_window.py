import os
from pathlib import Path
from typing import cast

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QWidget,
)

from controller.table_logic import update_table
from model import DataPersistence, Semester

from .ui import SemesterSelectionDialog
from .ui_main_window import MainWindowUI


class Application(QMainWindow, MainWindowUI):
    """
    This class represents the main window of the University Marks Manager application. It provides
    a graphical user interface (GUI) for managing university marks, including subjects, assessments,
    and semesters. The application allows users to add, delete, and update entries, calculate exam marks,
    and manage total marks for subjects.

    Args:
        storage_handler (DataPersistence): Handles data persistence for the application.
        semesters (dict): A dictionary mapping semester names to Semester objects.
        central_widget (QWidget): The main widget of the application.
        year_combo (QComboBox): Dropdown for selecting the year.
        semester_combo (QComboBox): Dropdown for selecting the semester.
        year_label (QLabel): Label for the year dropdown.
        semester_label (QLabel): Label for the semester dropdown.
        table (QTableWidget): Table for displaying subjects and assessments.
        subject_code_entry (QLineEdit): Input field for subject code.
        subject_name_entry (QLineEdit): Input field for subject name.
        assessment_entry (QLineEdit): Input field for assessment name.
        weighted_mark_entry (QLineEdit): Input field for weighted mark.
        mark_weight_entry (QLineEdit): Input field for mark weight.
        btn_add_entry (QPushButton): Button for adding an entry.
        btn_delete_entry (QPushButton): Button for deleting an entry.
        btn_calc (QPushButton): Button for calculating exam marks.
        btn_add_subject (QPushButton): Button for adding a subject.
        btn_delete_subject (QPushButton): Button for deleting a subject.
        btn_set_total_mark (QPushButton): Button for managing total marks.

    Methods:
        __init__(storage_handler: DataPersistence):
            Initializes the Application class and sets up the GUI components.

        init_ui():
            Initializes the user interface for the application.

        setup_dropdowns():
            Configures the year and semester dropdowns.

        setup_labels():
            Configures the labels for the dropdowns.

        setup_tables():
            Configures the table for displaying subjects and assessments.

        setup_entry_fields(entry_layout: QGridLayout):
            Configures the input fields for adding or updating entries.

        setup_buttons(button_layout: QGridLayout):
            Configures the buttons for managing entries and subjects.

        populate_entries_from_selection():
            Populates the input fields based on the selected row in the table.

        update_year():
            Updates the application data based on the selected year.

        update_semester():
            Updates the application data based on the selected semester.

        update_table(semester: Semester | str):
            Updates the table with data from the specified semester.

        wrap_text(text: str, max_chars):
            Wraps text to fit within a maximum character limit.

        resizeEvent(a0):
            Handles window resizing and adjusts row heights and column widths dynamically.

        add_subject():
            Adds a new subject to the selected semester.

        delete_subject():
            Deletes a subject from the selected semester.

        add_entry():
            Adds or updates an entry for a subject in the selected semester.

        __validate_float(value: Any, error_message: str) -> float:
            Validates the input value and returns it as a float.

        delete_entry():
            Deletes an entry for a subject in the selected semester.

        calculate_exam_mark():
            Calculates the exam mark for a subject in the selected semester.

        manage_total_mark():
            Sets or clears the total mark for a subject in the selected semester.

        sync_table_entries(current_semester: Semester, synced_semester: Semester):
            Synchronizes the table entries between the current semester and the synced semester.
    """

    def __init__(self, storage_handler: DataPersistence):
        """
        Initializes the Application main window and its core components.

        Args:
            storage_handler (DataPersistence): The handler for loading and saving persistent data.
        """
        super().__init__()

        # Set the application window icon
        self.setWindowIcon(QIcon("assets/app_icon.png"))

        # Store the data persistence handler
        self.storage_handler = storage_handler

        # List of semester names loaded from the storage handler's data (e.g., ["Autumn", "Spring", ...])
        self.semester_names = list(self.storage_handler.data.keys())

        # Dictionary to cache loaded Semester objects for quick access
        self._semesters = {}

        # Main central widget for the window
        self.central_widget = QWidget()

        # Dropdown widgets for selecting year and semester
        self.year_combo = QComboBox()
        self.semester_combo = QComboBox()

        # Labels for the dropdowns (initialized as None, set up later)
        self.year_label = QLabel("Select Year:")
        self.semester_label = QLabel("Select Semester:")

        # Table widget for displaying subjects, assessments, and marks
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # Select entire rows
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # Only one row at a time
        self.table.setWordWrap(True)  # Enable word wrapping in table cells

        # Entry fields for user input (subject code, name, assessment, marks, etc.)
        self.subject_code_entry = QLineEdit()
        self.subject_name_entry = QLineEdit()
        self.assessment_entry = QLineEdit()
        self.weighted_mark_entry = QLineEdit()
        self.mark_weight_entry = QLineEdit()

        # Buttons for various actions (add/delete entry/subject, calculate, set total mark)
        self.btn_add_entry = QPushButton("Add Entry", self)
        self.btn_delete_entry = QPushButton("Delete Entry", self)
        self.btn_calc = QPushButton("Calculate Exam Mark", self)
        self.btn_add_subject = QPushButton("Add Subject", self)
        self.btn_delete_subject = QPushButton("Delete Subject", self)
        self.btn_set_total_mark = QPushButton("Set Total Mark", self)  # Button for managing total mark

        # Initialize the user interface and layout
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface for the University Marks Manager application.
        This method sets up the main window, layouts, widgets, and connections for the application.
        It organizes the UI components such as dropdowns, labels, tables, entry fields, and buttons
        into appropriate layouts and ensures proper alignment and resizing.
        Key functionalities:
        - Sets the window title and geometry.
        - Configures the central widget and its layout.
        - Creates and organizes layouts for dropdowns, labels, entry fields, and buttons.
        - Adds dropdowns for year and semester selection.
        - Sets up a table for displaying data and ensures columns and rows are resized to fit content.
        - Connects table selection changes to populate entry fields.
        - Ensures the UI components are expandable and properly aligned.
        Note:
        - This method assumes that helper methods like `setup_entry_fields`, `setup_dropdowns`,
          `setup_labels`, `setup_tables`, and `setup_buttons` are implemented elsewhere in the class.
        - The `update_year` method is called to initialize the year dropdown.
        """

        self.setup_ui()

    def populate_entries_from_selection(self) -> None:
        """
        Populates the entry fields in the application based on the selected row in the table.

        This method retrieves the data from the first selected row in the table and updates
        the corresponding entry fields for subject code, assessment name, weighted mark,
        and mark weight. It handles special cases where the assessment name contains
        "No Assignments" or the subject code contains keywords like "==" or "Summary".

        Behavior:
        - If no rows are selected, the method does nothing.
        - If the selected row contains invalid or empty items, a message is printed.
        - Clears entry fields if specific keywords are found in the subject code or assessment name.
        - Populates entry fields with data from the selected row if valid items are present.

        Entry Fields Updated:
        - `self.subject_code_entry`: Text field for the subject code.
        - `self.assessment_entry`: Text field for the assessment name.
        - `self.weighted_mark_entry`: Text field for the weighted mark.
        - `self.mark_weight_entry`: Text field for the mark weight (percentage).

        Special Cases:
        - Clears all entry fields if "No Assignments" is found in the assessment name.
        - Clears all entry fields if the subject code contains "==" or "Summary".

        Returns:
        None
        """
        sel_model = self.table.selectionModel()
        if sel_model is None:
            return
        selected_rows = sel_model.selectedRows()

        if selected_rows:
            row = selected_rows[0].row()  # Get the first selected row

            subject_code_item = self.table.item(row, 0)
            assessment_name_item = self.table.item(row, 2)

            if subject_code_item and assessment_name_item:
                subject_code = subject_code_item.text()
                assessment_name = assessment_name_item.text()

                if "No Assignments" in assessment_name:
                    self.subject_code_entry.setText(subject_code)
                    self.assessment_entry.clear()
                    self.weighted_mark_entry.clear()
                    self.mark_weight_entry.clear()
                    return
                elif any(keyword in subject_code for keyword in ["==", "Summary"]):
                    self.subject_code_entry.clear()
                    self.assessment_entry.clear()
                    self.weighted_mark_entry.clear()
                    self.mark_weight_entry.clear()
                    return

                self.subject_code_entry.setText(subject_code)
                self.assessment_entry.setText(assessment_name)
                weighted_item = self.table.item(row, 4)
                mark_weight_item = self.table.item(row, 5)
                if weighted_item:
                    self.weighted_mark_entry.setText(weighted_item.text())
                else:
                    self.weighted_mark_entry.clear()
                if mark_weight_item:
                    self.mark_weight_entry.setText(mark_weight_item.text().replace("%", ""))
                else:
                    self.mark_weight_entry.clear()
            else:
                QMessageBox.critical(None, "Error", "Invalid or empty items in the selected row.")

    def update_year(self) -> None:
        """
        Updates the application state based on the selected academic year.
        This method handles the following:
        - Clears existing semester data.
        - Checks if a JSON file for the selected year exists.
            - If the file exists:
                - Loads the data from the file.
                - Initializes the storage handler with the loaded data.
                - Dynamically creates Semester objects based on the JSON keys.
                - Updates the semester combo box with the available semesters.
                - Updates the UI to reflect the selected semester.
            - If the file does not exist:
                - Prompts the user to select semesters to create via a dialog.
                - Initializes the storage handler for the new year.
                - Creates empty data structures for the selected semesters.
                - Saves the initialized data to a new JSON file.
                - Creates Semester objects for the selected semesters.
                - Updates the semester combo box with the selected semesters.
                - Updates the UI to reflect the selected semester.
        - If the user cancels the year change, displays an informational message.
        Raises:
            None
        Returns:
            None
        """

        selected_year = self.year_combo.currentText()

        self._semesters.clear()  # Clear the existing semesters
        # Build the expected JSON file path for the selected year
        json_file_path = Path(f"data/{selected_year}.json")
        if os.path.exists(json_file_path):
            # If the file exists, load the data and update the storage handler
            self.storage_handler = DataPersistence(selected_year)
            # Dynamically gather semester names from JSON keys in the loaded data
            self.semesters = {
                semester_name: Semester(semester_name, selected_year, self.storage_handler)
                for semester_name in self.storage_handler.data.keys()
            }

            # Clear and populate the semester combo box with dynamic semester names
            self.semester_combo.clear()
            self.semester_combo.addItems(self.semesters.keys())

            # Update the UI to reflect the selected semester
            self.update_semester()
            return

        # If the file does not exist, prompt the user to select which semesters to create
        dialog = SemesterSelectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_semesters = dialog.get_selected_semesters()

            # If no semesters are selected, default to all standard semesters
            if not selected_semesters:
                QMessageBox.warning(self, "Warning", "No semesters selected. Defaulting to all semesters.")
                selected_semesters = ["Autumn", "Spring", "Annual"]

            # Initialise the storage handler for the new year
            self.storage_handler = DataPersistence(selected_year)
            # Create an empty dictionary for each selected semester in the data
            for semester_name in selected_semesters:
                self.storage_handler.data[semester_name] = {}

            # Save the initialized data structure to the JSON file
            self.storage_handler.save_data(self.storage_handler.data)

            # Now create Semester objects for each selected semester
            self.semesters = {
                semester_name: Semester(semester_name, self.storage_handler.year, self.storage_handler)
                for semester_name in selected_semesters
            }

            # Update the semester combo box with the selected semesters
            self.semester_combo.clear()
            self.semester_combo.addItems(selected_semesters)

            # Update the UI to reflect the selected semester
            self.update_semester()
        else:
            # If the user cancels, show an informational message
            QMessageBox.information(self, "Info", "Year change canceled.")

    def update_semester(self) -> None:
        """
        Updates the current semester based on the selected semester name from the combo box.

        This method performs the following actions:
        1. Retrieves the selected semester name from the combo box.
        2. Validates the existence of the selected semester and displays a warning if not found.
        3. Identifies semesters marked as "Sync Subject" dynamically from the storage handler's data.
        4. Loops through each identified sync semester and attempts to synchronize its data.
        5. Refreshes the table view by passing the updated Semester object to the `update_table` method.

        Returns:
            None
        """
        semester_name = self.semester_combo.currentText()
        if not semester_name:
            return

        semester = self.get_semester(semester_name)
        if semester is None:
            QMessageBox.warning(None, "Warning", f"Semester '{semester_name}' not found.")
            return
        assert semester is not None

        # Identify sync semesters dynamically by checking for "Sync Subject" in their data
        sync_semesters = [
            sem_name
            for sem_name, sem_data in self.storage_handler.data.items()
            if any(isinstance(subject, dict) and subject.get("Sync Subject", False) for subject in sem_data.values())
        ]

        # Loop through each sync semester and sync its data to dynamic semesters
        for sync_semester_name in sync_semesters:
            sync_semester = self.semesters.get(sync_semester_name)
            if not sync_semester:
                QMessageBox.critical(None, "Error", f"Sync semester '{sync_semester_name}' not found.")  # Debugging
                continue

        # Pass the Semester object to update_table to refresh the table view
        self.update_table(cast(Semester, semester))

    def update_table(self, semester: Semester | str):
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
        """
        update_table(self, semester)

    def resizeEvent(self, a0):
        """
        Handles the resize event for the application window.
        This method is triggered whenever the application window is resized.
        It ensures that the rows in the table are resized to fit their contents
        after the window's dimensions change.
        Args:
            a0 (QResizeEvent): The resize event object containing details about
            the resize operation.
        """

        super().resizeEvent(a0)

        self.table.resizeRowsToContents()

    def get_semester(self, semester_name: str) -> Semester:
        if semester_name not in self._semesters:
            print(f"Loading semester: {semester_name}")
            # Only load/create the Semester when first accessed
            self._semesters[semester_name] = Semester(semester_name, self.storage_handler.year, self.storage_handler)
        return self._semesters[semester_name]
