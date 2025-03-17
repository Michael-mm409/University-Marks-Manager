from tkinter import simpledialog

from ui import ask_add_subject


def add_subject(app):
    """Adds a new subject to the selected semester."""
    subject_code, subject_name, sync_source = ask_add_subject(app.root)

    if subject_code and subject_name:
        semester_name = app.sheet_var.get()
        app.semesters[semester_name].add_subject(subject_code, subject_name, sync_source)
        app.update_treeview()


def remove_subject(app):
    """Removes the selected subject from the selected semester."""
    subject_code = simpledialog.askstring("Remove Subject", "Enter the subject code to remove:")
    if subject_code:
        semester_name = app.sheet_var.get()
        app.semesters[semester_name].remove_subject(subject_code)
        app.update_treeview()


def sort_subjects(app, sort_by="Subject Code"):
    """
    Sorts the subjects in the Treeview widget based on the selected field.

    Args:
        sort_by (str, optional): The field by which the subjects are sorted.
                                 Defaults to "Subject Code".
    """
    semester_name = app.sheet_var.get()
    semester = app.semesters[semester_name]

    treeview_data = semester.view_data(sort_by)

    # Sort by the chosen field (Subject Code, Subject Assessment, Weighted Mark, Mark Weight)
    if sort_by == "Subject Code":
        treeview_data.sort(key=lambda row: row[0])  # Sort by Subject Code (row[0])
    elif sort_by == "Subject Assessment":
        treeview_data.sort(key=lambda row: row[1])  # Sort by Subject Assessment (row[1])
    elif sort_by == "Weighted Mark":
        treeview_data.sort(key=lambda row: float(row[3]) if row[3] else 0)
    elif sort_by == "Mark Weight":
        treeview_data.sort(key=lambda row: float(row[4].replace("%", "")) if row[4] else 0)

    # Optionally display a success message
    app.messagebox.showinfo("Sorted", f"Subjects sorted by {sort_by}.")

    # Wipe the existing rows in the Treeview
    for row_id in app.treeview.get_children():
        app.treeview.delete(row_id)

    # Re-insert the rows in sorted order
    for row in treeview_data:
        app.treeview.insert("", "end", values=row)
