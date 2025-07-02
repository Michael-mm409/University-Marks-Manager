"""Data formatting utilities for views."""

from typing import Optional

from model.enums import GradeType


def safe_float(val) -> Optional[float]:
    """Safely converts a value to a float, or returns None for 'S'/'U'."""
    if isinstance(val, str) and val.strip().upper() in {GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value}:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_display_value(val) -> str:
    """Safely converts a value to a string for display."""
    if isinstance(val, str) and val.upper() in {GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value}:
        return val.upper()
    try:
        return str(float(val))
    except (ValueError, TypeError):
        return ""
