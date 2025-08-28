"""Model layer package for the University Marks Manager.

This package provides the complete data model layer for the University Marks Manager
application, including domain entities, data persistence, type definitions, and
enumerations. It follows Domain-Driven Design principles with clear separation
between entities, repositories, and supporting types.

Package Structure:
    Domain Models:
        - Core business entities representing academic concepts
        - Rich domain objects with behavior and validation
        - Relationships between academic entities

    Data Access:
        - Repository pattern for data persistence
        - JSON-based storage with type safety
        - CRUD operations for academic data management

    Type System:
        - TypedDict definitions for JSON data structures
        - Static type checking for data interchange
        - Runtime compatibility with regular dictionaries

    Enumerations:
        - Grade types and assessment categories
        - Semester naming conventions
        - Data access keys and constants

Architecture:
    The model layer implements a clean architecture pattern:

    Domain Layer (Core):
        ├── Subject: Complete subject with assignments and exams
        ├── Assignment: Individual assessments with marks and weights
        ├── Examination: Exam data with marks and weights
        └── Semester: Collection of subjects for a session

    Repository Layer (Data Access):
        └── DataPersistence: JSON storage and retrieval operations

    Type Layer (Contracts):
        ├── SubjectDict: JSON structure for subject data
        ├── AssignmentDict: JSON structure for assignment data
        └── SemesterDict: JSON structure for semester data

    Enum Layer (Constants):
        ├── GradeType: Assessment categories (assignment, quiz, project, etc.)
        ├── SemesterName: Standardized semester naming
        └── DataKeys: JSON field names and data access constants

Usage Patterns:
    >>> from model import Subject, Assignment, DataPersistence
    >>>
    >>> # Create domain entities
    >>> assignment = Assignment("Assignment 1", 15.0, 20.0, "assignment")
    >>> subject = Subject("CSCI251", "Advanced Programming")
    >>> subject.add_assignment(assignment)
    >>>
    >>> # Persist data
    >>> persistence = DataPersistence()
    >>> persistence.save_subject_data("2024 Session 1", subject)

Design Principles:
    - Domain-Driven Design: Rich domain models with business logic
    - Repository Pattern: Clean separation of data access concerns
    - Type Safety: Comprehensive type definitions for data interchange
    - Immutability: Value objects where appropriate
    - Validation: Business rule enforcement at the domain level

Integration:
    The model layer integrates with:
    - Controller Layer: Business logic orchestration and user interactions
    - Service Layer: Calculations, analytics, and business operations
    - View Layer: Data presentation and user interface binding
    - Storage Layer: File system JSON persistence and data management

Example:
    >>> from model import Subject, Assignment, GradeType, DataPersistence
    >>> from model.types import SubjectDict
    >>>
    >>> # Domain model usage
    >>> subject = Subject("CSCI251", "Advanced Programming")
    >>> assignment = Assignment("Quiz 1", 8.5, 10.0, GradeType.QUIZ)
    >>> subject.add_assignment(assignment)
    >>>
    >>> # Type-safe data handling
    >>> subject_data: SubjectDict = subject.to_dict()
    >>>
    >>> # Data persistence
    >>> persistence = DataPersistence()
    >>> persistence.save_data("2024 Session 1", {"CSCI251": subject_data})
"""

from .domain import Assignment, Examination, Semester, Subject
from .enums import DataKeys, GradeType, SemesterName
from .repositories import DataPersistenceSQLite as DataPersistence  # Prefer SQLite backend
from .repositories.sqlite_persistence import PersistenceProtocol  # re-export protocol
from .services import AnalyticsService, GradeCalculationService, PerformanceMetricsService
from .types import AssignmentDict, SemesterDict, SubjectDict

__all__ = [
    # Domain models - Core business entities
    "Semester",  # Collection of subjects for an academic session
    "Assignment",  # Individual assessment with marks and metadata
    "Examination",  # Exam data with marks and weight information
    "Subject",  # Complete subject with assignments and exams
    # Data access - Repository pattern implementation
    "DataPersistence",  # SQLite storage and retrieval operations (aliased)
    "PersistenceProtocol",  # protocol for duck-typed persistence
    # Enums - Constants and controlled vocabularies
    "GradeType",  # Assessment categories (assignment, quiz, project)
    "SemesterName",  # Standardized semester naming conventions
    "DataKeys",  # JSON field names and data access constants
    # Types - TypedDict definitions for data structures
    "AssignmentDict",  # JSON structure for assignment data
    "SubjectDict",  # JSON structure for subject data
    "SemesterDict",  # JSON structure for semester data
    # Services - Business logic and analytics operations
    "AnalyticsService",  # Analytics and performance calculations
    "GradeCalculationService",  # Grade calculations and statistics
    "PerformanceMetricsService",  # Performance metrics and analysis
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Model layer for academic data management and persistence"

# Model layer capabilities
_MODEL_FEATURES = {
    "domain_entities": ["Subject", "Assignment", "Examination", "Semester"],
    "data_persistence": ["JSON storage", "Repository pattern", "CRUD operations"],
    "type_safety": ["TypedDict definitions", "Static type checking", "Runtime compatibility"],
    "enumerations": ["Grade types", "Semester names", "Data keys"],
}

# Data integrity and validation features
_VALIDATION_FEATURES = {
    "business_rules": "Domain entities enforce academic business rules",
    "type_checking": "Comprehensive type hints and validation",
    "data_consistency": "Referential integrity between related entities",
    "format_validation": "JSON schema compliance and structure validation",
}
