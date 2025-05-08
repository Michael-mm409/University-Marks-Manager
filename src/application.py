"""
This module contains the Application class which is responsible for managing the
user interface of the University Marks Manager application. It also includes the
ToolTip class for displaying tooltips when hovering over a Treeview cell.
"""
from datetime import datetime
from os import path
from pathlib import Path
from typing import Any
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QTableWidget, QComboBox, QLineEdit, QMessageBox,
    QAbstractItemView, QDialog, QCheckBox, QHeaderView, QInputDialog, QTableWidgetItem, QSizePolicy
)

from ui.subject_dialog import AddSubjectDialog, confirm_remove_subject

from data_persistence import DataPersistence
from semester import Semester


class Application(QMainWindow):
    def __init__(self, storage_handler: DataPersistence):
        super().__init__()

        self.setWindowIcon(QIcon('assets/app_icon.png'))
        self.storage_handler = storage_handler
        self.semesters = {
            sem: Semester(sem, storage_handler.year, storage_handler)
            for sem in ["Autumn", "Spring", "Annual"]
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
        Initialize the user interface for the University Marks Manager application.
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
        current_year = datetime.now().year
        self.year_combo.addItems([str(year) for year in range(current_year - 2, current_year + 2)])
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentIndexChanged.connect(self.update_year)

        self.semester_combo.addItems(["Autumn", "Spring", "Annual"])
        if self.semester_combo.count() > 0:
            self.semester_combo.setCurrentIndex(0)  # Default to the first valid semester
        self.semester_combo.currentIndexChanged.connect(self.update_semester)

    def setup_labels(self):
        self.year_label = QLabel("Select Year:")
        self.semester_label = QLabel("Select Semester:")

    def setup_tables(self):
        columns = ["Subject Code", "Subject Name", "Assessment", "Unweighted Mark",
                   "Weighted Mark", "Mark Weight", "Total Mark"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing cells

        # Enable dynamic resizing of columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Stretch columns to fill the table width

        # Enable word wrapping for the table
        self.table.setWordWrap(True)

    def setup_entry_fields(self, entry_layout: QGridLayout):
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
            entry_layout.addWidget(label, row, col)       # Add label
            entry_layout.addWidget(field, row, col + 1)  # Add input field

    def setup_buttons(self, button_layout: QGridLayout):
        buttons = [
            self.btn_add_subject,
            self.btn_delete_subject,
            self.btn_add_entry,
            self.btn_delete_entry,
            self.btn_calc,
            self.btn_set_total_mark  # New button for managing Total Mark
        ]

        # Dynamically arrange buttons in two rows
        max_buttons_per_row = (len(buttons) + 1) // 2  # Calculate max buttons per row
        for idx, button in enumerate(buttons):
            row = idx // max_buttons_per_row  # Determine row index
            col = idx % max_buttons_per_row  # Determine column index
            button_layout.addWidget(button, row, col)  # Add button to the grid layout

        # Connect button signals
        self.btn_add_entry.clicked.connect(self.add_entry)
        self.btn_delete_entry.clicked.connect(self.delete_entry)
        self.btn_calc.clicked.connect(self.calculate_exam_mark)
        self.btn_add_subject.clicked.connect(self.add_subject)
        self.btn_delete_subject.clicked.connect(self.delete_subject)
        self.btn_set_total_mark.clicked.connect(self.manage_total_mark)  # Connect the new button

    def populate_entries_from_selection(self):
        selected_rows = self.table.selectionModel().selectedRows()
        # print(f"Selected rows: {selected_rows}")  # Debugging

        if selected_rows:
            row = selected_rows[0].row()  # Get the first selected row
            # print(f"Selected row: {row}")  # Debugging

            subject_code_item = self.table.item(row, 0)
            assessment_name_item = self.table.item(row, 2)

            if subject_code_item and assessment_name_item:
                subject_code = subject_code_item.text()
                assessment_name = assessment_name_item.text()
                # print(f"Subject Code: {subject_code}, Assessment Name: {assessment_name}")  # Debugging

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
                self.weighted_mark_entry.setText(self.table.item(row, 4).text())
                self.mark_weight_entry.setText(self.table.item(row, 5).text().replace("%", ""))
            else:
                print("Invalid or empty items in the selected row.")
        else:
            print("No rows selected.")

    def update_year(self):
        selected_year = self.year_combo.currentText()

        # Check if the JSON file for the selected year exists
        json_file_path = Path(f"data/{selected_year}.json")
        if path.exists(json_file_path):
            # If the file exists, load the data and update the storage handler
            self.storage_handler = DataPersistence(selected_year)
            # Dynamically gather semester names from JSON keys
            self.semesters = {semester_name: Semester(semester_name, selected_year, self.storage_handler)
                              for semester_name in self.storage_handler.data.keys()}

            # Clear and populate with dynamic semester names
            self.semester_combo.clear()

            # Add all keys (semesters) dynamically from JSON data
            self.semester_combo.addItems(self.semesters.keys())

            print("Semesters in file:", self.storage_handler.data.keys())
            print("Self.semesters populated as:", self.semesters.keys())
            self.update_semester()
            return

        # Show the semester selection dialogue if the file does not exist
        dialog = SemesterSelectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_semesters = dialog.get_selected_semesters()

            if not selected_semesters:
                QMessageBox.warning(self, "Warning", "No semesters selected. Defaulting to all semesters.")
                selected_semesters = ["Autumn", "Spring", "Annual"]

            # Initialise the storage handler and create empty semesters
            self.storage_handler = DataPersistence(selected_year)
            for semester_name in selected_semesters:
                self.storage_handler.data[semester_name] = {}  # Create an empty dictionary for the semester

            # Save the initialised data and update the semesters
            self.storage_handler.save_data()
            self.semesters = {
                semester_name: Semester(semester_name, self.storage_handler.year, self.storage_handler)
                for semester_name in selected_semesters
            }

            # Update the semester combo box with the selected semesters
            self.semester_combo.clear()
            self.semester_combo.addItems(selected_semesters)

            self.update_semester()
        else:
            QMessageBox.information(self, "Info", "Year change canceled.")

    def update_semester(self):
        semester_name = self.semester_combo.currentText()
        if not semester_name:
            # QMessageBox.warning(self, "Warning", "No semester selected. Please select a semester.")
            return
        semester = self.semesters.get(semester_name)
        # if semester is None:
        #     QMessageBox.warning(self, "Warning", f"Semester '{semester_name}' not found. Please check the data.")
        #     return

        # Identify sync semesters dynamically based on a property or predefined logic
        sync_semesters = [
            sem_name for sem_name, sem_data in self.storage_handler.data.items()
            if sem_data.get("Sync Subject", "").lower()  # Assuming "type": "sync" is in the JSON structure
        ]

        # Identify dynamic semesters by excluding sync semesters
        dynamic_semesters = [
            sem_name for sem_name in self.storage_handler.data.keys()
            if sem_name not in sync_semesters
        ]
        print(f"Dynamic semesters: {dynamic_semesters}")

        # Loop through each sync semester and sync its data to dynamic semesters
        for sync_semester_name in sync_semesters:
            sync_semester = self.semesters.get(sync_semester_name)
            if not sync_semester:
                continue  # Skip if the sync semester is not present in self.semesters

            sync_data = sync_semester.view_data()
            for semester_name in dynamic_semesters:
                semester = self.semesters.get(semester_name)
                if not semester:
                    continue  # Skip if the semester does not exist in self.semesters

                # Sync data to the dynamic semester
                for row_data in sync_data:
                    subject_code = row_data[0]

                    if "Summary" not in subject_code and "=" not in subject_code:
                        # Add data to the semester if it doesn't already contain the subject code
                        if subject_code not in semester.data:
                            semester.data[subject_code] = \
                                sync_semester.get_subject_data(sync_semester_name, subject_code)

        # Pass the Semester object to update_table
        self.update_table(semester)

    def update_table(self, semester: Semester | str):
        """Update the table with new data, simulate text wrapping, and add tooltips."""
        self.table.setRowCount(0)  # Clear existing rows

        # Retrieve all subjects, including synced subjects
        synced_subjects = semester.get_synced_subjects() if isinstance(semester, Semester) else []
        all_data = semester.view_data() + [
            [subject["Subject Code"], subject["Name"], "Synced Subject", "", "", "", ""]
            for subject in synced_subjects
        ]

        # Insert new rows with data
        for row_index, row_data in enumerate(all_data):
            self.table.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                table_item = QTableWidgetItem(cell_data)

                # Check if the row is a separator line
                if "=" in cell_data.strip():
                    # Center the separator line vertically and horizontally
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
                else:
                    # Default alignment for other rows
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

                self.table.setItem(row_index, col_index, table_item)

            # Adjust row height for wrapped text
            self.table.resizeRowToContents(row_index)

        # Resize columns to fit content
        self.table.resizeColumnsToContents()

    def wrap_text(self, text: str, max_chars):
        """Manually wrap text to fit within a maximum character limit."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:  # +1 for the space
                current_line += (word + " ")
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return "\n".join(lines)  # Join lines with a newline character

    def resizeEvent(self, event):
        """Handle window resizing and adjust row heights and column widths dynamically."""
        super().resizeEvent(event)

        self.table.resizeRowsToContents()

    def add_subject(self):
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name, "Unknown")

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
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name, "Unknown")

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
            self.storage_handler.save_data()  # Save changes
            self.update_table(semester)  # Refresh the table
        except ValueError as error:
            QMessageBox.critical(self, "Error", f"Failed to delete subject: {error}")

    def add_entry(self):
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name)

        if not semester:
            QMessageBox.warning(self, "Error", f"Semester '{semester_name}' not found.")
            return

        subject_code = self.subject_code_entry.text().strip()
        assessment = self.assessment_entry.text().strip()
        weighted_mark = self.weighted_mark_entry.text().strip()
        mark_weight = self.mark_weight_entry.text().strip()

        # Validate and convert input values to float
        weighted_mark = self.__validate_float(weighted_mark, "Weighted Mark must be a valid number.")
        mark_weight = self.__validate_float(mark_weight, "Mark Weight must be a valid number.")

        if weighted_mark == -1 or mark_weight == -1:
            return  # Exit if any of the values are invalid

        # Check if the subject exists in the current semester
        target_semester = semester
        # Search for the subject in other semesters
        for other_semester_name, other_semester in self.semesters.items():
            if subject_code in other_semester.data:
                target_semester = other_semester
                break

        # If the subject belongs to a different semester, show a warning
        if target_semester != semester:
            QMessageBox.warning(
                self,
                "Warning",
                f"Subject '{subject_code}' belongs to the '{target_semester.name}' semester. "
                "Please switch to that semester to modify or add entries for this subject."
            )
            return

        try:
            # Add or update the entry in the target semester
            target_semester.add_entry(
                semester=target_semester.name,
                subject_code=subject_code,
                subject_assessment=assessment,
                weighted_mark=weighted_mark,
                mark_weight=mark_weight
            )

            # Sync the changes back to the current semester
            self.sync_table_entries(current_semester=semester, synced_semester=target_semester)

            # Refresh the table for the current semester
            self.update_table(semester)

            QMessageBox.information(
                self,
                "Success",
                f"Entry added or updated for subject '{subject_code}' in semester '{target_semester.name}'."
            )
        except ValueError as error:
            QMessageBox.critical(self, "Error", f"Failed to add or update entry: {error}")

    @staticmethod
    def __validate_float(value: Any, error_message: str) -> float:
        """Validate the input value and return it as a float."""
        if value is None or value == "":
            return 0.0
        try:
            return float(value)
        except ValueError:
            QMessageBox.critical(None, "Error", error_message)
            return -1

    def delete_entry(self):
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name, "Unknown")

        selected_rows = self.table.selectionModel().selectedRows()
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
                    for synced_semester_name, synced_semester in self.semesters.items():
                        if synced_semester != semester and subject_code in synced_semester.data:
                            self.sync_table_entries(semester, synced_semester)

                except ValueError as error:
                    QMessageBox.critical(self, "Error", f"Failed to delete entry: {error}")
            else:
                QMessageBox.warning(self, "Error", "Failed to retrieve subject code or assessment.")

        # Refresh the table for the current semester
        self.update_table(semester)

    def calculate_exam_mark(self):
        semester_name = self.semester_combo.currentText()
        subject_code = self.subject_code_entry.text()

        if not subject_code:
            QMessageBox.critical(self, "Error", "Please enter a Subject Code.")
            return

        exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)
        self.update_table(self.semesters[semester_name])

        if exam_mark is None:
            QMessageBox.critical(self, "Error", f"Subject {subject_code} not found.")

    def manage_total_mark(self):
        """Set or clear the Total Mark for the subject specified in the entry fields."""
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
        if subject_code not in semester.data:
            # Search for the subject in other semesters
            for other_semester_name, other_semester in self.semesters.items():
                if subject_code in other_semester.data:
                    target_semester = other_semester
                    break

            if target_semester == semester:
                QMessageBox.critical(self, "Error", f"Subject '{subject_code}' not found in any semester.")
                return

        # Prompt the user to set or clear the Total Mark
        total_mark, ok = QInputDialog.getDouble(
            self, "Set Total Mark", f"Enter Total Mark for {subject_code}:", decimals=2
        )

        if ok:  # If the user clicks OK, set the Total Mark
            try:
                target_semester.data[subject_code]["Total Mark"] = total_mark
                self.storage_handler.save_data()  # Save changes
                self.update_table(semester)  # Refresh the table for the current semester
                QMessageBox.information(
                    self,
                    "Success",
                    f"Total Mark for '{subject_code}' set to {total_mark} in semester '{target_semester.name}'."
                )
            except KeyError:
                QMessageBox.critical(self, "Error", f"Failed to set Total Mark for {subject_code}.")
        else:  # If the user cancels, clear the Total Mark
            try:
                target_semester.data[subject_code]["Total Mark"] = 0
                self.storage_handler.save_data()  # Save changes
                self.update_table(semester)  # Refresh the table for the current semester
                QMessageBox.information(
                    self,
                    "Success",
                    f"Total Mark for '{subject_code}' cleared in semester '{target_semester.name}'."
                )
            except KeyError:
                QMessageBox.critical(self, "Error", f"Failed to clear Total Mark for {subject_code}.")

    @staticmethod
    def sync_table_entries(current_semester: Semester, synced_semester: Semester):
        """
        Synchronize the table entries between the current semester and the synced semester.

        Args:
            current_semester (Semester): The current semester displayed in the table.
            synced_semester (Semester): The synced semester to pull data from.
        """
        for subject_code, subject_data in synced_semester.data.items():
            if subject_code not in current_semester.data:
                # Add the subject to the current semester in memory (not saved to JSON)
                current_semester.data[subject_code] = {
                    "Subject Name": subject_data["Subject Name"],
                    "Assignments": subject_data["Assignments"],
                    "Total Mark": subject_data["Total Mark"],
                    "Examinations": subject_data["Examinations"]
                }
            else:
                # Update the current semester's data with the synced semester's data
                current_subject_data = current_semester.data[subject_code]
                for assignment in subject_data["Assignments"]:
                    # Check if the assignment already exists in the current semester
                    existing_assignment = next(
                        (assessment for assessment in current_subject_data["Assignments"]
                         if assessment["Subject Assessment"] == assignment["Subject Assessment"]),
                        None
                    )
                    if existing_assignment:
                        # Update the existing assignment
                        existing_assignment.update(assignment)
                    else:
                        # Add the new assignment
                        current_subject_data["Assignments"].append(assignment)


class SemesterSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Semesters")
        self.setGeometry(300, 300, 400, 200)  # Adjusted height to fit the new field

        # Layout
        self.layout = QVBoxLayout()

        # Checkboxes for predefined semesters
        self.autumn_checkbox = QCheckBox("Autumn")
        self.spring_checkbox = QCheckBox("Spring")
        self.annual_checkbox = QCheckBox("Annual")

        # Add checkboxes to the layout
        self.layout.addWidget(self.autumn_checkbox)
        self.layout.addWidget(self.spring_checkbox)
        self.layout.addWidget(self.annual_checkbox)

        # Input field for custom semesters
        self.custom_semester_label = QLabel("Custom Semesters (comma-separated):")
        self.custom_semester_input = QLineEdit()
        self.layout.addWidget(self.custom_semester_label)
        self.layout.addWidget(self.custom_semester_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add buttons to the layout
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_semesters(self):
        """Return a list of selected semesters, including custom ones."""
        checkboxes = {
            "Autumn": self.autumn_checkbox.isChecked(),
            "Spring": self.spring_checkbox.isChecked(),
            "Annual": self.annual_checkbox.isChecked()
        }
        selected_semesters = [semester for semester, checkbox in checkboxes.items() if checkbox]

        # Add custom semesters
        custom_semesters = [
            semester.strip() for semester in self.custom_semester_input.text().split(",") if semester.strip()
        ]
        selected_semesters.extend(custom_semesters)

        return selected_semesters