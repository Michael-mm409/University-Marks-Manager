# Package-level variables and imports for the application module.
__version__ = "1.0.0"
__author__ = "Michael McMillan"

# Common imports used across the application.
from .entry_logic import (
    add_entry,
    delete_entry,
    calculate_exam_mark,
    manage_total_mark
)

from .main_window import Application

from .subject_logic import (
    add_subject,
    delete_subject
)

from .table_logic import (
    update_table,
    sync_table_entries
)

# Package-level exports.
__all__ = [
    "__version__",
    "__author__",
    "add_entry",
    "delete_entry",
    "calculate_exam_mark",
    "manage_total_mark",
    "Application",
    "add_subject",
    "delete_subject",
    "update_table",
    "sync_table_entries"
]
