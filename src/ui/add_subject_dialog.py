from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton


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

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

    def get_subject_data(self):
        return self.subject_code_input.text(), self.subject_name_input.text()