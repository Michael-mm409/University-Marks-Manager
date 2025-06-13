from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class AddSubjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Subject")
        self.setGeometry(300, 300, 400, 150)  # Adjusted height to fit the new field

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
        """
        Returns the entered subject data, including the optional custom semesters and sync status.
        """
        return (
            self.subject_code_input.text(),
            self.subject_name_input.text(),
            +self.sync_subject_checkbox.isChecked(),
        )


def confirm_remove_subject(self, subject_code: str):
    reply = QMessageBox.question(
        self,
        "Remove Subject",
        f"Are you sure you want to remove the subject '{subject_code}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes


class DeleteSubjectDialog(QDialog):
    def __init__(self, subjects, default_subject=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Subject from Semester")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select subject(s) to delete from this semester:"))
        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for subj in subjects:
            item = QListWidgetItem(subj)
            self.list_widget.addItem(item)
            if subj == default_subject:
                item.setSelected(True)
        layout.addWidget(self.list_widget)
        btn = QPushButton("Delete", self)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def selected_subjects(self):
        return [item.text() for item in self.list_widget.selectedItems()]
