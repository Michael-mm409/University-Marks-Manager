"""Domain entities subpackage for core business objects.

This subpackage provides the fundamental domain entities that represent the core
business concepts in academic data management. These entities implement rich
domain models with encapsulated behavior, validation, and business logic
following Domain-Driven Design principles.

Entity Types:
    The entities package contains three primary domain objects:

    Core Entities:
        - Subject: Academic course entity with assignment collections

    Value Objects:
        - Assignment: Individual assessment with marks and metadata
        - Examination: Exam data with weight and mark information

Entity Characteristics:
    Subject (Entity):
        - Identity: Unique subject code and name
        - Lifecycle: Managed creation, modification, and persistence
        - Behavior: Assignment management, grade calculations, analytics
        - State: Mutable with business rule enforcement
        - Relationships: Contains assignments and optional examination

    Assignment (Value Object):
        - Identity: Based on content equality, not reference
        - Lifecycle: Immutable once created
        - Behavior: Mark validation, percentage calculation
        - State: Immutable data with encapsulated validation
        - Purpose: Represents individual assessments and evaluations

    Examination (Value Object):
        - Identity: Based on content equality
        - Lifecycle: Immutable exam data
        - Behavior: Weight validation, mark calculation
        - State: Immutable with business rule enforcement
        - Purpose: Represents final exam component of subject assessment

Design Principles:
    - Entity vs Value Object: Clear distinction based on identity requirements
    - Encapsulation: Business logic contained within appropriate entities
    - Immutability: Value objects prevent accidental state changes
    - Validation: Business rules enforced at creation and modification
    - Rich Behavior: Entities provide domain-specific operations

Business Logic:
    Each entity encapsulates relevant business rules:

    Subject Business Rules:
        - Subject codes must be unique and properly formatted
        - Assignment collections maintain referential integrity
        - Grade calculations follow academic weighting standards
        - Total marks and weights are validated for consistency

    Assignment Business Rules:
        - Marks cannot exceed maximum possible values
        - Weights must be valid percentage values (0-100)
        - Grade types must be from predefined categories
        - Names must be unique within subject scope

    Examination Business Rules:
        - Exam marks validated against standard academic ranges
        - Weights integrated with overall subject assessment
        - Optional component with proper default handling
        - Validation ensures academic integrity standards

Usage Patterns:
    >>> from model.domain.entities import Subject, Assignment, Examination
    >>>
    >>> # Entity creation with validation
    >>> subject = Subject("CSCI251", "Advanced Programming")
    >>> assignment = Assignment("Assignment 1", 18.5, 20.0, "assignment")
    >>> exam = Examination(75.0, 50.0)
    >>>
    >>> # Entity relationships and behavior
    >>> subject.add_assignment(assignment)
    >>> subject.examination = exam
    >>> total_mark = subject.calculate_total_mark()

Integration:
    These entities integrate with:
    - Domain Layer: Core business object implementations
    - Repository Layer: Persistence and data conversion operations
    - Service Layer: Complex business operations and calculations
    - Controller Layer: User action processing and workflow management
    - Type System: JSON serialization and deserialization support

Value Object Benefits:
    - Immutability: Prevents accidental modification of assessment data
    - Equality: Content-based comparison for proper domain behavior
    - Validation: Business rules enforced at creation time
    - Simplicity: Clear, focused responsibility without identity concerns
    - Performance: Efficient comparison and hashing operations

Entity Benefits:
    - Identity: Unique identification for proper lifecycle management
    - Behavior: Rich domain operations for business logic
    - State Management: Controlled mutation with validation
    - Relationships: Complex associations with other domain objects
    - Persistence: Clear mapping to storage representations

Example:
    >>> from model.domain.entities import Subject, Assignment, Examination
    >>> from model.enums import GradeType
    >>>
    >>> # Rich domain model construction
    >>> subject = Subject("CSCI251", "Advanced Programming")
    >>> subject.total_mark = 85.0  # Target grade
    >>>
    >>> # Value objects with business validation
    >>> quiz = Assignment("Quiz 1", 8.5, 10.0, GradeType.QUIZ)
    >>> assignment = Assignment("Major Project", 45.0, 50.0, GradeType.PROJECT)
    >>> exam = Examination(68.0, 40.0)
    >>>
    >>> # Entity behavior and relationships
    >>> subject.add_assignment(quiz)
    >>> subject.add_assignment(assignment)
    >>> subject.examination = exam
    >>>
    >>> # Domain-driven calculations
    >>> assignment_total = subject.calculate_assignment_total()
    >>> final_mark = subject.calculate_final_mark()
    >>> progress = subject.calculate_progress_percentage()
    >>>
    >>> # Business rule validation
    >>> if subject.is_passing_grade():
    ...     print(f"Subject {subject.subject_code} meets passing requirements")
"""

from .assignment import Assignment
from .examination import Examination
from .subject import Subject

__all__ = [
    # Core entity - academic course with rich behavior
    "Subject",  # Academic subject/course entity with assignment management
    # Value objects - immutable assessment data
    "Assignment",  # Individual assessment with marks, weights, and validation
    "Examination",  # Exam component with marks and weight integration
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Core domain entities for academic business object modeling"

# Entity characteristics summary
_ENTITY_TYPES = {
    "Subject": {
        "pattern": "Entity",
        "identity": "Subject code uniquely identifies instance",
        "mutability": "Mutable with controlled state changes",
        "relationships": "Contains assignments and optional examination",
        "behavior": "Assignment management, calculations, analytics",
    },
    "Assignment": {
        "pattern": "Value Object",
        "identity": "Content-based equality, no unique identity",
        "mutability": "Immutable once created",
        "relationships": "Belongs to subject, independent lifecycle",
        "behavior": "Mark validation, percentage calculations",
    },
    "Examination": {
        "pattern": "Value Object",
        "identity": "Content-based equality for exam data",
        "mutability": "Immutable exam assessment data",
        "relationships": "Optional component of subject assessment",
        "behavior": "Weight validation, mark integration",
    },
}

# Business rules enforced by entities
_BUSINESS_RULES = {
    "validation": "All entities enforce business rules at creation and modification",
    "consistency": "Cross-entity validation ensures data integrity",
    "academic_standards": "Calculations follow academic weighting conventions",
    "data_integrity": "Immutable value objects prevent accidental changes",
}
