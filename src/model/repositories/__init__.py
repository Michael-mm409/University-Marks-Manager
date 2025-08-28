"""Repository layer package for the University Marks Manager model layer.

This package provides the repository pattern implementation for data persistence
in the University Marks Manager application. It abstracts data storage operations
and provides a clean interface between the domain layer and the underlying
JSON-based file storage system.

Repository Pattern:
    The repository pattern encapsulates the logic needed to access data sources.
    It centralizes common data access functionality, providing better maintainability
    and decoupling the infrastructure or technology used to access databases from
    the domain model layer.

Package Structure:
    DataPersistence: Primary repository implementation
    ├── JSON file-based storage and retrieval
    ├── Semester and subject data management
    ├── CRUD operations with type safety
    └── File system abstraction and error handling

Key Features:
    - JSON-based persistence with human-readable data files
    - Type-safe operations using TypedDict definitions
    - Automatic file management and directory structure creation
    - Error handling for file system operations and data corruption
    - Semester-based data organization with subject collections
    - Backup and recovery capabilities for data integrity

Design Principles:
    - Repository Pattern: Clean separation of data access concerns
    - Single Responsibility: Each repository handles one aggregate root
    - Interface Segregation: Simple, focused data access methods
    - Dependency Inversion: Domain layer depends on repository abstractions
    - Error Handling: Graceful degradation and informative error messages

Data Organization:
    The repository organizes academic data in a hierarchical structure:

    Storage Layout:
        data/
        ├── semester_1_data.json    # Semester 1 subjects and assignments
        ├── semester_2_data.json    # Semester 2 subjects and assignments
        └── summer_session_data.json # Summer session data

    JSON Structure:
        {
            "CSCI251": {               # Subject code
                "subject_name": "...",  # Subject metadata
                "assignments": [...],   # Assignment collection
                "examination": {...}    # Exam data (optional)
            }
        }

Usage Patterns:
    >>> from model.repositories import DataPersistence
    >>>
    >>> # Initialize repository
    >>> persistence = DataPersistence()
    >>>
    >>> # Load semester data
    >>> semester_data = persistence.load_data("2024 Session 1")
    >>>
    >>> # Save updated data
    >>> persistence.save_data("2024 Session 1", semester_data)
    >>>
    >>> # Get all available semesters
    >>> semesters = persistence.get_available_semesters()

Integration:
    The repository layer integrates with:
    - Domain Layer: Conversion between entities and JSON structures
    - Controller Layer: Data operations requested by business logic
    - Service Layer: Bulk operations and data analytics processing
    - Type System: TypedDict validation for data integrity

Error Handling:
    The repository provides comprehensive error handling for:
    - File system permissions and access issues
    - JSON parsing and serialization errors
    - Data corruption and validation failures
    - Missing files and directory creation
    - Concurrent access and file locking scenarios

Performance Considerations:
    - Lazy loading: Data loaded only when requested
    - Caching: Recently accessed data kept in memory
    - Batch operations: Multiple changes saved together
    - File size optimization: Efficient JSON serialization
    - Backup strategies: Automatic data backup before modifications

Example:
    >>> from model.repositories import DataPersistence
    >>> from model.types import SubjectDict
    >>>
    >>> # Repository usage with type safety
    >>> persistence = DataPersistence()
    >>>
    >>> # Load with error handling
    >>> try:
    ...     data = persistence.load_data("2024 Session 1")
    ...     subject: SubjectDict = data.get("CSCI251", {})
    ... except FileNotFoundError:
    ...     print("Semester data not found")
    ... except ValueError as e:
    ...     print(f"Data corruption detected: {e}")
    >>>
    >>> # Save with validation
    >>> updated_data = {"CSCI251": subject}
    >>> success = persistence.save_data("2024 Session 1", updated_data)
    >>> if success:
    ...     print("Data saved successfully")
"""

from .data_persistence import DataPersistence
from .sqlite_persistence import DataPersistenceSQLite

__all__ = [
    "DataPersistence",  # JSON-based persistence
    "DataPersistenceSQLite",  # SQLite-based persistence
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Repository pattern implementation for academic data persistence"

# Repository capabilities
_REPOSITORY_FEATURES = {
    "persistence_type": "JSON file-based storage",
    "pattern": "Repository pattern with aggregate root design",
    "type_safety": "TypedDict integration for data validation",
    "error_handling": "Comprehensive file system and data error management",
    "organization": "Semester-based hierarchical data structure",
}

# Storage characteristics
_STORAGE_INFO = {
    "format": "Human-readable JSON files",
    "structure": "Hierarchical: Semester → Subject → Assignment/Exam",
    "location": "Local file system with configurable data directory",
    "backup": "Automatic backup before modifications",
    "concurrent_access": "File locking for safe concurrent operations",
}

# Performance features
_PERFORMANCE_FEATURES = {
    "loading": "Lazy loading with caching for frequently accessed data",
    "saving": "Batch operations to minimize file I/O",
    "validation": "Pre-save validation to prevent corrupted data",
    "optimization": "Efficient JSON serialization with minimal overhead",
}

# Integration points
_INTEGRATION_LAYERS = {
    "domain": "Converts between domain entities and JSON structures",
    "controller": "Handles data requests from business logic layer",
    "service": "Supports analytics and bulk data operations",
    "types": "Uses TypedDict definitions for data validation",
}
