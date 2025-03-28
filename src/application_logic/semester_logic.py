from tkinter import messagebox, simpledialog

from semester import Semester


def update_semester(self, _event=None):
    """Update the semester logic in the application."""
    selected_sheet = self.sheet_var.get()
    selected_year = self.year_var.get()
    if selected_sheet not in self.semesters:
        self.semesters[selected_sheet] = Semester(selected_sheet, selected_year, self.data_persistence)
    else:
        # Refresh the semester data from data_persistence
        self.semesters[selected_sheet] = Semester(selected_sheet, selected_year, self.data_persistence)
    self.update_treeview()
    print(self.semesters.keys())


def add_semester(self):
    """Adds a new semester to the application."""
    new_semester_name = simpledialog.askstring("Add Semester", "Enter the name of the new semester:")
    if new_semester_name:
        if new_semester_name in self.semesters:
            messagebox.showerror("Error", "Semester already exists!")
        else:
            self.semesters[new_semester_name] = Semester(new_semester_name, self.year_var.get(), self.data_persistence)
            self.sheet_var.set(new_semester_name)
            self.update_semester()
            self.update_semester_menu()


def remove_semester(self):
    """Removes the selected semester from the application."""
    semester_name = self.sheet_var.get()
    if semester_name:
        self.data_persistence.remove_semester(semester_name)
        if semester_name in self.semesters:
            del self.semesters[semester_name]
        self.update_semester()
        self.update_semester_menu()
        messagebox.showinfo("Success", f"Semester '{semester_name}' has been removed.")


def update_semester_menu(self):
    """Update the semester menu based on the data in data_persistence."""
    sheet_menu = self.semester_menu["menu"]
    sheet_menu.delete(0, "end")
    for semester_name in sorted(self.data_persistence.data.keys()):
        sheet_menu.add_command(label=semester_name, command=lambda value=semester_name: self.sheet_var.set(value))
    if self.data_persistence.data and not self.sheet_var.get():
        self.sheet_var.set(sorted(self.data_persistence.data.keys())[0])
