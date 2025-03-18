from tkinter import messagebox

from semester import Semester
from ui import ask_add_semester, ask_confirm


def update_semester(self, _event=None):
    """Update the semester logic in the application."""
    # Refresh the semester data from data_persistence
    self.semesters = {
        semester_name: Semester(semester_name, self.data_persistence.year, self.data_persistence)
        for semester_name in self.data_persistence.data
    }
    self.update_treeview()
    print("Updated semesters:", self.semesters.keys())


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


def remove_semester(self):
    """Removes the selected semester from the application."""
    semester_name = self.sheet_var.get()
    if semester_name:
        conformation = ask_confirm(
            parent=self.root,
            title="Confirm Removal",
            message=f"Are you sure you want to remove '{semester_name}'?",
            icon_path=self.icon_path,
        )

        # If the user does not want to remove semester, return
        if not conformation:
            return

        self.data_persistence.remove_semester(semester_name)
        if semester_name in self.semesters:
            del self.semesters[semester_name]
        self.update_semester()
        self.update_semester_menu()
        self.update_treeview()
        messagebox.showinfo("Success", f"Semester '{semester_name}' has been removed.")


def update_semester_menu(self):
    """Update the semester menu with the current semesters."""
    self.semester_menu.configure(values=sorted(self.semesters.keys()))

    # Set the first semester as the default selection
    if self.semesters:
        self.sheet_var.set(sorted(self.semesters.keys())[0])
