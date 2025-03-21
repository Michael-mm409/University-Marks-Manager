from os import path


def update_year(self, _event=None):
    """Update the year logic in the application."""
    # Import DataPersistence and Semester locally to avoid circular import
    from model import DataPersistence, Semester
    from view import ask_semesters  # Import the semester selection dialog

    original_year = self.year_var.get()  # Store the original year
    original_sheet_var = self.sheet_var.get()  # Store the original sheet_var
    file_path = f"./data/{original_year}.json"

    # Prompt the user to select semesters if the data file does not exist
    if not path.exists(file_path):
        selected_semesters = ask_semesters(self.root, self.icon_path)
        if not selected_semesters:  # User canceled the dialog
            print("No semesters selected. Reverting to original year and semester.")
            self.year_var.set(original_year)
            self.sheet_var.set(original_sheet_var)
            self.update_semester_menu()
            return
    else:
        selected_semesters = None  # Use existing data

    # Re-initialize the data persistence object and semesters
    self.data_persistence = DataPersistence(original_year, semesters=selected_semesters)
    self.semesters = {
        semester_name: Semester(semester_name, self.data_persistence.year, self.data_persistence)
        for semester_name in self.data_persistence.data
    }

    # Check if any semester has the Sync Source flag set to true
    sync_source_semester = None
    for semester_name, semester_data in self.data_persistence.data.items():
        if semester_data.get("Sync Source", False):
            sync_source_semester = semester_name
            break

    # Set sheet_var to the semester with Sync Source = true, or fallback to the first key
    if sync_source_semester:
        self.sheet_var.set(sync_source_semester)
    else:
        first_key = sorted(self.data_persistence.data.keys())[0]
        self.sheet_var.set(first_key)

    print(f"Year: {original_year}, Semesters: {list(self.semesters.keys())}")
    print(f"Sheet var: {self.sheet_var.get()}")

    # Update the semester menu
    self.update_semester_menu()
    self.update_treeview()
