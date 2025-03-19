from model import Semester


def update_semester(self, _event=None):
    """Update the semester logic in the application."""
    # Refresh the semester data from data_persistence
    self.semesters = {
        semester_name: Semester(semester_name, self.data_persistence.year, self.data_persistence)
        for semester_name in self.data_persistence.data
    }
    self.update_treeview()
    print("Updated semesters:", self.semesters.keys())


def update_semester_menu(self):
    """Update the semester menu with the current semesters."""
    self.semester_menu.configure(values=sorted(self.semesters.keys()))

    # Set the first semester as the default selection
    if self.semesters:
        self.sheet_var.set(sorted(self.semesters.keys())[0])
