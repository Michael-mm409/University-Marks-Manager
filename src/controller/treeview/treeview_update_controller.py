def update_treeview(self):
    """Update the treeview widget in the application."""
    semester_name = self.sheet_var.get()
    semester = self.semesters[semester_name]
    treeview_data = semester.sort_subjects()  # Retrieve all subjects' data

    # Clear the existing rows in the Treeview
    for row in self.treeview.get_children():
        self.treeview.delete(row)

    # Insert the data into the Treeview
    for row in treeview_data:
        self.treeview.insert("", "end", values=row)
