from model import DataPersistence, Semester


def update_year(self, _event=None):
    """Update the year logic in the application."""
    selected_year = self.year_var.get()
    # Re-initialize the data persistence object and semesters
    self.data_persistence = DataPersistence(selected_year)
    self.semesters = {
        semester_name: Semester(semester_name, self.data_persistence.year, self.data_persistence)
        for semester_name in self.data_persistence.data
    }

    print(f"Year: {selected_year}, Semesters: {list(self.semesters.keys())}")

    # Update the semester menu
    self.update_semester_menu()
    self.update_treeview()
