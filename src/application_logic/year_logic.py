from data_persistence import DataPersistence
from semester import Semester


def update_year(self, _event=None):
    """Update the year logic in the selflication."""
    selected_year = self.year_var.get()
    # Re-initialise the data persistence object and semesters
    self.data_persistence = DataPersistence(selected_year)
    self.semesters = {
        semester_name: Semester(semester_name, self.data_persistence.year, self.data_persistence,)
        for semester_name in self.data_persistence.data
    }

    # self.update_semester_menu()
    self.update_semester()
    self.update_treeview()
