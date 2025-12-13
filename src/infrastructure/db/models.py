"""SQLModel ORM models (infrastructure layer)."""
from __future__ import annotations

from enum import Enum
from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship as sa_relationship


class GradeType(str, Enum):
    """Supported grading modes for an assessment component."""

    NUMERIC = "numeric"
    SATISFACTORY = "S"
    UNSATISFACTORY = "U"


class Semester(SQLModel, table=True):
    """Academic semester (e.g., Autumn 2025).
    
    Candidate key: (course_id, name, year) - no duplicate semesters per course
    """

    __tablename__: ClassVar[str] = "semesters"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)
    course_id: Optional[int] = Field(default=None, foreign_key="courses.id")
    # Target uniqueness per UML: one (name, year) per course
    # NOTE: Applying this change requires a DB migration (updates constraint name and keys)
    __table_args__ = (
        UniqueConstraint("course_id", "name", "year", name="uq_semester_course_name_year"),  # Candidate key
    )

    # Relationship is attached after class definitions to avoid forward-ref issues
    # course: "Course" = Relationship(back_populates="semesters")


class Subject(SQLModel, table=True):
    """Subject/course within a semester.
    
    Candidate key: (subject_code, semester_id) - one subject code per semester
    """

    __tablename__: ClassVar[str] = "subjects"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_code: str = Field(index=True)
    semester_id: int = Field(foreign_key="semesters.id", index=True)
    semester_year: int = Field(foreign_key="semesters.year", index=True)
    subject_name: str
    total_mark: Optional[float] = 0.0
    credit_points: int = Field(default=6)
    sync_subject: bool = False

    __table_args__ = (
        # Uniqueness: one subject_code per semester
        UniqueConstraint("subject_code", "semester_id", name="uq_subject_code_semester"),  # Candidate key
    )

    # NOTE:
    # Fully normalized schema via migrations 001-007.
    # semester_name/year denormalization removed in migration 007.


class Course(SQLModel, table=True):
    """Represents a degree or program of study.
    
    Candidate key: code (unique course identifier)
    """

    __tablename__: ClassVar[str] = "courses"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(index=True)
    grading_scale: str = Field(default="Standard")
    __table_args__ = (
        UniqueConstraint("code", name="uq_course_code"),  # Candidate key
    )

    # NOTE: Redundant (name, code) constraint removed via migration 005.

    # Relationships are attached after class definitions to avoid forward-ref issues
    # semesters: list[Semester] = Relationship(back_populates="course")


class Assignment(SQLModel, table=True):
    """Assessment item belonging to a subject (numeric or S/U).
    
    Candidate key: (assessment, subject_id) - unique assessment names per subject
    """

    __tablename__: ClassVar[str] = "assignments"
    id: int = Field(default=None, primary_key=True)
    assessment: str = Field(index=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True)
    # Store numeric weighted marks as floats. Grade type tracks S/U separately.
    weighted_mark: Optional[float] = None
    unweighted_mark: Optional[float] = None
    mark_weight: Optional[float] = None
    grade_type: str = Field(default=GradeType.NUMERIC.value)
    is_exam: bool = Field(default=False)
    __table_args__ = (
        # Ensure one assessment name per subject (fully normalized via migration 007)
        UniqueConstraint("assessment", "subject_id", name="uq_assignment_subject"),  # Candidate key
    )


class Examination(SQLModel, table=True):
    """Single exam record per subject.
    
    Candidate key: subject_id (1:1 relationship with Subject)
    """

    __tablename__: ClassVar[str] = "examinations"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True, unique=True)  # Candidate key
    exam_mark: float = 0
    exam_weight: float = 100


class ExamSettings(SQLModel, table=True):
    """
    Stores pass-scale (PS) exam configuration separately to avoid altering existing tables.

    This allows persisting ps_exam flag and ps_factor without a migration altering the Examination table already present in user data.
    
    Candidate key: subject_id (1:1 relationship with Subject)
    """

    __tablename__: ClassVar[str] = "exam_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subjects.id", index=True, unique=True)  # Candidate key
    ps_exam: bool = False
    ps_factor: float = 40.0


class GradeScale(SQLModel, table=True):
    """
    Configuration for grade bands (e.g. HD, D, C, P, F).
    Allows customizing thresholds and GPA points.
    
    Candidate key: (scale_name, grade, band_type) - unique grade per scale/band combination
    """
    __tablename__: ClassVar[str] = "grade_scales"
    id: Optional[int] = Field(default=None, primary_key=True)
    scale_name: str = Field(default="Standard", index=True)
    grade: str  # e.g. "HD"
    label: str  # e.g. "High Distinction"
    min_mark: float  # e.g. 85.0
    gpa_point: float  # e.g. 4.0
    band_type: str = Field(default="both", index=True, description="wam, gpa, or both")
    __table_args__ = (
        UniqueConstraint("scale_name", "grade", "band_type", name="uq_scale_grade_type"),  # Candidate key
    )


__all__ = [
	"GradeType",
	"Semester",
	"Subject",
	"Assignment",
	"Examination",
    "ExamSettings",
    "Course",
    "GradeScale",
]

# Attach relationships explicitly after all classes are defined to avoid
# SQLAlchemy trying to resolve generic strings like "Optional['Course']" or "list['Semester']".
Semester.course = sa_relationship("Course", back_populates="semesters")
Course.semesters = sa_relationship("Semester", back_populates="course")

# Manually update forward references to resolve circular dependencies
Course.model_rebuild()
Semester.model_rebuild()
Subject.model_rebuild()

