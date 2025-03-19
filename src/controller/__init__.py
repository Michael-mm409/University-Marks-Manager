# Import only frequently used functions or classes
from .entry.entry_logic import add_entry, delete_entry
from .exam import add_total_mark, calculate_exam_mark
from .semester import add_semester, remove_semester, update_semester, update_semester_menu, update_year
from .subject.subject_logic import remove_subject
from .treeview import on_treeview_motion, on_treeview_select, on_window_resize, update_treeview

# Avoid importing everything unless absolutely necessary
__all__ = [
    "add_entry",
    "delete_entry",
    "add_semester",
    "remove_semester",
    "update_semester",
    "remove_subject",
    "update_semester_menu",
    "update_treeview",
    "on_treeview_select",
    "on_treeview_motion",
    "on_window_resize",
    "update_year",
    "calculate_exam_mark",
    "add_total_mark",
]
