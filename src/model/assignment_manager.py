from collections import OrderedDict
from tkinter import messagebox


class AssignmentManager:
    def __init__(self, semester):
        self.semester = semester

    def add_assignment(
        self,
        subject_code: str,
        subject_assessment: str,
        weighted_mark: float,
        mark_weight: float,
    ) -> None:
        sem_data = self.semester.data_persistence.data.get(self.semester.name, {})
        subject_data = sem_data.get(subject_code)
        if not subject_data:
            messagebox.showerror(
                "Error", f"Subject '{subject_code}' does not exist in semester '{self.semester.name}'."
            )
            return

        # Validate weighted_mark and mark_weight
        try:
            weighted_mark = float(weighted_mark) if weighted_mark else 0.0
            mark_weight = float(mark_weight) if mark_weight else 0.0
        except ValueError:
            messagebox.showerror("Error", "Weighted Mark and Mark Weight must be valid numbers.")
            return

        if mark_weight < 0 or mark_weight > 100:
            messagebox.showerror("Error", "Mark Weight must be between 0 and 100.")
            return

        # Calculate unweighted mark
        unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

        # Check if the assessment already exists
        assignments = subject_data.get("Assignments", [])
        for entry in assignments:
            if entry.get("Subject Assessment") == subject_assessment:
                entry.update(
                    {"Unweighted Mark": unweighted_mark, "Weighted Mark": weighted_mark, "Mark Weight": mark_weight}
                )
                self.semester.data_persistence.data[self.semester.name][subject_code] = subject_data
                self.semester.data_persistence.save_data()
                messagebox.showinfo("Success", "Assessment updated successfully!")
                return

        # Add a new assessment
        new_assessment = OrderedDict(
            [
                ("Subject Assessment", subject_assessment),
                ("Unweighted Mark", unweighted_mark),
                ("Weighted Mark", weighted_mark),
                ("Mark Weight", mark_weight),
            ]
        )
        assignments.append(new_assessment)
        subject_data["Assignments"] = assignments
        self.semester.data_persistence.data[self.semester.name][subject_code] = subject_data
        self.semester.data_persistence.save_data()
        messagebox.showinfo("Success", "Assessment added successfully!")
