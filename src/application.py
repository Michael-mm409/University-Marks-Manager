"""
This module contains the Application class which is responsible for managing the 
user interface of the University Marks Manager application. It also includes the
ToolTip class for displaying tooltips when hovering over a Treeview cell.
"""
from datetime import datetime
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QMessageBox, QAbstractItemView
)

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

        # Table (equivalent to Treeview)
        self.table = QTableWidget()

        # Entry Fields
        self.subject_code_entry = QLineEdit()
        self.assessment_entry = QLineEdit()
        self.weighted_mark_entry = QLineEdit()
        self.mark_weight_entry = QLineEdit()
        self.total_mark_entry = QLineEdit()

        # Buttons
        self.add_button = QPushButton("Add Entry", self)
        self.delete_button = QPushButton("Delete Entry", self)
        self.calc_button = QPushButton("Calculate Exam Mark", self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("University Marks Manager")
        self.setGeometry(100, 100, 800, 600)

        # Main Widget
        self.setCentralWidget(self.central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        entry_layout = QFormLayout()  # New layout for labels + inputs
        button_layout = QHBoxLayout()  # New layout for buttons

        # Dropdowns
        current_year = datetime.now().year
        self.year_combo.addItems([str(year) for year in range(current_year - 2, current_year + 2)])
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentTextChanged.connect(self.update_year)

        self.semester_combo.addItems(["Autumn", "Spring", "Annual"])
        self.semester_combo.currentTextChanged.connect(self.update_semester)

        # Labels
        year_label = QLabel("Select Year:")
        semester_label = QLabel("Select Semester:")

        # Table
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Subject Code", "Assessment", "Unweighted Mark", "Weighted Mark", "Mark Weight"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # Ensure row selection
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # Allow single row selection

        # Entry Field Labels
        subject_code_label = QLabel("Select Subject Code:")
        assessment_label = QLabel("Select Assessment:")
        weighted_mark_label = QLabel("Select Weighted Mark:")
        mark_weight_label = QLabel("Select Mark Weight:")
        total_mark_label = QLabel("Select Total Mark:")

        # Add Labels and Fields to entry Layout
        entry_layout.addRow(subject_code_label, self.subject_code_entry)
        entry_layout.addRow(assessment_label, self.assessment_entry)
        entry_layout.addRow(weighted_mark_label, self.weighted_mark_entry)
        entry_layout.addRow(mark_weight_label, self.mark_weight_entry)
        entry_layout.addRow(total_mark_label, self.total_mark_entry)

        # Buttons
        self.add_button.clicked.connect(self.add_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.calc_button.clicked.connect(self.calculate_exam_mark)

        # Add buttons to button layout
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.calc_button)

        # Wrap the entry layout in a QWidget
        entry_widget = QWidget()
        entry_widget.setLayout(entry_layout)

        # Wrap the button layout in a QWidget
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Layout Arrangements
        form_layout.addWidget(year_label)
        form_layout.addWidget(self.year_combo)
        form_layout.addWidget(semester_label)
        form_layout.addWidget(self.semester_combo)

        # Add layouts to the main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table, stretch=1)  # Add the table without explicit stretch
        main_layout.addWidget(entry_widget)  # Add the labels + input fields layout
        main_layout.addWidget(button_widget)  # Add the buttons

        self.central_widget.setLayout(main_layout)
        self.update_semester()

        # Resize columns to fit content after updating the table
        self.table.resizeColumnsToContents()

        self.table.itemSelectionChanged.connect(self.populate_entries_from_selection)

    def populate_entries_from_selection(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()

            subject_code = self.table.item(row, 0).text()
            if "=" in subject_code or "Summary" in subject_code:
                # Deselect the row if it contains the unwanted strings
                self.table.clearSelection()

                # Show a message box to inform the user
                # QMessageBox.warning(self, "Selection Restricted", "This row cannot be selected because it contains summary information.")
                return
            self.subject_code_entry.setText(subject_code)
            self.assessment_entry.setText(self.table.item(row, 1).text())
            self.weighted_mark_entry.setText(self.table.item(row, 3).text())
            self.mark_weight_entry.setText(self.table.item(row, 4).text().strip("%"))

    def update_year(self):
        selected_year = self.year_combo.currentText()
        self.storage_handler = DataPersistence(selected_year)
        self.semesters = {
            sem: Semester(sem, self.storage_handler.year, self.storage_handler)
            for sem in self.semesters.keys()
        }
        self.update_semester()

    def update_semester(self):
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name, "Unknown")
        self.update_table(semester)


    def update_table(self, semester: Semester | str):
        """ Update the table with new data and adjust row heights. """
        self.table.setRowCount(0)  # Clear existing rows

        # Insert new rows with data
        for row_data in semester.view_data():
            row_index = self.table.rowCount()  # Get the current row index
            self.table.insertRow(row_index)

            # Fill the row with data
            for col, item in enumerate(row_data):
                item_widget = QTableWidgetItem(str(item))
                self.table.setItem(row_index, col, item_widget)

        # Call to update row heights based on available space
        self.update_row_heights()

    def update_row_heights(self):
        """ Adjust row heights based on available space. """
        available_height = self.height() - self.table.horizontalHeader().height()
        num_rows = self.table.rowCount()

        if num_rows > 0:
            row_height = available_height // num_rows
            for row in range(num_rows):
                self.table.setRowHeight(row, row_height)
        else:
            for row in range(num_rows):
                self.table.setRowHeight(row, 20)  # Default height if no rows exist

        # Resize rows to fit content after adjusting heights
        self.table.resizeRowsToContents()

    def resizeEvent(self, event):
        """ Handle window resizing and adjust row heights accordingly. """
        super().resizeEvent(event)
        # Update row heights and font size when resizing the window
        self.update_row_heights()
        # self.adjust_table_font_size()

    def add_entry(self):
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name, "Unknown")

        subject_code = self.subject_code_entry.text()
        assessment = self.assessment_entry.text()
        weighted_mark = self.weighted_mark_entry.text()
        mark_weight = self.mark_weight_entry.text()
        total_mark = self.total_mark_entry.text()

        if total_mark == "":
            total_mark = 0

        try:
            semester.add_entry(
                semester=semester_name,
                subject_code=subject_code,
                subject_assessment=assessment,
                weighted_mark=float(weighted_mark),
                mark_weight=float(mark_weight),
                total_mark=float(total_mark)
            )
            self.storage_handler.save_data()  # Ensure data is saved after adding entry
            self.update_table(semester)
        except ValueError as error:
            QMessageBox.critical(self, "Error", f"Failed to add entry: {error}")

    def delete_entry(self):
        semester_name = self.semester_combo.currentText()
        semester = self.semesters.get(semester_name, "Unknown")

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Please select an entry to delete.")
            return

        print(f"Selected rows: {selected_rows}")  # Debugging information

        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            subject_code_item = self.table.item(row, 0)
            assessment_item = self.table.item(row, 1)

            if subject_code_item and assessment_item:
                subject_code = subject_code_item.text()
                assessment = assessment_item.text()
                print(f"Deleting entry: {subject_code}, {assessment}, row: {row}")  # Debugging information
                try:
                    semester.delete_entry(subject_code, assessment)
                    self.table.removeRow(row)
                except ValueError as error:
                    QMessageBox.critical(self, "Error", f"Failed to delete entry: {error}")
            else:
                QMessageBox.warning(self, "Error", "Failed to retrieve subject code or assessment.")

        self.storage_handler.save_data()  # Ensure data is saved after deleting entry
        QMessageBox.information(self, "Success", "Selected entry has been deleted")
        self.update_table(semester)

    def calculate_exam_mark(self):
        semester_name = self.semester_combo.currentText()
        subject_code = self.subject_code_entry.text()

        if not subject_code:
            QMessageBox.critical(self, "Error", "Please enter a Subject Code.")
            return

        exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)
        self.update_table(self.semesters[semester_name])

        if exam_mark is not None:
            QMessageBox.information(self, "Success", f"Exam Mark for {subject_code}: {exam_mark}")
        else:
            QMessageBox.critical(self, "Error", f"Subject {subject_code} not found.")

