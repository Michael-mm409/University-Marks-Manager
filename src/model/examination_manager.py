from tkinter import messagebox


class ExaminationManager:
    def __init__(self, semester):
        self.semester = semester

    def add_total_mark(self, subject_code: str, total_mark: float) -> None:
        sem_data = self.semester.data_persistence.data.get(self.semester.name, {})
        if subject_code in sem_data:
            self.semester.data_persistence.data[self.semester.name][subject_code]["Total Mark"] = total_mark
            self.semester.data_persistence.save_data()
        else:
            messagebox.showerror("Error", f"Subject '{subject_code}' not found.")
