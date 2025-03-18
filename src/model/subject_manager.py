from collections import OrderedDict
from tkinter import messagebox


class SubjectManager:
    def __init__(self, semester):
        self.semester = semester

    def add_subject(self, subject_code: str, subject_name: str, sync_source: bool = False) -> None:
        sem_data = self.semester.data_persistence.data.get(self.semester.name, {})
        if subject_code in sem_data:
            messagebox.showerror("Error", f"Subject '{subject_code}' already exists.")
            return

        subject_data = OrderedDict(
            [
                ("Subject Name", subject_name),
                ("Assignments", []),
                ("Examinations", {"Exam Mark": 0, "Exam Weight": 100}),
                ("Sync Source", sync_source),
                ("Total Mark", 0),
            ]
        )

        sem_data[subject_code] = subject_data
        self.semester.data_persistence.data[self.semester.name] = sem_data
        self.semester.data_persistence.save_data()

    def remove_subject(self, subject_code: str) -> None:
        sem_data = self.semester.data_persistence.data.get(self.semester.name, {})
        if subject_code in sem_data:
            del sem_data[subject_code]
            self.semester.data_persistence.data[self.semester.name] = sem_data
            self.semester.data_persistence.save_data()
        else:
            messagebox.showerror("Error", f"Subject '{subject_code}' not found.")
