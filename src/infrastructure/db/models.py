"""SQLModel ORM models (infrastructure layer)."""
from __future__ import annotations

from enum import Enum
from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel


class GradeType(str, Enum):
    """Supported grading modes for an assessment component."""

    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"


class Semester(SQLModel, table=True):
    """Academic semester (e.g., Autumn 2025)."""

    __tablename__: ClassVar[str] = "semesters"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: str = Field(index=True)


class Subject(SQLModel, table=True):
    """Subject/course within a semester/year."""

    __tablename__: ClassVar[str] = "subjects"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    subject_name: str
    semester_name: str = Field(index=True)
    year: str = Field(index=True)
    total_mark: float = 0
    sync_subject: bool = False


class Assignment(SQLModel, table=True):
    """Assessment item belonging to a subject (numeric or S/U)."""

    __tablename__: ClassVar[str] = "assignments"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_name: str = Field(index=True)
    year: str = Field(index=True)
    assessment: str
    weighted_mark: Optional[str] = None  # numeric stored as text or S/U
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str = Field(default=GradeType.NUMERIC.value)


class Examination(SQLModel, table=True):
    """Single exam record per subject."""

    __tablename__: ClassVar[str] = "examinations"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_name: str = Field(index=True)
    year: str = Field(index=True)
    exam_mark: float = 0
    exam_weight: float = 100


class ExamSettings(SQLModel, table=True):
    """
    Stores pass-scale (PS) exam configuration separately to avoid altering existing tables.

    This allows persisting ps_exam flag and ps_factor without a migration altering the Examination table already present in user data.
    """

    __tablename__: ClassVar[str] = "exam_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_name: str = Field(index=True)
    year: str = Field(index=True)
    ps_exam: bool = False
    ps_factor: float = 40.0


__all__ = [
	"GradeType",
	"Semester",
	"Subject",
	"Assignment",
	"Examination",
    "ExamSettings",
]

