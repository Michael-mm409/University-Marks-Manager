from .entry_logic import add_entry, calculate_exam_mark, delete_entry, manage_total_mark
from .subject_logic import add_subject, delete_subject
from .table_logic import sync_table_entries, update_table

__all__ = [
    "add_entry",
    "delete_entry",
    "calculate_exam_mark",
    "manage_total_mark",
    "add_subject",
    "delete_subject",
    "update_table",
    "sync_table_entries",
]
