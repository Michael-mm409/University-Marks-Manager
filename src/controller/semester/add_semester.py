from tkinter import messagebox

from view import ask_add_semester


def add_semester(self):
    """Adds a new semester to the application."""
    new_semester_name = ask_add_semester(
        parent=self.root, title="Add Semester", message="Enter the name of the new semester:", icon_path=self.icon_path
    )
    if new_semester_name:
        if new_semester_name in self.semesters:
            messagebox.showerror("Error", "Semester already exists!")
        else:
            print("Adding new semester:", new_semester_name)
            self.data_persistence.add_semester(new_semester_name)
            self.sheet_var.set(new_semester_name)
            print("sheet_var set to:", self.sheet_var.get())
            print("Semesters before update:", self.semesters.keys())
            self.update_semester_menu()
            self.update_semester()
            print("New semester added:", new_semester_name)
            print("Current semesters:", self.semesters.keys())
