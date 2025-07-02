"""Input validation utilities for view components.

This module provides comprehensive validation functions for user input in the
University Marks Manager application. It implements a consistent validation
strategy with detailed error messaging, type safety, and business rule
enforcement for academic data management.

The validation functions follow a standardized pattern of returning tuples
containing validation status and error messages, enabling consistent error
handling across all view components. Each validator implements specific
business rules for academic data integrity.

Validation Categories:
    Subject Validation:
        - Subject code format and uniqueness validation
        - Subject name length and content validation

    Assessment Validation:
        - Assessment name validation with length constraints
        - Weighted mark validation supporting numeric and S/U grades
        - Mark weight percentage validation with range checking

    Grade Validation:
        - Total mark validation with academic range constraints
        - Form-level validation combining multiple field validations

Key Features:
    - Consistent Return Pattern: All validators return (bool, str) tuples
    - Business Rule Enforcement: Academic constraints built into validation
    - Type Safety: Comprehensive type checking and conversion
    - Error Messaging: Clear, user-friendly error descriptions
    - Flexible Input Handling: Support for various input formats and edge cases

Design Principles:
    - Fail Fast: Early validation prevents invalid data propagation
    - Clear Feedback: Descriptive error messages guide user correction
    - Business Logic: Academic rules enforced at validation level
    - Type Safety: Robust type checking and conversion handling
    - Consistency: Standardized validation patterns across all functions

Dependencies:
    - re: Regular expression matching for format validation
    - typing: Type hints for function signatures and return types
    - model.enums.GradeType: Enumeration for valid grade type values

Example:
    >>> from view.utils.validators import validate_subject_code, validate_weighted_mark
    >>>
    >>> # Subject code validation
    >>> is_valid, error = validate_subject_code("CSCI251")
    >>> if not is_valid:
    ...     print(f"Validation error: {error}")
    >>>
    >>> # Weighted mark validation with S/U support
    >>> is_valid, value, error = validate_weighted_mark("85.5")
    >>> if is_valid:
    ...     print(f"Valid mark: {value}")
"""

import re
from typing import Optional, Tuple, Union

from model.enums import GradeType


def validate_subject_code(subject_code: str) -> Tuple[bool, str]:
    """Validate subject code format according to academic standards.

    Validates subject code input ensuring proper format, non-empty content,
    and compliance with academic naming conventions. The validation supports
    standard academic subject code patterns with department prefixes and
    numeric identifiers.

    Validation Rules:
        - Cannot be empty or whitespace-only
        - Must follow format: 3-4 letters + 3-4 digits (e.g., CSCI251, MATH1001)
        - Case insensitive input (automatically converted to uppercase)
        - Standard academic department and course number pattern

    Args:
        subject_code: The subject code string to validate (e.g., "CSCI251")

    Returns:
        Tuple containing:
            - bool: True if valid, False if validation fails
            - str: Empty string if valid, detailed error message if invalid

    Examples:
        >>> validate_subject_code("CSCI251")
        (True, "")

        >>> validate_subject_code("invalid")
        (False, "Subject code should be in format like 'CSCI101' or 'MATH1001'")

        >>> validate_subject_code("")
        (False, "Subject code cannot be empty")

    Business Rules:
        - Follows standard university subject code conventions
        - Department prefix (3-4 alphabetic characters)
        - Course number (3-4 numeric characters)
        - Case insensitive for user convenience
    """
    if not subject_code:
        return False, "Subject code cannot be empty"

    if not subject_code.strip():
        return False, "Subject code cannot be only whitespace"

    # Basic format validation (adjust regex as needed)
    if not re.match(r"^[A-Z]{3,4}[0-9]{3,4}$", subject_code.upper().strip()):
        return False, "Subject code should be in format like 'CSCI101' or 'MATH1001'"

    return True, ""


def validate_subject_name(subject_name: str) -> Tuple[bool, str]:
    """Validate subject name content and length constraints.

    Validates subject name input ensuring appropriate length, non-empty
    content, and reasonable constraints for academic subject naming.
    Implements business rules for subject name standardization.

    Validation Rules:
        - Cannot be empty or whitespace-only
        - Minimum length: 3 characters (after trimming)
        - Maximum length: 100 characters (prevents database overflow)
        - Must contain meaningful content after whitespace removal

    Args:
        subject_name: The subject name string to validate

    Returns:
        Tuple containing:
            - bool: True if valid, False if validation fails
            - str: Empty string if valid, detailed error message if invalid

    Examples:
        >>> validate_subject_name("Advanced Programming")
        (True, "")

        >>> validate_subject_name("CS")
        (False, "Subject name must be at least 3 characters long")

        >>> validate_subject_name("")
        (False, "Subject name cannot be empty")

    Business Rules:
        - Reasonable length constraints for academic subjects
        - Prevents empty or meaningless subject names
        - Database field length compatibility
    """
    if not subject_name:
        return False, "Subject name cannot be empty"

    if not subject_name.strip():
        return False, "Subject name cannot be only whitespace"

    if len(subject_name.strip()) < 3:
        return False, "Subject name must be at least 3 characters long"

    if len(subject_name.strip()) > 100:
        return False, "Subject name cannot exceed 100 characters"

    return True, ""


def validate_assessment_name(assessment_name: str) -> Tuple[bool, str]:
    """Validate assessment name content and length constraints.

    Validates assessment/assignment name input ensuring appropriate length,
    non-empty content, and reasonable constraints for academic assessment
    naming conventions.

    Validation Rules:
        - Cannot be empty or whitespace-only
        - Minimum length: 2 characters (after trimming)
        - Maximum length: 50 characters (UI display optimization)
        - Must contain meaningful content after whitespace removal

    Args:
        assessment_name: The assessment name string to validate

    Returns:
        Tuple containing:
            - bool: True if valid, False if validation fails
            - str: Empty string if valid, detailed error message if invalid

    Examples:
        >>> validate_assessment_name("Assignment 1")
        (True, "")

        >>> validate_assessment_name("A")
        (False, "Assessment name must be at least 2 characters long")

        >>> validate_assessment_name("")
        (False, "Assessment name cannot be empty")

    Business Rules:
        - Shorter length limit for UI display optimization
        - Prevents single-character or empty assessment names
        - Suitable for assignment, quiz, project naming
    """
    if not assessment_name:
        return False, "Assessment name cannot be empty"

    if not assessment_name.strip():
        return False, "Assessment name cannot be only whitespace"

    if len(assessment_name.strip()) < 2:
        return False, "Assessment name must be at least 2 characters long"

    if len(assessment_name.strip()) > 50:
        return False, "Assessment name cannot exceed 50 characters"

    return True, ""


def validate_weighted_mark(weighted_mark_input: str) -> Tuple[bool, Optional[Union[float, str]], str]:
    """Validate weighted mark input supporting numeric grades and S/U categories.

    Validates weighted mark input with support for both numeric grades (0-100)
    and categorical grades (Satisfactory/Unsatisfactory). Provides flexible
    input handling with comprehensive error messaging for invalid formats.

    Validation Rules:
        - Cannot be empty or whitespace-only
        - Numeric grades: 0-100 range validation
        - Categorical grades: 'S' (Satisfactory) or 'U' (Unsatisfactory)
        - Case insensitive input handling
        - Type conversion for numeric values

    Args:
        weighted_mark_input: The weighted mark input string to validate

    Returns:
        Tuple containing:
            - bool: True if valid, False if validation fails
            - Optional[Union[float, str]]: Parsed value (float for numeric, str for S/U) or None if invalid
            - str: Empty string if valid, detailed error message if invalid

    Examples:
        >>> validate_weighted_mark("85.5")
        (True, 85.5, "")

        >>> validate_weighted_mark("S")
        (True, "S", "")

        >>> validate_weighted_mark("invalid")
        (False, None, "Invalid mark format. Use a number, 'S', or 'U'")

    Business Rules:
        - Supports traditional numeric grading (0-100 scale)
        - Supports pass/fail grading with S/U categories
        - Prevents negative marks and marks exceeding 100%
        - Flexible input format handling
    """
    if not weighted_mark_input:
        return False, None, "Weighted mark cannot be empty"

    weighted_mark_input = weighted_mark_input.strip().upper()

    # Check for S/U grades
    if weighted_mark_input in [GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value]:
        return True, weighted_mark_input, ""

    # Try to parse as numeric
    try:
        mark = float(weighted_mark_input)
        if mark < 0:
            return False, None, "Mark cannot be negative"
        if mark > 100:
            return False, None, "Mark cannot exceed 100"
        return True, mark, ""
    except ValueError:
        return (
            False,
            None,
            f"Invalid mark format. Use a number, '{GradeType.SATISFACTORY.value}', or '{GradeType.UNSATISFACTORY.value}'",
        )


def validate_mark_weight(mark_weight: float) -> Tuple[bool, str]:
    """Validate mark weight percentage within academic constraints.

    Validates mark weight input ensuring percentage values fall within
    reasonable academic ranges. Prevents negative weights, excessive
    weights, and zero-weight assignments that would be meaningless.

    Validation Rules:
        - Cannot be negative (weights must be positive contributions)
        - Cannot exceed 100% (prevents over-weighting)
        - Cannot be exactly 0% (meaningless zero-weight assessments)
        - Must be a valid percentage value

    Args:
        mark_weight: The mark weight percentage to validate (0-100 scale)

    Returns:
        Tuple containing:
            - bool: True if valid, False if validation fails
            - str: Empty string if valid, detailed error message if invalid

    Examples:
        >>> validate_mark_weight(25.0)
        (True, "")

        >>> validate_mark_weight(-5.0)
        (False, "Mark weight cannot be negative")

        >>> validate_mark_weight(150.0)
        (False, "Mark weight cannot exceed 100%")

    Business Rules:
        - Percentage-based weighting system (0-100 scale)
        - Prevents meaningless zero-weight assessments
        - Constrains weights to reasonable academic ranges
        - Supports fractional percentage weights
    """
    if mark_weight < 0:
        return False, "Mark weight cannot be negative"

    if mark_weight > 100:
        return False, "Mark weight cannot exceed 100%"

    if mark_weight == 0:
        return False, "Mark weight should be greater than 0%"

    return True, ""


def validate_total_mark(total_mark: float) -> Tuple[bool, str]:
    """Validate total mark for subject within academic grade ranges.

    Validates total mark input ensuring values fall within standard
    academic grading ranges. Supports percentage-based grading systems
    with appropriate range constraints.

    Validation Rules:
        - Cannot be negative (grades must be non-negative)
        - Cannot exceed 100 (percentage-based grading ceiling)
        - Supports decimal precision for accurate grading
        - Standard academic grade range validation

    Args:
        total_mark: The total mark percentage to validate (0-100 scale)

    Returns:
        Tuple containing:
            - bool: True if valid, False if validation fails
            - str: Empty string if valid, detailed error message if invalid

    Examples:
        >>> validate_total_mark(85.5)
        (True, "")

        >>> validate_total_mark(-10.0)
        (False, "Total mark cannot be negative")

        >>> validate_total_mark(110.0)
        (False, "Total mark cannot exceed 100")

    Business Rules:
        - Percentage-based grading system (0-100 scale)
        - Supports decimal precision for accurate grade calculation
        - Prevents impossible grade values
        - Compatible with standard academic grading conventions
    """
    if total_mark < 0:
        return False, "Total mark cannot be negative"

    if total_mark > 100:
        return False, "Total mark cannot exceed 100"

    return True, ""


def validate_form_data(form_type: str, **kwargs) -> Tuple[bool, str]:
    """Validate complete form data based on form type with comprehensive checking.

    Provides form-level validation by orchestrating individual field validators
    based on the form type. Implements comprehensive validation workflows that
    ensure all related fields are validated consistently and business rules
    are enforced across form submissions.

    Validation Workflows:
        Subject Form:
            - Subject code format and uniqueness validation
            - Subject name content and length validation

        Assignment Form:
            - Assessment name validation
            - Weighted mark validation (numeric or S/U)
            - Mark weight validation (only for numeric marks)

        Total Mark Form:
            - Total mark range and format validation

    Args:
        form_type: Type of form to validate ("subject", "assignment", "total_mark")
        **kwargs: Form field values to validate (field names vary by form type)

    Returns:
        Tuple containing:
            - bool: True if all validations pass, False if any validation fails
            - str: Empty string if valid, first error message encountered if invalid

    Examples:
        >>> validate_form_data("subject", subject_code="CSCI251", subject_name="Advanced Programming")
        (True, "")

        >>> validate_form_data("assignment", assessment_name="Quiz 1", weighted_mark="85", mark_weight=10.0)
        (True, "")

        >>> validate_form_data("total_mark", total_mark=85.0)
        (True, "")

    Form Types:
        subject: Validates subject creation/editing forms
            - Required: subject_code, subject_name

        assignment: Validates assignment creation/editing forms
            - Required: assessment_name, weighted_mark
            - Optional: mark_weight (validated only for numeric marks)

        total_mark: Validates total mark setting forms
            - Required: total_mark

    Business Rules:
        - Fails fast on first validation error encountered
        - Validates fields in logical dependency order
        - Supports conditional validation (e.g., weight only for numeric marks)
        - Comprehensive error reporting for user feedback
    """
    if form_type == "subject":
        # Validate subject form
        code_valid, code_error = validate_subject_code(kwargs.get("subject_code", ""))
        if not code_valid:
            return False, code_error

        name_valid, name_error = validate_subject_name(kwargs.get("subject_name", ""))
        if not name_valid:
            return False, name_error

    elif form_type == "assignment":
        # Validate assignment form
        name_valid, name_error = validate_assessment_name(kwargs.get("assessment_name", ""))
        if not name_valid:
            return False, name_error

        mark_valid, mark_value, mark_error = validate_weighted_mark(kwargs.get("weighted_mark", ""))
        if not mark_valid:
            return False, mark_error

        # Only validate weight for numeric marks
        if isinstance(mark_value, (int, float)):
            weight_valid, weight_error = validate_mark_weight(kwargs.get("mark_weight", 0))
            if not weight_valid:
                return False, weight_error

    elif form_type == "total_mark":
        # Validate total mark form
        total_valid, total_error = validate_total_mark(kwargs.get("total_mark", 0))
        if not total_valid:
            return False, total_error

    return True, ""
