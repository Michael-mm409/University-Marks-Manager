"""Domain entities package for the University Marks Manager model layer.

This package provides the core domain entities that represent the fundamental
business concepts of academic data management. These entities implement the
Domain-Driven Design pattern with rich domain objects that encapsulate both
data and behavior related to academic performance tracking.

Domain Architecture:
    The domain layer implements a hierarchical structure reflecting real-world
    academic organization:

    Semester (Aggregate Root)
    ├── Subject (Entity)
    │   ├── Assignment (Value Object)
    │   ├── Assignment (Value Object)
    │   └── Examination (Value Object)
    └── Subject (Entity)
        └── ...

Core Entities:
    Semester: Aggregate root managing a collection of subjects for an academic period
    ├── Manages subject lifecycle and validation
    ├── Provides semester-wide calculations and analytics
    ├── Handles subject addition, removal, and updates
    └── Enforces business rules for academic sessions

    Subject: Entity representing a single academic subject/course
    ├── Contains assignments and optional examination
    ├── Calculates weighted marks and final grades
    ├── Manages assignment collection and validation
    └── Provides subject-specific analytics and metrics

    Assignment: Value object for individual assessments
    ├── Immutable assessment data with marks and weights
    ├── Grade calculation and percentage conversion
    ├── Type categorization (assignment, quiz, project, etc.)
    └── Validation for mark ranges and weight constraints

    Examination: Value object for exam data
    ├── Exam mark and weight information
    ├── Integration with subject final mark calculations
    ├── Optional component of subject assessment
    └── Validation for exam-specific business rules

Design Principles:
    - Domain-Driven Design: Rich domain models with encapsulated behavior
    - Aggregate Pattern: Clear boundaries and consistency guarantees
    - Value Objects: Immutable objects for data integrity
    - Entity Identity: Unique identification and lifecycle management
    - Business Logic: Domain rules enforced at the entity level

Key Features:
    - Rich Domain Models: Entities contain both data and behavior
    - Business Rule Enforcement: Domain constraints validated automatically
    - Calculation Services: Built-in academic calculations and analytics
    - Type Safety: Comprehensive type hints and validation
    - Immutability: Value objects prevent accidental data modification

Business Rules:
    Academic Constraints:
        - Assignment marks cannot exceed maximum possible marks
        - Subject weights should not exceed 100% when combined
        - Semester must contain at least one subject for calculations
        - Grade types must be from predefined assessment categories

    Data Integrity:
        - Assignment names must be unique within a subject
        - Subject codes must be unique within a semester
        - Marks must be non-negative numeric values
        - Weights must be percentage values (0-100)

Usage Patterns:
    >>> from model.domain import Semester, Subject, Assignment, Examination
    >>>
    >>> # Create domain entities
    >>> semester = Semester("2024 Session 1")
    >>> subject = Subject("CSCI251", "Advanced Programming")
    >>> assignment = Assignment("Assignment 1", 18.5, 20.0, "assignment")
    >>>
    >>> # Build domain relationships
    >>> subject.add_assignment(assignment)
    >>> semester.add_subject(subject)
    >>>
    >>> # Access domain behavior
    >>> total_mark = subject.calculate_total_mark()
    >>> semester_average = semester.calculate_average()

Integration:
    Domain entities integrate with:
    - Repository Layer: Persistence and data loading operations
    - Controller Layer: Business logic orchestration and user actions
    - Service Layer: Complex calculations and analytics processing
    - Type System: TypedDict conversion for JSON persistence
    - View Layer: Data presentation and user interface binding

Performance Considerations:
    - Lazy Calculation: Expensive computations performed on demand
    - Caching: Calculated values cached until data changes
    - Immutable Values: Value objects prevent accidental modifications
    - Efficient Collections: Optimized data structures for assignments
    - Memory Management: Minimal object overhead for large datasets

Example:
    >>> from model.domain import Semester, Subject, Assignment, GradeType
    >>>
    >>> # Domain model construction
    >>> semester = Semester("2024 Session 1")
    >>>
    >>> # Subject with rich behavior
    >>> subject = Subject("CSCI251", "Advanced Programming")
    >>> subject.total_mark = 85.0  # Set target grade
    >>>
    >>> # Value objects with validation
    >>> quiz = Assignment("Quiz 1", 8.5, 10.0, GradeType.QUIZ)
    >>> assignment = Assignment("Assignment 1", 18.0, 20.0, GradeType.ASSIGNMENT)
    >>>
    >>> # Domain operations
    >>> subject.add_assignment(quiz)
    >>> subject.add_assignment(assignment)
    >>> semester.add_subject(subject)
    >>>
    >>> # Business logic through domain
    >>> if subject.calculate_assignment_total() >= 50:
    ...     print("Minimum assignment requirement met")
    >>>
    >>> # Analytics through domain behavior
    >>> progress = subject.calculate_progress_to_target()
    >>> semester_stats = semester.get_performance_statistics()
"""

from .entities import Assignment, Examination, Subject
from .semester import Semester

__all__ = [
    # Aggregate root - manages academic sessions
    "Semester",  # Collection of subjects for an academic period
    # Core entities - fundamental business objects
    "Subject",  # Individual academic subject/course with assignments
    # Value objects - immutable assessment data
    "Assignment",  # Individual assessment with marks and metadata
    "Examination",  # Exam data with marks and weight information
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Domain entities for academic data modeling and business logic"

# Domain capabilities
_DOMAIN_FEATURES = {
    "design_pattern": "Domain-Driven Design with aggregate roots and value objects",
    "business_logic": "Rich domain models with encapsulated academic rules",
    "calculations": "Built-in academic calculations and analytics",
    "validation": "Business rule enforcement at the domain level",
    "type_safety": "Comprehensive type hints and runtime validation",
}

# Entity characteristics
_ENTITY_INFO = {
    "Semester": {
        "type": "Aggregate Root",
        "responsibility": "Academic session management and subject collection",
        "key_behaviors": ["subject_management", "semester_analytics", "validation"],
    },
    "Subject": {
        "type": "Entity",
        "responsibility": "Individual course with assignments and calculations",
        "key_behaviors": ["assignment_management", "grade_calculation", "progress_tracking"],
    },
    "Assignment": {
        "type": "Value Object",
        "responsibility": "Immutable assessment data with validation",
        "key_behaviors": ["mark_validation", "percentage_calculation", "type_categorization"],
    },
    "Examination": {
        "type": "Value Object",
        "responsibility": "Exam data integration with subject calculations",
        "key_behaviors": ["exam_validation", "weight_management", "grade_integration"],
    },
}

# Business rules summary
_BUSINESS_RULES = {
    "academic_constraints": [
        "Assignment marks cannot exceed maximum possible marks",
        "Subject weights should not exceed 100% when combined",
        "Grade types must be from predefined assessment categories",
    ],
    "data_integrity": [
        "Assignment names must be unique within a subject",
        "Subject codes must be unique within a semester",
        "Marks must be non-negative numeric values",
        "Weights must be percentage values (0-100)",
    ],
}
