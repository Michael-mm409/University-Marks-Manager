from tkinter import messagebox

def calculate_exam_mark(app):
    """Calculate the exam mark for the selected subject."""
    semester_name = app.sheet_var.get()
    subject_code = app.subject_code_entry.get()

    if not subject_code:
        app.messagebox.showerror("Error", "Please enter a Subject Code.")
        return
    
    exam_mark = app.semesters[semester_name].calculate_exam_mark(subject_code)
    
    app.update_treeview()
    if exam_mark is not None:
        messagebox.showinfo("Success", f"Exam Mark for {subject_code}: {exam_mark}")
    else:
        messagebox.showerror("Error", f"Subject {subject_code} not found.")
        app.update_treeview()