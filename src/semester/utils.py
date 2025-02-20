from tkinter import messagebox
from typing import Any, Dict

def get_subject_data(semester, subject_code: str, subject_name: str = "", sync_source: bool = False) -> Dict[str, Any]:
    if semester not in semester.data_persistence.data:
        semester.data_persistence.data[semester] = {}

    if subject_code not in semester.data_persistence.data[semester]:
        semester.data_persistence.data[semester][subject_code] = {
            "Subject Name": subject_name,
            "Assignments": [],
            "Total Mark": semester.data_persistence.data[semester].get("Total Mark", 0),
            "Examinations": {
                "Exam Mark": semester.data_persistence.data[semester][subject_code]["Examinations"].get("Exam Mark", 0),
                "Exam Weight": semester.data_persistence.data[semester][subject_code]["Examinations"].get("Exam Weight", 0)
            },
            "Sync Source": sync_source
        }
    return semester.data_persistence.data[semester][subject_code]

def validate_float(value: Any, error_message: str) -> float:
    if value is None or value == "":
        return 0
    try:
        return float(value)
    except ValueError:
        messagebox.showerror("Error", error_message)
        return -1