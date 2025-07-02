# src/controller/__init__.py
from .app_controller import AppController
from .handlers import AnalyticsHandler, AssignmentHandler, SubjectHandler
from .handlers.analytics_handler import get_all_subjects, get_summary

# Backward compatibility imports
from .handlers.assignment_handler import add_assignment, delete_assignment
from .handlers.subject_handler import add_subject, delete_subject, set_total_mark

__all__ = [
    # Main controller
    "AppController",
    # Handlers
    "AssignmentHandler",
    "SubjectHandler",
    "AnalyticsHandler",
    # Backward compatibility functions
    "add_assignment",
    "delete_assignment",
    "add_subject",
    "delete_subject",
    "set_total_mark",
    "get_all_subjects",
    "get_summary",
]
