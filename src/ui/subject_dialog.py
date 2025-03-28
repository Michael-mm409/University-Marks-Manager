from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox


class AddSubjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Subject")
        self.setGeometry(300, 300, 400, 200)

        # Layout
        layout = QVBoxLayout()

        # Input fields
        self.subject_code_label = QLabel("Subject Code:")
        self.subject_code_input = QLineEdit()
        self.subject_name_label = QLabel("Subject Name:")
        self.subject_name_input = QLineEdit()

        layout.addWidget(self.subject_code_label)
        layout.addWidget(self.subject_code_input)
        layout.addWidget(self.subject_name_label)
        layout.addWidget(self.subject_name_input)

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
        return self.subject_code_input.text(), self.subject_name_input.text()


def confirm_remove_subject(self, subject_code: str):
    reply = QMessageBox.question(
        self,
        "Remove Subject",
        f"Are you sure you want to remove the subject '{subject_code}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes