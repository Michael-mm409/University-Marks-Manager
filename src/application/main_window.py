import os
from datetime import datetime
from pathlib import Path
from typing import cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QGridLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data_persistence import DataPersistence
from semester import Semester
from ui.semester_selection_dialog import SemesterSelectionDialog

from .entry_logic import add_entry, calculate_exam_mark, delete_entry, manage_total_mark
from .subject_logic import add_subject, delete_subject


class Application(QMainWindow):
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
        super().__init__()

        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.storage_handler = storage_handler
        self.semesters = {
            sem: Semester(sem, storage_handler.year, storage_handler) for sem in ["Autumn", "Spring", "Annual"]
        }

        # Main Widget
        self.central_widget = QWidget()

        # Dropdowns
        self.year_combo = QComboBox()
        self.semester_combo = QComboBox()

        # Labels
        self.year_label = None
        self.semester_label = None

        # Table (equivalent to Treeview)
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setWordWrap(True)

        # Entry Fields
        self.subject_code_entry = QLineEdit()
        self.subject_name_entry = QLineEdit()
        self.assessment_entry = QLineEdit()
        self.weighted_mark_entry = QLineEdit()
        self.mark_weight_entry = QLineEdit()

        # Buttons
        self.btn_add_entry = QPushButton("Add Entry", self)
        self.btn_delete_entry = QPushButton("Delete Entry", self)
        self.btn_calc = QPushButton("Calculate Exam Mark", self)
        self.btn_add_subject = QPushButton("Add Subject", self)
        self.btn_delete_subject = QPushButton("Delete Subject", self)
        self.btn_set_total_mark = QPushButton("Set Total Mark", self)  # New button for managing Total Mark

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

        self.setWindowTitle("University Marks Manager")
        self.setGeometry(100, 100, 1500, 900)

        # Main Widget
        self.setCentralWidget(self.central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QGridLayout()  # Use QGridLayout for dropdowns and labels
        button_layout = QGridLayout()  # Use QGridLayout for buttons
        entry_layout = QGridLayout()  # Use QGridLayout for entry fields
        self.setup_entry_fields(entry_layout)

        # Wrap the entry layout in a QWidget
        entry_widget = QWidget()
        entry_widget.setLayout(entry_layout)

        # Dropdowns
        self.setup_dropdowns()
        self.setup_labels()
        self.setup_tables()
        self.setup_buttons(button_layout)  # Pass button_layout to setup_buttons

        # Add labels and dropdowns to the form layout
        form_layout.addWidget(self.year_label, 0, 0)  # Row 0, Column 0
        form_layout.addWidget(self.year_combo, 0, 1)  # Row 0, Column 1
        form_layout.addWidget(self.semester_label, 0, 2)  # Row 0, Column 2
        form_layout.addWidget(self.semester_combo, 0, 3)  # Row 0, Column 3

        # Adjust column spans to ensure no overlap
        form_layout.setColumnStretch(1, 1)  # Stretch for year dropdown
        form_layout.setColumnStretch(3, 1)  # Stretch for semester dropdown

        # Add layouts to the main layout
        main_layout.addLayout(form_layout)  # Add form layout for dropdowns and labels
        main_layout.addWidget(self.table, stretch=1)  # Add the table
        main_layout.addWidget(entry_widget)  # Add the entry fields
        main_layout.addLayout(button_layout)  # Add the button layout

        self.central_widget.setLayout(main_layout)
        self.central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update_year()

        # Resize columns to fit content after updating the table
        self.table.resizeColumnsToContents()
        self.table.setFocus()

        self.table.itemSelectionChanged.connect(self.populate_entries_from_selection)

        self.table.resizeRowsToContents()

    def setup_dropdowns(self):
        """
        Sets up dropdown menus for selecting the year and semester in the application.

        This method initializes the year dropdown (`year_combo`) with a range of years
        spanning from two years before the current year to two years after the current year.
        It sets the default selected year to the current year and connects the dropdown's
        index change event to the `update_year` method.

        The semester dropdown (`semester_combo`) is populated with predefined semester options
        ("Autumn", "Spring", "Annual"). The default selected semester is set to the first option
        ("Autumn"), and the dropdown's index change event is connected to the `update_semester` method.

        Returns:
            None
        """
        current_year = datetime.now().year
        self.year_combo.addItems([str(year) for year in range(current_year - 2, current_year + 2)])
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentIndexChanged.connect(self.update_year)

        self.semester_combo.addItems(["Autumn", "Spring", "Annual"])
        if self.semester_combo.count() > 0:
            self.semester_combo.setCurrentIndex(0)  # Default to the first valid semester
        self.semester_combo.currentIndexChanged.connect(self.update_semester)

    def setup_labels(self):
        """
        Initializes and sets up the labels for the year and semester selection.

        This method creates QLabel objects for displaying prompts to the user
        to select a year and semester in the application interface.
        """
        self.year_label = QLabel("Select Year:")
        self.semester_label = QLabel("Select Semester:")

    def setup_tables(self):
        """
        Configures the table widget with predefined columns, headers, and settings.

        This method sets up the table with the following features:
        - Defines column headers for the table, including subject details and marks.
        - Sets the selection mode to allow single selection of rows.
        - Disables editing of table cells to prevent modifications.
        - Enables dynamic resizing of columns to stretch and fill the table width.
        - Activates word wrapping for better readability of cell content.

        Args:
            columns (list): A list of column names to be displayed in the table.
        """
        columns = [
            "Subject Code",
            "Subject Name",
            "Assessment",
            "Unweighted Mark",
            "Weighted Mark",
            "Mark Weight",
            "Total Mark",
        ]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing cells

        # Enable dynamic resizing of columns
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Stretch columns to fill the table width

        # Enable word wrapping for the table
        self.table.setWordWrap(True)

    def setup_entry_fields(self, entry_layout: QGridLayout):
        """
        Sets up entry fields in a grid layout for user input.

        This method dynamically arranges labels and corresponding input fields
        into a grid layout. Each label is paired with an input field, and the
        fields are organized into two rows based on the total number of fields.

        Args:
            entry_layout (QGridLayout): The grid layout where the labels and input
                fields will be added.

        Fields:
            - "Enter Subject Code:" paired with `self.subject_code_entry`
            - "Enter Assessment:" paired with `self.assessment_entry`
            - "Enter Weighted Mark:" paired with `self.weighted_mark_entry`
            - "Enter Mark Weight:" paired with `self.mark_weight_entry`

        Layout:
            - Labels are placed in even columns.
            - Input fields are placed in odd columns next to their respective labels.
            - Rows are determined dynamically based on the number of fields.
        """
        # Define labels and corresponding input fields
        fields = [
            ("Enter Subject Code:", self.subject_code_entry),
            ("Enter Assessment:", self.assessment_entry),
            ("Enter Weighted Mark:", self.weighted_mark_entry),
            ("Enter Mark Weight:", self.mark_weight_entry),
        ]

        # Dynamically arrange fields in two rows
        max_fields_per_row = (len(fields) + 1) // 2  # Calculate max fields per row
        for idx, (label_text, field) in enumerate(fields):
            row = idx // max_fields_per_row  # Determine row index
            col = (idx % max_fields_per_row) * 2  # Determine column index (leave space for labels)
            label = QLabel(label_text)

            # Add label and field to the grid layout
            entry_layout.addWidget(label, row, col)  # Add label

            entry_layout.addWidget(field, row, col + 1)  # Add input field

    def setup_buttons(self, button_layout: QGridLayout):
        """
        Sets up the buttons in the application by arranging them in a grid layout
        and connecting their signals to corresponding methods.

        Args:
            button_layout (QGridLayout): The grid layout to arrange the buttons.

        Buttons:
            - Add Subject: Adds a new subject to the application.
            - Delete Subject: Deletes an existing subject from the application.
            - Add Entry: Adds a new entry to the selected subject.
            - Delete Entry: Deletes an existing entry from the selected subject.
            - Calculate Exam Mark: Calculates the exam mark based on the entries.
            - Set Total Mark: Manages the total mark configuration.

        Layout:
            Buttons are dynamically arranged in two rows within the grid layout.

        Signal Connections:
            - btn_add_entry: Connected to the `add_entry` method.
            - btn_delete_entry: Connected to the `delete_entry` method.
            - btn_calc: Connected to the `calculate_exam_mark` method.
            - btn_add_subject: Connected to the `add_subject` method.
            - btn_delete_subject: Connected to the `delete_subject` method.
            - btn_set_total_mark: Connected to the `manage_total_mark` method.
        """
        buttons = [
            self.btn_add_subject,
            self.btn_delete_subject,
            self.btn_add_entry,
            self.btn_delete_entry,
            self.btn_calc,
            self.btn_set_total_mark,  # New button for managing Total Mark
        ]

        # Dynamically arrange buttons in two rows
        max_buttons_per_row = (len(buttons) + 1) // 2  # Calculate max buttons per row
        for idx, button in enumerate(buttons):
            row = idx // max_buttons_per_row  # Determine row index
            col = idx % max_buttons_per_row  # Determine column index
            button_layout.addWidget(button, row, col)  # Add button to the grid layout

        # Connect button signals
        self.btn_add_entry.clicked.connect(lambda: add_entry(self))
        self.btn_delete_entry.clicked.connect(lambda: delete_entry(self))
        self.btn_calc.clicked.connect(lambda: calculate_exam_mark(self))
        self.btn_add_subject.clicked.connect(lambda: add_subject(self))
        self.btn_delete_subject.clicked.connect(lambda: delete_subject(self))
        self.btn_set_total_mark.clicked.connect(lambda: manage_total_mark(self))  # Connect the new button

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
        Updates the application's state based on the selected year from the year combo box.
        Loads semesters from file if they exist, or prompts the user to select semesters if not.
        """
        selected_year = self.year_combo.currentText()

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
        Updates the semester data and synchronizes information between sync semesters
        and dynamic semesters. This method identifies sync semesters based on specific
        criteria and ensures their data is propagated to dynamic semesters.
        """
        semester_name = self.semester_combo.currentText()
        if not semester_name:
            return

        semester = self.semesters.get(semester_name)
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
        self.table.setRowCount(0)

        # Ensure semester is a Semester object
        if isinstance(semester, str):
            sem_obj = self.semesters.get(semester)
            if sem_obj is None:
                QMessageBox.warning(None, "Warning", f"Semester '{semester}' not found.")
                return
        else:
            sem_obj = semester

        # 1. Gather all subjects (including synced ones)
        subject_map = {}

        # Add normal subjects from the current semester
        for subject_code, subject in sem_obj.subjects.items():
            subject_map.setdefault(subject_code, []).append((subject, False))  # False = not synced

        # Add synced subjects from other semesters (if sync_subject is True)
        for sync_semester in self.semesters.values():
            if sync_semester is sem_obj:
                continue
            for code, subj in sync_semester.subjects.items():
                if getattr(subj, "sync_subject", False):
                    subject_map.setdefault(code, []).append((subj, True))  # True = synced

        # 2. Sort subject codes for display order
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
                # Summary row for the subject
                total_weighted_mark = sum(entry.weighted_mark for entry in subject.assignments)
                total_weight = sum(entry.mark_weight for entry in subject.assignments)
                exam_mark = subject.examinations.exam_mark if hasattr(subject, "examinations") else 0
                exam_weight = subject.examinations.exam_weight if hasattr(subject, "examinations") else 100
                all_rows.append(
                    [
                        f"Summary for {subject_code}",
                        f"Assessments: {len(subject.assignments)}",
                        f"Total Weighted: {total_weighted_mark:.2f}",
                        f"Total Weight: {total_weight:.0f}",
                        f"Total Mark: {total_mark:.0f}",
                        f"Exam Mark: {exam_mark:.2f}",
                        f"Exam Weight: {exam_weight:.0f}",
                        "Synced" if is_synced else "",
                    ]
                )
                # Separator row for visual separation
                all_rows.append(["=" * 25 for _ in range(8)])

        # 4. Insert rows into the table widget
        self.table.setRowCount(0)
        for row_data in all_rows:
            self.table.insertRow(self.table.rowCount())
            for col_index, cell_data in enumerate(row_data):
                table_item = QTableWidgetItem(cell_data)
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                self.table.setItem(self.table.rowCount() - 1, col_index, table_item)

        # Resize columns to fit content after populating
        self.table.resizeColumnsToContents()

    def wrap_text(self, text: str, max_chars) -> str:
        """
        Wraps the given text into lines with a maximum number of characters per line.
        Args:
            text (str): The input text to be wrapped.
            max_chars (int): The maximum number of characters allowed per line.
        Returns:
            str: The text wrapped into multiple lines, separated by newline characters.
        """

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:  # +1 for the space
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return "\n".join(lines)  # Join lines with a newline character

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
