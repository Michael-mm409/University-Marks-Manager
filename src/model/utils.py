from tkinter import messagebox, simpledialog
from typing import Any, Dict


def get_subject_data(semester, subject_code: str, subject_name: str = "", sync_source: bool = False) -> Dict[str, Any]:
    if semester.name not in semester.data_persistence.data:
        semester.data_persistence.data[semester.name] = {}

    # Use semester.name, not semester
    if subject_code not in semester.data_persistence.data[semester.name]:
        semester.data_persistence.data[semester.name][subject_code] = {
            "Subject Name": subject_name,
            "Assignments": [],
            "Total Mark": 0,
            "Examinations": {"Exam Mark": 0, "Exam Weight": 0},
            "Sync Source": sync_source,
        }

    return semester.data_persistence.data[semester.name][subject_code]


def validate_float(value: Any, error_message: str, default_value: float = 0) -> float:
    if value is None or value == "":
        messagebox.showwarning("Warning", f"No value entered. Defaulting to {default_value}.")
        return default_value
    try:
        return float(value)  # Return the valid float
    except ValueError:
        messagebox.showerror("Error", error_message)  # Show error message
        # Re-prompt the user for input
        return validate_float(
            simpledialog.askstring("Input", error_message + " Please enter a valid number."),
            error_message,
            default_value,
        )
