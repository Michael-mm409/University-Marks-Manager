from tkinter import messagebox


def calculate_exam_mark(self):
    """Calculate the exam mark for the selected subject."""
    semester_name = self.sheet_var.get()
    subject_code = self.subject_code_entry.get()

    if not subject_code:
        self.messagebox.showerror("Error", "Please enter a Subject Code.")
        return

    exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)

    self.update_treeview()
    if exam_mark is not None:
        messagebox.showinfo("Success", f"Exam Mark for {subject_code}: {exam_mark}")
    else:
        messagebox.showerror("Error", f"Subject {subject_code} not found.")
        self.update_treeview()


def add_total_mark(self):
    """Add the total mark for the selected subject."""
    semester_name = self.sheet_var.get()
    subject_code = self.subject_code_entry.get()

    if not subject_code:
        messagebox.showerror("Error", "Please enter a Subject Code.")
        return

    total_mark = self.semesters[semester_name].add_total_mark(subject_code)

    self.update_treeview()
    if total_mark is not None:
        messagebox.showinfo("Success", f"Total Mark for {subject_code}: {total_mark}")
    else:
        messagebox.showerror("Error", f"Subject {subject_code} not found.")
        self.update_treeview()
