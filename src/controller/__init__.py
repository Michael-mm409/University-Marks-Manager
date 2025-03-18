# Import only frequently used functions or classes
from .entry_logic import add_entry, delete_entry
from .examTotal_mark_logic import add_total_mark, calculate_exam_mark
from .semester_logic import add_semester, remove_semester, update_semester, update_semester_menu
from .subject_logic import remove_subject
from .treeview_logic import on_treeview_motion, on_treeview_select, on_window_resize, update_treeview
from .year_logic import update_year

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
