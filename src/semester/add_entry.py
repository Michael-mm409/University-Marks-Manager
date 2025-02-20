from tkinter import messagebox
from .utils import get_subject_data, validate_float

def add_entry(semester, subject_code, subject_name, subject_assessment,
              weighted_mark, mark_weight, total_mark, sync_source=False) -> None:
    """Add a new entry to the selected semester with assignment details."""
    if not subject_code:
        messagebox.showerror("Error", "Subject Code is required!")
        return

    subject_data = get_subject_data(semester, subject_code, subject_name, sync_source)

    total_mark = validate_float(total_mark, "Total Mark must be a valid number.")
    if total_mark != -1:
        subject_data["Total Mark"] = total_mark

    weighted_mark = validate_float(weighted_mark, "Weighted Mark must be a valid number.")
    mark_weight = validate_float(mark_weight, "Mark Weight must be a valid number.")
    if mark_weight < 0 or mark_weight > 100:
        messagebox.showerror("Error", "Mark Weight must be between 0 and 100.")
        return

    unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

    assessments = subject_data["Assignments"]
    for entry in assessments:
        if entry.get("Subject Assessment") == subject_assessment:
            entry.update({
                "Unweighted Mark": unweighted_mark,
                "Weighted Mark": weighted_mark,
                "Mark Weight": mark_weight
            })
            messagebox.showinfo("Success", "Assessment updated successfully!")
            semester.data_persistence.save_data()
            break
    else:
        new_assessment = {
            "Subject Assessment": subject_assessment,
            "Unweighted Mark": unweighted_mark,
            "Weighted Mark": weighted_mark if mark_weight != -1 else 0,
            "Mark Weight": mark_weight if mark_weight != -1 else 0
        }
        assessments.append(new_assessment)
        subject_data["Assignments"] = assessments
        messagebox.showinfo("Success", "Assessment added successfully!")
        if mark_weight != -1:
            subject_data["Examinations"]["Exam Weight"] -= mark_weight
        semester.data_persistence.save_data()

    if sync_source:
        for other_semester in semester.data_persistence.data:
            if other_semester != semester.name:
                try:
                    from semester import Semester
                    other_sem = Semester(other_semester, semester.year, semester.data_persistence)
                    other_sem.add_entry(
                        semester=other_semester,
                        subject_code=subject_code,
                        subject_name=subject_name,
                        subject_assessment=subject_assessment,
                        weighted_mark=weighted_mark,
                        mark_weight=mark_weight,
                        total_mark=total_mark,
                        sync_source=False
                    )
                except Exception as e:
                    print(f"Error syncing entry to semester {other_semester}: {e}")