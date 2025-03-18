from view import ask_add_subject, ask_remove_subject


def add_subject(app):
    """Adds a new subject to the selected semester."""
    subject_code, subject_name, sync_source = ask_add_subject(
        parent=app.root, title="Add Subject", message="Enter the subject code and name:", icon_path=app.icon_path
    )

    if subject_code and subject_name:
        semester_name = app.sheet_var.get()
        app.semesters[semester_name].add_subject(subject_code, subject_name, sync_source)
        app.update_treeview()


def remove_subject(app):
    """Removes the selected subject from the selected semester."""
    subject_code = ask_remove_subject(
        parent=app.root, title="Remove Subject", message="Enter the subject code to remove:", icon_path=app.icon_path
    )
    if subject_code:
        semester_name = app.sheet_var.get()
        app.semesters[semester_name].remove_subject(subject_code)
        app.update_treeview()
