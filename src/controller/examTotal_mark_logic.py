from tkinter import messagebox

from view import ask_add_total_mark


def calculate_exam_mark(self):
    """Calculate the exam mark for the selected subject."""
    semester_name = self.sheet_var.get()
    subject_code = self.subject_code_entry.get()

    if not subject_code:
        messagebox.showerror("Error", "Please enter a Subject Code.")
        return

    exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)

    self.update_treeview()
    if exam_mark is None:
        messagebox.showerror("Error", f"Subject {subject_code} not found.")
        self.update_treeview()


def add_total_mark(self):
    """
    Add or update the total mark for a subject in the selected semester.
    """
    semester_name = self.sheet_var.get()
    subject_code = self.subject_code_entry.get()

    if not semester_name or not subject_code:
        messagebox.showerror("Error", "Semester and Subject Code are required.")
        return

    try:
        # Call the add_total_mark method in the Semester class
        self.semesters[semester_name].add_total_mark(subject_code, self.root)
        messagebox.showinfo("Success", f"Total mark for subject '{subject_code}' updated successfully.")
        self.update_treeview()
    except ValueError as error:
        messagebox.showerror("Error", str(error))

    def add_total_mark(self, subject_code: str, parent_window) -> None:
        """
        Add or update the total mark for a subject in the semester.

        Args:
            subject_code (str): The code of the subject.
            parent_window: The parent window for the dialog.

        Raises:
            ValueError: If the subject code is not found or the total mark is invalid.
        """
        # Retrieve the semester data
        sem_data = self.data_persistence.data.get(self.name, {})
        subject_data = sem_data.get(subject_code)

        if not subject_data:
            raise ValueError(f"Subject '{subject_code}' does not exist in semester '{self.name}'.")

        # Use the ask_add_total_mark dialog to get the total mark
        total_mark = ask_add_total_mark(
            parent_window,
            title="Add Total Mark",
            message="Enter the total mark:",
            icon_path="assets/app_icon.ico",  # Ensure the correct icon path is provided
        )
        if total_mark is None:
            raise ValueError("No total mark was provided.")

        # Validate the total mark
        if total_mark < 0 or total_mark > 100:
            raise ValueError("Total mark must be between 0 and 100.")

        # Update the total mark for the subject
        subject_data["Total Mark"] = total_mark
        self.data_persistence.data[self.name][subject_code] = subject_data
        self.data_persistence.save_data()
