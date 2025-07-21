# config/settings.py
from pathlib import Path

from domain import GradeType


class Settings:
    """Application configuration."""

    DATA_DIR = Path("data")
    SUPPORTED_YEARS = range(2020, 2030)
    DEFAULT_EXAM_WEIGHT = 100.0
    JSON_INDENT = 4


# config/constants.py


class UIConstants:
    """UI-related constants."""

    PAGE_TITLE = "University Marks Manager"
    PAGE_ICON = "📚"


class ValidationConstants:
    """Validation constants."""

    MIN_MARK = 0.0
    MAX_MARK = 100.0
    VALID_GRADE_TYPES = [GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value]
