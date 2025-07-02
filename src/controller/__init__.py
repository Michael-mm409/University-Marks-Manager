"""
Controller module initializer.

This package provides the central application controller and its supporting
handlers for managing subjects, assignments, and analytics.

Modules:
    - app_controller: Main entry point for coordinating app logic.
    - handlers.analytics_handler: Provides performance and subject-level analytics.
    - handlers.assignment_handler: Manages assignment CRUD operations.
    - handlers.subject_handler: Manages subject CRUD operations and total mark settings.

Backward Compatibility:
    Commonly used handler functions are re-exported at the package level
    to maintain backward compatibility with earlier imports.

Exports:
    - AppController
    - AnalyticsHandler
    - AssignmentHandler
    - SubjectHandler
    - add_assignment
    - delete_assignment
    - modify_assignment
    - add_subject
    - delete_subject
    - set_total_mark
    - get_all_subjects
    - get_summary
"""

from .app_controller import AppController

"""Main application controller for coordinating logic between handlers and UI."""

from .handlers import AnalyticsHandler, AssignmentHandler, SubjectHandler  # noqa: E402

"""Handler classes responsible for specific domains:
- `AnalyticsHandler`: Computes performance insights and summaries.
- `AssignmentHandler`: Manages assignment addition, deletion, and modification.
- `SubjectHandler`: Manages subject data and related settings like total marks.
"""

from .handlers.analytics_handler import get_all_subjects, get_summary  # noqa: E402

"""Utility functions for retrieving all subjects and generating summary analytics."""

from .handlers.assignment_handler import add_assignment, delete_assignment, modify_assignment  # noqa: E402

"""Functions for CRUD operations on assignments."""

from .handlers.subject_handler import add_subject, delete_subject, set_total_mark  # noqa: E402

"""Functions for managing subjects and setting total marks."""


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
    "modify_assignment",
]
