from PyQt6.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class SemesterSelectionDialog(QDialog):
    """
    A dialog for selecting predefined semesters and entering custom semesters.

    This dialog provides checkboxes for predefined semesters (Autumn, Spring, Annual)
    and an input field for entering custom semesters as a comma-separated list.
    It also includes OK and Cancel buttons for user interaction.

    Methods:
        __init__(parent=None):
            Initializes the dialog with checkboxes, input field, and buttons.

        get_selected_semesters():
            Returns a list of selected semesters, including custom ones entered
            in the input field.

    Attributes:
        autumn_checkbox (QCheckBox): Checkbox for selecting the "Autumn" semester.
        spring_checkbox (QCheckBox): Checkbox for selecting the "Spring" semester.
        annual_checkbox (QCheckBox): Checkbox for selecting the "Annual" semester.
        custom_semester_label (QLabel): Label for the custom semester input field.
        custom_semester_input (QLineEdit): Input field for entering custom semesters.
        ok_button (QPushButton): Button to confirm the selection.
        cancel_button (QPushButton): Button to cancel the selection.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Semesters")
        self.setGeometry(300, 300, 400, 200)  # Adjusted height to fit the new field

        # Layout
        self.main_layout = QVBoxLayout()

        # Checkboxes for predefined semesters
        self.autumn_checkbox = QCheckBox("Autumn")
        self.spring_checkbox = QCheckBox("Spring")
        self.annual_checkbox = QCheckBox("Annual")

        # Add checkboxes to the layout
        self.main_layout.addWidget(self.autumn_checkbox)
        self.main_layout.addWidget(self.spring_checkbox)
        self.main_layout.addWidget(self.annual_checkbox)

        # Input field for custom semesters
        self.custom_semester_label = QLabel("Custom Semesters (comma-separated):")
        self.custom_semester_input = QLineEdit()
        self.main_layout.addWidget(self.custom_semester_label)
        self.main_layout.addWidget(self.custom_semester_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add buttons to the layout
        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_semesters(self):
        """
        Retrieve a list of selected semesters, including predefined and custom ones.

        This method checks the state of predefined semester checkboxes (Autumn, Spring, Annual)
        and collects their names if they are selected. Additionally, it retrieves custom semester
        names entered by the user in a text input field, splitting them by commas and stripping
        any extra whitespace.

        Returns:
            list: A list of strings representing the selected semesters, including both predefined
              and custom semesters.
        """
        checkboxes = {
            "Autumn": self.autumn_checkbox.isChecked(),
            "Spring": self.spring_checkbox.isChecked(),
            "Annual": self.annual_checkbox.isChecked(),
        }
        selected_semesters = [semester for semester, checkbox in checkboxes.items() if checkbox]

        # Add custom semesters
        custom_semesters = [
            semester.strip() for semester in self.custom_semester_input.text().split(",") if semester.strip()
        ]
        selected_semesters.extend(custom_semesters)

        return selected_semesters
