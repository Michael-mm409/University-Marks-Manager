"""Type definitions package for the University Marks Manager model layer.

This package provides TypedDict definitions for JSON data structures used throughout
the University Marks Manager application. These types enable static type checking
and IDE support while maintaining runtime compatibility with regular Python dictionaries.

The type system follows the hierarchical structure of academic data:
    RawDataDict (root) → SemesterDict → SubjectDict → AssignmentDict/ExaminationDict

Purpose:
    - Static type checking for JSON data manipulation
    - IDE autocomplete and error detection support
    - Documentation through type annotations
    - Runtime compatibility with standard dictionaries
    - Validation contracts for data interchange

Type Hierarchy:
    RawDataDict: Complete dataset mapping semesters to subjects
    ├── SemesterDict: Maps subject codes to subject data
    │   └── SubjectDict: Complete subject with assignments and exams
    │       ├── AssignmentDict: Individual assignment/assessment data
    │       └── ExaminationDict: Exam marks and weight information

Key Features:
    - Comprehensive type coverage for all JSON structures
    - Optional fields using total=False for partial data loading
    - Union types for flexible data handling during JSON parsing
    - Clear documentation with examples and usage patterns
    - Type aliases for common usage scenarios

Integration:
    These types integrate with:
    - Domain models: Conversion to/from business entities
    - Repository layer: JSON serialization and deserialization
    - Controller layer: Data validation and type safety
    - Service layer: Analytics calculations and data processing

Example:
    >>> from model.types import SubjectDict, AssignmentDict
    >>>
    >>> # Type-safe assignment creation
    >>> assignment: AssignmentDict = {
    ...     "subject_assessment": "Assignment 1",
    ...     "weighted_mark": 14.5,
    ...     "mark_weight": 15.0,
    ...     "grade_type": "assignment"
    ... }
    >>>
    >>> # Type-safe subject data handling
    >>> subject: SubjectDict = {
    ...     "subject_code": "CSCI251",
    ...     "subject_name": "Advanced Programming",
    ...     "assignments": [assignment],
    ...     "sync_subject": True
    ... }

Design Benefits:
    - Type Safety: Catch errors at development time rather than runtime
    - IDE Support: Enhanced autocomplete and refactoring capabilities
    - Documentation: Self-documenting code through type annotations
    - Maintainability: Clear contracts for data structure evolution
    - Compatibility: Works with existing JSON-based persistence layer
"""

from .json_types import (
    AssignmentDict,  # Individual assignment/assessment data structure
    ExaminationDict,  # Exam marks and weight information
    RawDataDict,  # Complete dataset root structure
    SemesterDict,  # Semester-level subject mapping
    SubjectDict,  # Complete subject data structure
)

__all__ = [
    # Core data structure types - ordered by hierarchy
    "RawDataDict",  # Root: Complete dataset (semesters → subjects)
    "SemesterDict",  # Level 1: Maps subject codes to subject data
    "SubjectDict",  # Level 2: Complete subject with assignments/exams
    "AssignmentDict",  # Level 3a: Individual assignment data
    "ExaminationDict",  # Level 3b: Exam data and weights
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "TypedDict definitions for JSON data structures"

# Type system capabilities
_TYPE_FEATURES = {
    "static_checking": "Full TypedDict coverage for all JSON structures",
    "ide_support": "Enhanced autocomplete and error detection",
    "runtime_compatibility": "Works with standard Python dictionaries",
    "flexible_parsing": "Union types and optional fields for JSON loading",
    "hierarchical_design": "Mirrors academic data structure organization",
}

# Data structure characteristics
_STRUCTURE_INFO = {
    "hierarchy_levels": 4,  # RawData → Semester → Subject → Assignment/Exam
    "optional_fields": "Supports partial data during loading with total=False",
    "union_types": "Flexible field types for JSON parsing compatibility",
    "type_aliases": "Common usage patterns with descriptive names",
}

# Usage recommendations
_USAGE_PATTERNS = {
    "import_style": "from model.types import SubjectDict, AssignmentDict",
    "type_annotations": "Use for function parameters and return types",
    "data_validation": "Leverage for JSON schema validation",
    "conversion": "Bridge between JSON data and domain models",
}
