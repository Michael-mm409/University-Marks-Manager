from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QAbstractItemView, QGridLayout, QHeaderView, QLabel, QSizePolicy, QVBoxLayout, QWidget

from controller.entry_logic import add_entry, calculate_exam_mark, delete_entry, manage_total_mark
from controller.subject_logic import add_subject, delete_subject

if TYPE_CHECKING:
    from view import Application


class MainWindowUI:
    def setup_ui(self: "Application"):  # type: ignore
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

    def setup_dropdowns(self: "Application"):  # type: ignore
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

    def setup_labels(self: "Application"):  # type: ignore
        """
        Initializes and sets up the labels for the year and semester selection.

        This method creates QLabel objects for displaying prompts to the user
        to select a year and semester in the application interface.
        """
        self.year_label = QLabel("Select Year:")
        self.semester_label = QLabel("Select Semester:")

    def setup_tables(self: "Application"):  # type: ignore
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

    def setup_entry_fields(self: "Application", entry_layout: QGridLayout):  # type: ignore
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

    def setup_buttons(self: "Application", button_layout: QGridLayout):  # type: ignore
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
