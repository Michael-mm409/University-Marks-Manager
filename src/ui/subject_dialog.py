from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox


class AddSubjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Subject")
        self.setGeometry(300, 300, 400, 300)  # Adjusted height to fit the new field

        # Layout
        layout = QVBoxLayout()

        # Input fields
        self.subject_code_label = QLabel("Subject Code:")
        self.subject_code_input = QLineEdit()
        self.subject_name_label = QLabel("Subject Name:")
        self.subject_name_input = QLineEdit()
        self.custom_semester_label = QLabel("Custom Semesters (comma-separated):")
        self.custom_semester_input = QLineEdit()

        layout.addWidget(self.subject_code_label)
        layout.addWidget(self.subject_code_input)
        layout.addWidget(self.subject_name_label)
        layout.addWidget(self.subject_name_input)
        layout.addWidget(self.custom_semester_label)
        layout.addWidget(self.custom_semester_input)

        # Checkbox to sync subject
        self.sync_subject_checkbox = QCheckBox("Sync Subject")
        layout.addWidget(self.sync_subject_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_subject_data(self):
        """
        Returns the entered subject data, including the optional custom semesters and sync status.
        """
        return (
            self.subject_code_input.text(),
            self.subject_name_input.text(),
            [semester.strip() for semester in self.custom_semester_input.text().split(",") if semester.strip()],
            self.sync_subject_checkbox.isChecked(),
        )


def confirm_remove_subject(self, subject_code: str):
    reply = QMessageBox.question(
        self,
        "Remove Subject",
        f"Are you sure you want to remove the subject '{subject_code}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes
