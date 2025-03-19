from view import ask_add_total_mark


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
