from data_persistence import DataPersistence
from semester import Semester

def update_year(app, _event=None):
    """Update the year logic in the application."""
    selected_year = app.year_var.get()
    # Re-initialise the data persistence object and semesters
    app.data_persistence = DataPersistence(selected_year)
    app.semesters = {
        semester_name: Semester(semester_name, app.data_persistence.year, app.data_persistence,)
        for semester_name in app.data_persistence.data
    }

    app.update_semester()
    app.update_treeview()