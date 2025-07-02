"""
Data formatting utilities for views.

This module provides helper functions for safely handling and converting
assignment mark values — especially for mixed grading schemes involving
both numeric scores and non-numeric grades like Satisfactory/Unsatisfactory.

Functions:
    - safe_float: Converts a value to float or returns None for S/U grades.
    - safe_display_value: Converts a value to a string suitable for UI display.

Dependencies:
    - GradeType (Enum defining SATISFACTORY and UNSATISFACTORY values)
"""

from typing import Optional

from model.enums import GradeType


def safe_float(val) -> Optional[float]:
    """
    Safely converts a value to a float, or returns None if it's a non-numeric grade.

    This function supports systems that use both numeric and symbolic grading (e.g., 'S', 'U').
    If the input is 'S' or 'U' (case-insensitive), the function returns None to signal that
    numeric operations should not be performed on the value.

    Args:
        val: The input value (str, int, float, or any).

    Returns:
        Optional[float]: The float value if conversion is successful, otherwise None.
    """
    if isinstance(val, str) and val.strip().upper() in {GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value}:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_display_value(val) -> str:
    """
    Converts a value to a clean string for display in the UI.

    Handles both numeric values and symbolic grades. If the input is 'S' or 'U',
    the function returns it in uppercase. For numeric inputs, the value is formatted
    as a float string. Returns an empty string if conversion fails.

    Args:
        val: The input value (str, int, float, or any).

    Returns:
        str: A display-safe string representation of the value.
    """
    if isinstance(val, str) and val.upper() in {GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value}:
        return val.upper()
    try:
        return str(float(val))
    except (ValueError, TypeError):
        return ""
