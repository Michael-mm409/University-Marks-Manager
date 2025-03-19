from tkinter import messagebox

from view import ask_confirm


def remove_semester(self):
    """Removes the selected semester from the application."""
    semester_name = self.sheet_var.get()
    if semester_name:
        confirmation = ask_confirm(
            parent=self.root,
            title="Confirm Removal",
            message=f"Are you sure you want to remove '{semester_name}'?",
            icon_path=self.icon_path,
        )

        # If the user does not want to remove the semester, return
        if not confirmation:
            return

        # Remove the semester from data persistence
        self.data_persistence.remove_semester(semester_name)
        if semester_name in self.semesters:
            del self.semesters[semester_name]

        # Update the sheet_var to point to a valid semester
        if self.semesters:
            new_semester = sorted(self.semesters.keys())[0]  # Select the first available semester
            self.sheet_var.set(new_semester)
        else:
            self.sheet_var.set("")  # Clear the selection if no semesters are left

        # Update the UI
        self.update_semester()
        self.update_semester_menu()
        self.update_treeview()

        messagebox.showinfo("Success", f"Semester '{semester_name}' has been removed.")
