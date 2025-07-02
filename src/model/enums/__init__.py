"""Enumeration package for the University Marks Manager model layer.

This package provides enumeration classes that define controlled vocabularies,
constants, and standardized values used throughout the University Marks Manager
application. Enums ensure data consistency, prevent invalid values, and provide
type-safe constants for academic data management.

Package Structure:
    The enums package contains three primary enumeration types:

    Assessment Categories:
        - GradeType: Standardized assessment categories and types

    Academic Periods:
        - SemesterName: Standardized semester naming conventions

    Data Access:
        - DataKeys: JSON field names and data structure constants

Purpose:
    - Data Consistency: Prevent invalid values through controlled vocabularies
    - Type Safety: Compile-time checking for enum usage
    - Standardization: Consistent naming across the application
    - Documentation: Self-documenting code through descriptive enum values
    - Maintenance: Centralized constant management

Design Benefits:
    - Immutable Values: Enum values cannot be changed at runtime
    - Namespace Isolation: Related constants grouped together
    - IDE Support: Enhanced autocomplete and error detection
    - Refactoring Safety: Centralized constant definitions
    - Clear Intent: Descriptive names improve code readability

Usage Patterns:
    >>> from model.enums import GradeType, SemesterName, DataKeys
    >>>
    >>> # Assessment categorization
    >>> assignment_type = GradeType.ASSIGNMENT
    >>> quiz_type = GradeType.QUIZ
    >>>
    >>> # Semester identification
    >>> current_semester = SemesterName.SESSION_1
    >>>
    >>> # Data access keys
    >>> subject_code_key = DataKeys.SUBJECT_CODE
    >>> assignments_key = DataKeys.ASSIGNMENTS

Integration:
    These enums integrate with:
    - Domain Models: Type validation and categorization
    - Repository Layer: JSON field name standardization
    - Controller Layer: Business logic with type-safe constants
    - View Layer: Display formatting and user interface labels
    - Service Layer: Analytics calculations and data processing

Example:
    >>> from model.enums import GradeType, SemesterName, DataKeys
    >>> from model import Assignment
    >>>
    >>> # Type-safe assignment creation
    >>> assignment = Assignment(
    ...     name="Quiz 1",
    ...     weighted_mark=8.5,
    ...     mark_weight=10.0,
    ...     grade_type=GradeType.QUIZ  # Type-safe enum usage
    ... )
    >>>
    >>> # Semester data organization
    >>> semester = SemesterName.SESSION_1
    >>> data_key = DataKeys.SUBJECT_CODE
    >>>
    >>> # Enum comparison and validation
    >>> if assignment.grade_type == GradeType.QUIZ:
    ...     print("This is a quiz assessment")
"""

from .data_keys import DataKeys
from .grade_types import GradeType
from .semester_names import SemesterName

__all__ = [
    # Assessment categories and types
    "GradeType",  # Standardized assessment categories (assignment, quiz, project, etc.)
    # Academic period definitions
    "SemesterName",  # Standardized semester naming conventions (Session 1, Session 2, etc.)
    # Data structure constants
    "DataKeys",  # JSON field names and data access constants
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Enumeration definitions for controlled vocabularies and constants"

# Enumeration capabilities
_ENUM_FEATURES = {
    "type_safety": "Compile-time checking for enum values",
    "data_consistency": "Prevents invalid values through controlled vocabularies",
    "standardization": "Consistent naming and categorization across application",
    "documentation": "Self-documenting code through descriptive enum names",
    "maintenance": "Centralized constant and vocabulary management",
}

# Enum categories and purposes
_ENUM_CATEGORIES = {
    "GradeType": {
        "purpose": "Assessment categorization and type classification",
        "values": "assignment, quiz, project, midterm, final, presentation",
        "usage": "Domain model validation and business logic",
    },
    "SemesterName": {
        "purpose": "Academic period standardization and identification",
        "values": "Session 1, Session 2, Summer Session, Winter Session",
        "usage": "Data organization and semester-based operations",
    },
    "DataKeys": {
        "purpose": "JSON field names and data structure constants",
        "values": "subject_code, subject_name, assignments, examination",
        "usage": "Repository layer and data persistence operations",
    },
}

# Integration benefits
_INTEGRATION_BENEFITS = {
    "domain_models": "Type validation and business rule enforcement",
    "repository_layer": "Consistent JSON field naming and structure",
    "controller_layer": "Type-safe business logic with clear constants",
    "view_layer": "Standardized display labels and formatting",
    "service_layer": "Analytics and calculations with validated categories",
}
