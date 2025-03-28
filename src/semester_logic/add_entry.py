from collections import OrderedDict
from tkinter import messagebox

from .utils import get_subject_data, validate_float


def add_entry(
    semester, subject_code, subject_name, subject_assessment, weighted_mark, mark_weight, sync_source=False
) -> None:
    """Add a new entry to the selected semester with assignment details."""
    # Check for a subject code.
    if not subject_code:
        messagebox.showerror("Error", "Subject Code is required!")
        return

    # Retrieve the subject data. This might be a normal dict from your JSON;
    # we now convert it to an OrderedDict with the desired key order.
    original_data = get_subject_data(semester, subject_code, subject_name)
    subject_data = OrderedDict(
        [
            ("Subject Name", original_data.get("Subject Name", subject_name)),
            ("Assignments", original_data.get("Assignments", [])),
            ("Total Mark", original_data.get("Total Mark", 0)),
            ("Examinations", original_data.get("Examinations", {"Exam Mark": 0, "Exam Weight": 100})),
            ("Sync Source", original_data.get("Sync Source", sync_source)),
        ]
    )

    # Validate weighted and mark weight.
    weighted_mark = validate_float(weighted_mark, "Weighted Mark must be a valid number.")
    mark_weight = validate_float(mark_weight, "Mark Weight must be a valid number.")
    if mark_weight < 0 or mark_weight > 100:
        messagebox.showerror("Error", "Mark Weight must be between 0 and 100.")
        return

    # Calculate unweighted mark.
    unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

    # Retrieve the list of assignments.
    assessments = subject_data.get("Assignments", [])
    for entry in assessments:
        if entry.get("Subject Assessment") == subject_assessment:
            entry.update(
                {"Unweighted Mark": unweighted_mark, "Weighted Mark": weighted_mark, "Mark Weight": mark_weight}
            )
            messagebox.showinfo("Success", "Assessment updated successfully!")
            # Reassign the ordered subject_data to storage and save.
            semester.data_persistence.data[semester.name][subject_code] = subject_data
            semester.data_persistence.save_data()
            break
    else:
        # Create a new assessment with ordered keys.
        new_assessment = OrderedDict(
            [
                ("Subject Assessment", subject_assessment),
                ("Unweighted Mark", unweighted_mark),
                ("Weighted Mark", weighted_mark if mark_weight != -1 else 0),
                ("Mark Weight", mark_weight if mark_weight != -1 else 0),
            ]
        )
        assessments.append(new_assessment)
        subject_data["Assignments"] = assessments
        messagebox.showinfo("Success", "Assessment added successfully!")
        if mark_weight != -1:
            subject_data["Examinations"]["Exam Weight"] -= mark_weight
        semester.data_persistence.data[semester.name][subject_code] = subject_data
        semester.data_persistence.save_data()

    # If sync_source is True, attempt to sync the entry to other semesters.
    if sync_source:
        for other_semester in semester.data_persistence.data:
            if other_semester != semester.name:
                try:
                    from semester import Semester

                    other_sem = Semester(other_semester, semester.year, semester.data_persistence)
                    other_sem.add_entry(
                        subject_code=subject_code,
                        subject_name=subject_name,
                        subject_assessment=subject_assessment,
                        weighted_mark=weighted_mark,
                        mark_weight=mark_weight,
                        sync_source=False,
                    )
                except Exception as e:
                    print(f"Error syncing entry to semester {other_semester}: {e}")
