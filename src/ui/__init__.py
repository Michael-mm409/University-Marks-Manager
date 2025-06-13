# Package-level variables and imports for the application module.
__version__ = "1.0.0"
__author__ = "Michael McMillan"

# Common imports used across the application
from .semester_selection_dialog import SemesterSelectionDialog
from .subject_dialog import AddSubjectDialog, DeleteSubjectDialog

# Package-level exports
__all__ = [
    "__version__",
    "__author__",
    "SemesterSelectionDialog",
    "AddSubjectDialog",
    "DeleteSubjectDialog"
]
