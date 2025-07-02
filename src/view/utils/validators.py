"""Input validation utilities for view components."""

import re
from typing import Optional, Tuple, Union

from model.enums import GradeType


def validate_subject_code(subject_code: str) -> Tuple[bool, str]:
    """
    Validate subject code format.

    Args:
        subject_code: The subject code to validate

    Returns:
        Tuple of (is_valid, error_message)
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
    """
    Validate subject name.

    Args:
        subject_name: The subject name to validate

    Returns:
        Tuple of (is_valid, error_message)
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
    """
    Validate assessment name.

    Args:
        assessment_name: The assessment name to validate

    Returns:
        Tuple of (is_valid, error_message)
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
    """
    Validate weighted mark input (numeric or S/U).

    Args:
        weighted_mark_input: The weighted mark input to validate

    Returns:
        Tuple of (is_valid, parsed_value_or_none, error_message)
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
    """
    Validate mark weight percentage.

    Args:
        mark_weight: The mark weight to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if mark_weight < 0:
        return False, "Mark weight cannot be negative"

    if mark_weight > 100:
        return False, "Mark weight cannot exceed 100%"

    if mark_weight == 0:
        return False, "Mark weight should be greater than 0%"

    return True, ""


def validate_total_mark(total_mark: float) -> Tuple[bool, str]:
    """
    Validate total mark for a subject.

    Args:
        total_mark: The total mark to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if total_mark < 0:
        return False, "Total mark cannot be negative"

    if total_mark > 100:
        return False, "Total mark cannot exceed 100"

    return True, ""


def validate_form_data(form_type: str, **kwargs) -> Tuple[bool, str]:
    """
    Validate complete form data based on form type.

    Args:
        form_type: Type of form ('subject', 'assignment', 'total_mark')
        **kwargs: Form field values to validate

    Returns:
        Tuple of (is_valid, error_message)
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
